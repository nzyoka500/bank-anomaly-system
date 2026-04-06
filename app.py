# File: app.py
# Description: Main Flask application for the Anomaly Detection System. 
# This app provides routes for the home page, anomaly detection API, and reports page. 
# It also defines a database model for tracking transactions and their anomaly status.

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from model_engine import AnomalyDetector
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database Model for Historical Tracking
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    is_anomaly = db.Column(db.Boolean)
    anomaly_score = db.Column(db.Float)

# Routes
# Home Page Route
@app.route('/')
def index():
    return render_template('index.html')

# API Endpoint for Anomaly Detection
@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    amount = float(data['amount'])
    
    # NEW: Get real-time data for behavior analysis
    now = datetime.datetime.now()
    hour = now.hour
    day = now.weekday()
    
    # For the prototype, we assume 1 frequency unless we query the DB
    # (Advanced feature: count how many times this user deposited today)
    freq = Transaction.query.filter(
        Transaction.timestamp >= datetime.datetime.now().replace(hour=0, minute=0)
    ).count() + 1

    detector = AnomalyDetector()
    pred, score = detector.predict(amount, hour, day, freq)
    
    is_unusual = True if pred == -1 else False
    
    new_tx = Transaction(amount=amount, is_anomaly=is_unusual, anomaly_score=score)
    db.session.add(new_tx)
    db.session.commit()
    
    return jsonify({
        "status": "Flagged" if is_unusual else "Normal",
        "score": round(score, 4),
        "details": f"Analyzed at hour {hour}, frequency {freq}"
    })

# Reports
@app.route('/reports')
def reports():
    all_transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('reports.html', transactions=all_transactions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Initialize DB
    app.run(debug=True)