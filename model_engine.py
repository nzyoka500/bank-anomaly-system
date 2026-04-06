"""
File: model_engine.py
Project: Bank Sentinel - Unusual Bank Deposit Detection System
Description: 
    The core analytical engine of the system. It implements a hybrid 
    anomaly detection approach using:
    1. Isolation Forest: For detecting global outliers (Objective 3.7)
    2. Neural Reconstruction Error: A lightweight Autoencoder proxy for 
       complex pattern recognition (Objective 3.7)
    
This module handles feature scaling, model persistence, and explainable AI logic.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

class AnomalyEngine:
    def __init__(self):
        """
        Initializes the engine, creates directories, and loads models into memory.
        Loading models here ensures high performance during live API requests.
        """
        self.model_dir = 'models'
        self.iso_path = os.path.join(self.model_dir, 'iso_forest.pkl')
        self.auto_path = os.path.join(self.model_dir, 'autoencoder.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load or Train models
        if not os.path.exists(self.iso_path) or not os.path.exists(self.scaler_path):
            self.train_production_models()
        
        # Cache models in memory for instant inference
        self.iso_forest = joblib.load(self.iso_path)
        self.autoencoder = joblib.load(self.auto_path)
        self.scaler = joblib.load(self.scaler_path)

    def train_production_models(self):
        """
        Trains the dual-model architecture using synthetic or historical data.
        Implements both Isolation Forest and a Neural Network (Autoencoder).
        """
        print("[System] Training production-grade models...")
        
        # 1. Load Dataset
        if os.path.exists('synthetic_deposits.csv'):
            df = pd.read_csv('synthetic_deposits.csv')
        else:
            # Fallback: Create minimal training set if CSV is missing
            data = np.random.normal(size=(2000, 4))
            df = pd.DataFrame(data, columns=['amount', 'hour', 'day_of_week', 'frequency'])

        # 2. Data Preprocessing (Feature Scaling)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        
        # 3. Model A: Isolation Forest (Statistical Outliers)
        # Contamination set to 3% as per typical fraud density
        iso_forest = IsolationForest(contamination=0.03, n_estimators=200, random_state=42)
        iso_forest.fit(scaled_data)
        
        # 4. Model B: MLP-based Autoencoder (Deep Learning Proxy)
        # Learns 'Normal' behavior; high error during prediction indicates anomaly.
        autoencoder = MLPRegressor(hidden_layer_sizes=(2, 2), activation='relu', 
                                   max_iter=500, random_state=42)
        autoencoder.fit(scaled_data, scaled_data) # Input = Output for Autoencoders
        
        # 5. Persist Models
        joblib.dump(iso_forest, self.iso_path)
        joblib.dump(autoencoder, self.auto_path)
        joblib.dump(scaler, self.scaler_path)
        print("[System] Models successfully exported to /models directory.")

    def analyze_transaction(self, amount, hour, day, freq):
        """
        Performs a multi-dimensional risk analysis on a single transaction.
        
        Returns:
            dict: Contains anomaly status, unified risk score, and human-readable reasons.
        """
        # Prepare and Scale input data
        features = np.array([[amount, hour, day, freq]])
        scaled_features = self.scaler.transform(features)
        
        # Get Isolation Forest Decision (Outlier detection)
        iso_pred = self.iso_forest.predict(scaled_features)[0]
        iso_score = self.iso_forest.decision_function(scaled_features)[0]
        
        # Get Autoencoder Reconstruction Error (Pattern deviation)
        # We calculate the Mean Squared Error between input and reconstruction
        reconstructed = self.autoencoder.predict(scaled_features)
        reconstruction_error = np.mean((scaled_features - reconstructed) ** 2)
        
        # --- HYBRID RISK LOGIC ---
        # A transaction is flagged if:
        # a) It is a statistical outlier (iso_pred == -1)
        # OR b) It deviates significantly from learned patterns (Error > threshold)
        pattern_threshold = 1.5 
        is_anomaly = True if (iso_pred == -1 or reconstruction_error > pattern_threshold) else False
        
        # Unified Risk Score Calculation (Normalized roughly between -1 and 1)
        # Lower scores = Higher Risk
        unified_score = round(float(iso_score), 4)

        # Explainable AI (XAI) Logic
        reasons = []
        if is_anomaly:
            if amount > 5000: reasons.append("Volume exceeds safety threshold")
            if hour < 6 or hour > 22: reasons.append("Atypical transaction hour")
            if freq > 3: reasons.append("Rapid deposit frequency detected")
            if reconstruction_error > pattern_threshold: reasons.append("Non-linear behavioral anomaly")
            
            # Fallback if no specific rule is met but AI is suspicious
            if not reasons: reasons.append("Complex behavioral deviation")
        
        return {
            "is_anomaly": is_anomaly,
            "score": unified_score,
            "reasons": ", ".join(reasons) if is_anomaly else "Patterns consistent with history"
        }