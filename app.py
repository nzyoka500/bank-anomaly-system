"""
File: app.py
Project: Bank Sentinel - Hybrid AI Anomaly Detection
Target: FinTech / SACCO / Micro-Lending Integration
Description: 
    Production-optimized gateway for real-time banking security. 
    Implements behavioral fingerprinting via Hybrid Machine Learning.
    
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

# Load environment variables (Security First)
load_dotenv()

# ==========================================
# 1. INITIALIZATION & INFRASTRUCTURE
# ==========================================

app = Flask(__name__)

# Essential for cloud deployments (Nginx/AWS/Heroku)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuration Management
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'database.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bank-sentinel-7788-prod-key')
app.permanent_session_lifetime = datetime.timedelta(hours=2)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ml_engine = AnomalyEngine()

# Production Security (CSP Headers)
csp = {
    'default-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
    'script-src': ['\'self\'', 'https://cdn.jsdelivr.net', '\'unsafe-inline\''],
    'style-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', '\'unsafe-inline\''],
    'font-src': ['\'self\'', 'https://cdnjs.cloudflare.com', 'https://cdn.jsdelivr.net', 'data:']
}
Talisman(app, content_security_policy=csp, force_https=False)

# Enterprise Logging
if not os.path.exists('logs'): os.mkdir('logs')
logging.basicConfig(filename='logs/sentinel.log', level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SENTINEL-API")

# ==========================================
# 2. DATABASE MODELS (Forensic Ledger)
# ==========================================

class Transaction(db.Model):
    __tablename__ = 'transactions'
    # We use 'id' as the column name to match industry standards and your HTML templates
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
    """Enterprise Session Gatekeeper."""
    public_endpoints = ['login', 'landing', 'static', 'api_detect', 'health']
    if request.endpoint not in public_endpoints and 'user_id' not in session:
        return redirect(url_for('login'))

# ==========================================
# 4. CORE API & DETECTION GATEWAY
# ==========================================

@app.route('/api/v1/health')
def health():
    """Liveness probe for DevOps/Monitoring."""
    return jsonify({"status": "healthy", "engine": "active", "timestamp": datetime.datetime.now()}), 200

def ui_detect():
    return process_transaction(request.json, source="UI")

@app.route('/api/v1/detect', methods=['POST'])
def api_detect():
    """Spin Mobile Integration Point."""
    api_key = request.headers.get('X-API-KEY')
    if api_key != os.getenv('API_KEY', 'SENTINEL_PROD_KEY'):
        return jsonify({"status": "unauthorized"}), 401
    return process_transaction(request.json, source="API")

def process_transaction(data, source="UI"):
    try:
        amount = float(data.get('amount', 0))
        acc_ref = data.get('account_id', 'WEB-SIM')
        
        # Behavioral Logic
        now = datetime.datetime.now()
        day_ago = now - datetime.timedelta(days=1)
        freq = Transaction.query.filter(Transaction.timestamp >= day_ago).count() + 1
        
        # Hybrid AI Inference
        result = ml_engine.analyze_transaction(amount, now.hour, now.weekday(), freq)
        
        # Immutable Logging
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
        logger.error(f"Inference Error: {str(e)}")
        return jsonify({"error": "Internal Processing Error"}), 500

# ==========================================
# 5. BUSINESS INTELLIGENCE & REPORTING
# ==========================================


@app.route('/reports')
def reports():
    try:
        total = Transaction.query.count()
        flags = Transaction.query.filter_by(is_anomaly=True).count()
        rate = round((flags / total * 100), 1) if total > 0 else 0
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
        return render_template('reports.html', transactions=transactions, total=total, flags=flags, rate=rate)
    except Exception as e:
        return f"Database Error: {e}. Please reset database.db", 500

@app.route('/export_audit')
def export_audit():
    txs = Transaction.query.all()
    data = []
    for t in txs:
        data.append({
            'ID': t.id,
            'Amount': t.amount,
            'Date': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Score': t.anomaly_score,
            'Status': 'FLAGGED' if t.is_anomaly else 'CLEARED',
            'Reason': t.reasons
        })
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='AuditLog')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     as_attachment=True, download_name=f'Sentinel_Audit_{datetime.date.today()}.xlsx')

@app.route('/download_receipt/<tx_id>')
def download_receipt(tx_id):
    tx = Transaction.query.get_or_404(tx_id)
    receipt_content = f"BANK SENTINEL RECEIPT\nID: {tx.id}\nAmt: ${tx.amount}\nRisk: {tx.anomaly_score}\nStatus: {'FLAGGED' if tx.is_anomaly else 'CLEARED'}\nReason: {tx.reasons}"
    buf = io.BytesIO(receipt_content.encode('utf-8'))
    return send_file(buf, as_attachment=True, download_name=f"Receipt_{tx.id[:8]}.txt", mimetype='text/plain')

@app.route('/detect', methods=['POST'])
def detect_transaction():
    data = request.json
    amount = float(data.get('amount', 0))
    now = datetime.datetime.now()
    freq = Transaction.query.filter(Transaction.timestamp >= (now - datetime.timedelta(days=1))).count() + 1
    
    result = ml_engine.analyze_transaction(amount, now.hour, now.weekday(), freq)
    
    new_tx = Transaction(
        amount=amount, is_anomaly=result['is_anomaly'], 
        anomaly_score=result['score'], reasons=result['reasons'],
        account_ref='UI-DASHBOARD'
    )
    db.session.add(new_tx)
    db.session.commit()
    
    return jsonify({"status": "Flagged" if result['is_anomaly'] else "Normal", "score": result['score'], "reasons": result['reasons'], "id": new_tx.id}), 201

@app.route('/compliance')
def compliance():
    total = Transaction.query.count()
    flags = Transaction.query.filter_by(is_anomaly=True).count()
    rate = round((flags / total * 100), 1) if total > 0 else 0
    return render_template('compliance.html', transactions=Transaction.query.limit(10).all(), rate=rate)

@app.route('/settings')
def settings():
    info = {"last_train": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "total_records": Transaction.query.count()}
    return render_template('settings.html', info=info)

@app.route('/retrain', methods=['POST'])
def retrain():
    ml_engine.train_production_models()
    return jsonify({"message": "Hybrid Engine re-calibrated successfully."})


@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        session['user_id'] = 'ADMIN-EN'
        logger.info(f"Authorized access: {request.form.get('employee_id')}")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/v1/recent-transactions', methods=['GET'])
def recent_transactions():
    """Fetch recent transactions for live dashboard updates."""
    limit = request.args.get('limit', default=20, type=int)
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(limit).all()
    return jsonify([{
        'amount': tx.amount,
        'score': tx.anomaly_score,
        'status': 'Flagged' if tx.is_anomaly else 'Normal',
        'timestamp': tx.timestamp.isoformat()
    } for tx in reversed(transactions)])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)