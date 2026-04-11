"""
File: model_engine.py
Project: Bank Sentinel - Unusual Bank Deposit Detection System
Target: Production-Grade FinTech Infrastructure (e.g., Spin Mobile Integration)
Description: 
    A High-Performance Hybrid Anomaly Detection Engine. 
    Uses an ensemble of:
    1. Isolation Forest (Statistical Outliers)
    2. Neural Autoencoder (Behavioral/Non-linear Outliers)

Features: Self-healing training, Standardized Feature Scaling, and Explainable AI (XAI).
"""

import os
import joblib
import logging
import pandas as pd
import numpy as np
import datetime
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sentinel-Engine")

class AnomalyEngine:
    def __init__(self):
        """
        Initializes the analytical core. Implements 'Singleton-style' 
        caching for models to ensure ultra-low latency in production.
        """
        self.model_dir = 'models'
        self.iso_path = os.path.join(self.model_dir, 'iso_forest.pkl')
        self.auto_path = os.path.join(self.model_dir, 'autoencoder.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load models or trigger self-healing if files are missing
        self._initialize_system()

    def _initialize_system(self):
        """Ensures all necessary ML artifacts exist before serving traffic."""
        if not all(os.path.exists(p) for p in [self.iso_path, self.auto_path, self.scaler_path]):
            logger.warning("ML Artifacts missing. Initiating self-healing training...")
            self.train_production_models()
        
        try:
            self.iso_forest = joblib.load(self.iso_path)
            self.autoencoder = joblib.load(self.auto_path)
            self.scaler = joblib.load(self.scaler_path)
            logger.info("Sentinel Hybrid Engine successfully loaded into memory.")
        except Exception as e:
            logger.error(f"Critical failure loading models: {e}")
            # In production, this would trigger an alert to the SRE team

    def train_production_models(self):
        """
        Calibrates the Hybrid AI Core. 
        In production, this is usually triggered via the /retrain API 
        after new historical data is ingested.
        """
        logger.info(f"Retraining started at {datetime.datetime.now()}")
        
        # 1. Dataset Acquisition
        if os.path.exists('synthetic_deposits.csv'):
            df = pd.read_csv('synthetic_deposits.csv')
        else:
            # Fallback: Create 5000 records of 'Normal' banking data for baseline
            logger.info("No training CSV found. Generating baseline behavioral data...")
            data = np.random.normal(loc=[300, 12, 2, 1], scale=[100, 4, 1, 0.5], size=(5000, 4))
            df = pd.DataFrame(data, columns=['amount', 'hour', 'day_of_week', 'frequency'])

        # 2. Preprocessing & Normalization
        # Crucial for Neural Networks to prevent 'feature drowning'
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        
        # 3. Component A: Isolation Forest (Global Outliers)
        # We increase n_estimators for higher stability in production
        iso_forest = IsolationForest(contamination=0.03, n_estimators=250, random_state=42)
        iso_forest.fit(scaled_data)
        
        # 4. Component B: Neural Autoencoder (Deep Pattern Outliers)
        # Learns the identity of 'Normal' transactions
        autoencoder = MLPRegressor(
            hidden_layer_sizes=(16, 8, 16), 
            activation='relu', 
            solver='adam', 
            max_iter=1000, 
            random_state=42
        )
        autoencoder.fit(scaled_data, scaled_data)
        
        # 5. Serialization
        joblib.dump(iso_forest, self.iso_path)
        joblib.dump(autoencoder, self.auto_path)
        joblib.dump(scaler, self.scaler_path)
        
        # Re-cache the active models
        self.iso_forest = iso_forest
        self.autoencoder = autoencoder
        self.scaler = scaler
        
        logger.info("Retraining complete. System re-calibrated.")

    def analyze_transaction(self, amount, hour, day, freq):
        """
        Standardized Inference Pipeline.
        Evaluates a single transaction through the dual-brain architecture.
        """
        try:
            # Prepare inputs
            # raw_features = np.array([[float(amount), int(hour), int(day), int(freq)]])
            # scaled_features = self.scaler.transform(raw_features)

            # Create a DataFrame instead of an array to keep feature names
            raw_features = pd.DataFrame([[float(amount), int(hour), int(day), int(freq)]], 
                                        columns=['amount', 'hour', 'day_of_week', 'frequency'])
            scaled_features = self.scaler.transform(raw_features)
            
            # --- MODEL 1: ISOLATION FOREST ---
            iso_pred = self.iso_forest.predict(scaled_features)[0]
            iso_score = self.iso_forest.decision_function(scaled_features)[0]
            
            # --- MODEL 2: NEURAL AUTOENCODER ---
            # High reconstruction error = The AI doesn't recognize this behavior
            reconstructed = self.autoencoder.predict(scaled_features)
            recon_error = np.mean((scaled_features - reconstructed) ** 2)
            
            # --- HYBRID RISK SCORING ---
            # Thresholds are tuned for low-risk banking environments
            # MSE > 2.0 is highly anomalous in a scaled environment
            is_anomaly = True if (iso_pred == -1 or recon_error > 2.0) else False
            
            # Calculate Risk Level
            # -1 to 0 (IF Score): -1 is max risk, 0 is no risk.
            risk_val = "LOW"
            if iso_score < -0.1 or recon_error > 2.5: risk_val = "CRITICAL"
            elif iso_score < 0 or recon_error > 1.8: risk_val = "MEDIUM"

            # Explainable AI (XAI) Mapping
            reasons = self._generate_reasons(amount, hour, freq, recon_error)
            
            return {
                "is_anomaly": is_anomaly,
                "score": round(float(iso_score), 4),
                "risk_level": risk_val,
                "reasons": ", ".join(reasons) if is_anomaly else "Normal behavioral pattern"
            }

        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return {"is_anomaly": False, "score": 0, "risk_level": "ERROR", "reasons": "Analysis bypass due to system error"}

    def _generate_reasons(self, amount, hour, freq, error):
        """Heuristic layer to provide human-readable justification for AI flags."""
        reasons = []
        if amount > 8000: reasons.append("Large-Value Transaction (LVT)")
        if hour < 5 or hour > 23: reasons.append("Atypical time of activity")
        if freq > 4: reasons.append("High-Frequency Smurfing Pattern")
        if error > 2.0: reasons.append("Complex non-linear behavioral anomaly")
        
        if not reasons: reasons.append("Structural behavioral deviation")
        return reasons