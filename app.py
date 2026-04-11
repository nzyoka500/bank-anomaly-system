"""
File: app.py
Project: Bank Sentinel - Unusual Bank Deposit Detection System
Target: FinTech / SACCO / Micro-Lending Integration
Description: 
    Production-grade Flask application featuring hybrid AI anomaly detection, 
    Talisman security headers, and automated forensic logging.
    
Author: ERIC NZYOKA
Date: April 2024
"""

import os
import logging
import datetime
import io
import uuid
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_talisman import Talisman
from dotenv import load_dotenv
from model_engine import AnomalyEngine
from werkzeug.middleware.proxy_fix import ProxyFix


# Load environment variables (API keys, Secret keys)
load_dotenv()

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================

app = Flask(__name__)

# ProxyFix is essential for correct client IP logging when behind a reverse proxy (e.g., Nginx, AWS ELB)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# --- A. Database Config ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bank-sentinel-7788-prod-key')

# --- B. Objects Initialization (ORDER MATTERS) ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ml_engine = AnomalyEngine()

# --- C. Production Security (Talisman) ---
# Content Security Policy (Allows Chart.js and FontAwesome CDNs)
csp = {
    'default-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
    'script-src': ['\'self\'', 'https://cdn.jsdelivr.net', '\'unsafe-inline\''],
    'style-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', '\'unsafe-inline\''],
    'font-src': ['\'self\'', 'https://cdnjs.cloudflare.com', 'https://cdn.jsdelivr.net']
}
# Note: Disable 'force_https' if you are testing locally without SSL
Talisman(app, content_security_policy=csp, force_https=False)

