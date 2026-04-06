"""
File: app.py
Project: Bank Sentinel - Unusual Bank Deposit Detection System
Description: 
    A production-grade Flask web application that serves as the command center 
    for real-time banking anomaly detection. It integrates a Machine Learning 
    pipeline (AnomalyEngine) with a persistent SQLite database for auditing 
    and historical trend analysis.

Author: [Your Name/System Name]
Date: April 2024
"""

import os
import logging
import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from model_engine import AnomalyEngine

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================

app = Flask(__name__)

# Configure Logging for production-level monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database Configuration (SQLite used for academic portability)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bank-sentinel-secure-key-2024' # Change for real deployment

db = SQLAlchemy(app)

# Initialize the ML Engine globally to keep it persistent in memory
ml_engine = AnomalyEngine()

# ==========================================
# 2. DATABASE MODELS (Objective IV: Tracking)
# ==========================================

class Transaction(db.Model):
    """
    Schema for storing every analyzed deposit. 
    This allows for long-term forensic auditing and compliance reporting.
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    is_anomaly = db.Column(db.Boolean, default=False)
    anomaly_score = db.Column(db.Float, nullable=False)
    reasons = db.Column(db.String(255), nullable=True) # Explainable AI output
    
    def __repr__(self):
        return f'<Transaction {self.id} | Amount: {self.amount} | Anomaly: {self.is_anomaly}>'

# ==========================================
# 3. CORE WEB ROUTES
# ==========================================

@app.route('/')
def index():
    """Renders the Live Monitoring Dashboard."""
    return render_template('index.html')

@app.route('/reports')
def reports():
    """
    Objective IV: Reporting and Historical Tracking.
    Fetches the 100 most recent transactions to display in the audit log.
    """
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
    return render_template('reports.html', transactions=transactions)

# ==========================================
# 4. API ENDPOINTS (Objective II: Backend System)
# ==========================================

@app.route('/detect', methods=['POST'])
def detect():
    """
    The main logic gate for the anomaly detection system.
    Receives deposit data, calculates behavioral context, and invokes the ML engine.
    """
    try:
        # 1. Parse and Validate Request
        data = request.json
        if not data or 'amount' not in data:
            return jsonify({"error": "No transaction amount provided"}), 400
        
        amount = float(data.get('amount', 0))
        
        # 2. Behavioral Context Calculation
        # We calculate frequency based on deposits in the last 24-hour rolling window
        now = datetime.datetime.now()
        day_ago = now - datetime.timedelta(days=1)
        freq = Transaction.query.filter(Transaction.timestamp >= day_ago).count() + 1
        
        # 3. Machine Learning Inference
        # Features: [Amount, Hour of Day, Day of Week, 24h Frequency]
        result = ml_engine.analyze_transaction(
            amount=amount, 
            hour=now.hour, 
            day=now.weekday(), 
            freq=freq
        )
        
        # 4. Persistence (Historical Tracking)
        new_record = Transaction(
            amount=amount, 
            is_anomaly=result['is_anomaly'], 
            anomaly_score=result['score'],
            reasons=result['reasons']
        )
        db.session.add(new_record)
        db.session.commit()
        
        # 5. Logging for Audit
        log_msg = f"TRANS_{new_record.id}: Amount {amount} | Anomaly: {result['is_anomaly']} | Score: {result['score']}"
        if result['is_anomaly']:
            logger.warning(f"ANOMALY DETECTED: {log_msg}")
        else:
            logger.info(f"NORMAL ACTIVITY: {log_msg}")

        # 6. Response Construction
        return jsonify({
            "status": "Flagged" if result['is_anomaly'] else "Normal",
            "score": result['score'],
            "reasons": result['reasons'],
            "details": f"Analyzed at {now.strftime('%H:%M:%S')}, 24h Freq: {freq}"
        })

    except ValueError:
        return jsonify({"error": "Invalid numerical input for amount"}), 400
    except Exception as e:
        logger.error(f"System Error: {str(e)}")
        return jsonify({"error": "Internal Processing Error"}), 500

# ==========================================
# 5. APPLICATION RUNNER
# ==========================================

if __name__ == '__main__':
    # Ensure database tables exist before first request
    with app.app_context():
        db.create_all()
        logger.info("Database initialized successfully.")
    
    # In production, use 'debug=False' and a WSGI server like Gunicorn
    # For project presentation, debug=True allows for live updates
    app.run(debug=True, port=5000)