# --- D. Logging Setup ---
if not os.path.exists('logs'): os.mkdir('logs')
logging.basicConfig(filename='logs/sentinel.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 2. DATABASE MODELS
# ==========================================

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    # Using UUID for trace_id but named 'id' to match HTML templates
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    is_anomaly = db.Column(db.Boolean, default=False, index=True)
    anomaly_score = db.Column(db.Float, nullable=False)
    reasons = db.Column(db.String(255), nullable=True)
    account_ref = db.Column(db.String(50), nullable=True)

# ==========================================
# 3. AUTHENTICATION MIDDLEWARE
# ==========================================

@app.before_request
def check_auth():
    """Protects all internal routes except for login and public pages."""
    public_endpoints = ['login', 'landing', 'static', 'api_detect']
    if request.endpoint not in public_endpoints and 'user_id' not in session:
        # Check if the path is a static file or the login page itself
        if request.path.startswith('/static') or request.path == '/login':
            return
        return redirect(url_for('login'))

# ==========================================
# 4. CORE API & DETECTION LOGIC
# ==========================================

@app.route('/detect', methods=['POST'])
def ui_detect():
    """Handles detection requests specifically from the Dashboard UI."""
    return process_transaction(request.json, source="UI")

# API Endpoint for external systems (e.g. Spin Mobile) with API Key authentication
@app.route('/api/v1/detect', methods=['POST'])
def api_detect():
    """Automated Endpoint for External Systems (e.g. Spin Mobile). Requires API Key."""
    api_key = request.headers.get('X-API-KEY')
    if api_key != "SENTINEL_PROD_KEY":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    return process_transaction(request.json, source="API")

# Unified processing function for both UI and API requests
def process_transaction(data, source="UI"):
    """Unified logic for both UI and API detection."""
    try:
        amount = float(data.get('amount', 0))
        acc_ref = data.get('account_id', 'WEB-SIM')
        
        # Behavioral Logic
        now = datetime.datetime.now()
        day_ago = now - datetime.timedelta(days=1)
        freq = Transaction.query.filter(Transaction.timestamp >= day_ago).count() + 1
        
        # ML Inference
        result = ml_engine.analyze_transaction(amount, now.hour, now.weekday(), freq)
        
        # Save to Ledger
        new_tx = Transaction(
            amount=amount, is_anomaly=result['is_anomaly'], 
            anomaly_score=result['score'], reasons=result['reasons'],
            account_ref=acc_ref
        )
        db.session.add(new_tx)
        db.session.commit()
        
        return jsonify({
            "status": "Flagged" if result['is_anomaly'] else "Normal",
            "score": result['score'],
            "reasons": result['reasons'],
            "trace_id": new_tx.id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 5. NAVIGATION & REPORTING
# ==========================================

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # In a real app, you would verify request.form['employee_id'] and password
        # For this production-level demo, we set the session and redirect
        session.permanent = True  # Keep the session alive
        session['user_id'] = 'ADMIN-EN'
        logger.info("Admin session initiated for ERIC NZYOKA")
        return redirect(url_for('dashboard'))
    
    # If GET, just show the page
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/reports')
def reports():
    try:
        # 1. Fetch data
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
        
        # 2. Calculate KPI stats for the cards
        total = Transaction.query.count()
        flags = Transaction.query.filter_by(is_anomaly=True).count()
        
        # Prevent division by zero
        rate = round((flags / total * 100), 1) if total > 0 else 0
        
        # 3. Pass everything to the template
        return render_template('reports.html', 
                               transactions=transactions, 
                               total=total, 
                               flags=flags, 
                               rate=rate)
    except Exception as e:
        logger.error(f"Reports Error: {str(e)}")
        return f"Database Error: {str(e)}. Try deleting 'database.db' and restarting.", 500

@app.route('/export_audit')
def export_audit():
    try:
        txs = Transaction.query.all()
        # FIXED: Changed 'for txs in txs' to 'for t in txs' to avoid naming conflict
        data_list = []
        for t in txs:
            data_list.append({
                'ID': t.id,
                'Amount': t.amount,
                'Date': t.timestamp.strftime('%Y-%m-%d %H:%M:%S') if t.timestamp else 'N/A',
                'Score': t.anomaly_score,
                'Status': 'FLAGGED' if t.is_anomaly else 'NORMAL',
                'Reason': t.reasons or 'Consistent Pattern'
            })
        
        df = pd.DataFrame(data_list)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='AuditLog')
        output.seek(0)
        
        return send_file(output, 
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                         as_attachment=True, 
                         download_name=f'Sentinel_Audit_{datetime.date.today()}.xlsx')
    except Exception as e:
        return str(e), 500

# Receipt Download Route
@app.route('/download_receipt/<tx_id>')
def download_receipt(tx_id):
    tx = Transaction.query.get_or_404(tx_id)
    # Simple text-based receipt generator
    receipt_content = f"""
    BANK SENTINEL - SECURITY RECEIPT
    -------------------------------
    Transaction ID: {tx.id}
    Timestamp:      {tx.timestamp}
    Amount:         ${tx.amount:.2f}
    Risk Score:  {tx.anomaly_score:.4f}
    Status:         {'FLAGGED' if tx.is_anomaly else 'CLEARED'}
    Description:   {tx.reasons if tx.reasons else 'Consistent with history'}
    -------------------------------
    Generated by Sentinel AI Engine
    """
    
    buf = io.BytesIO()
    buf.write(receipt_content.encode('utf-8'))
    buf.seek(0)
    
    return send_file(buf, as_attachment=True, 
                     download_name=f"Receipt_{tx.id[:8]}.txt", 
                     mimetype='text/plain')


@app.route('/compliance')
def compliance():
    total = Transaction.query.count()
    flags = Transaction.query.filter_by(is_anomaly=True).count()
    rate = round((flags/total*100), 1) if total > 0 else 0
    return render_template('compliance.html', transactions=Transaction.query.limit(10).all(), rate=rate)

@app.route('/settings')
def settings():
    info = {"last_train": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "total_records": 2000}
    return render_template('settings.html', info=info)

@app.route('/retrain', methods=['POST'])
def retrain():
    ml_engine.train_production_models()
    return jsonify({"message": "Hybrid Engine re-calibrated successfully."})

@app.before_request
def check_auth():
    """Protects internal routes."""
    # List of endpoints that DO NOT require login
    public_endpoints = ['login', 'landing', 'static', 'api_detect']
    
    if request.endpoint in public_endpoints:
        return

    if 'user_id' not in session:
        return redirect(url_for('login'))
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)