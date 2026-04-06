# File: model-engine.py
# Description: This module defines the AnomalyDetector class, which uses an Isolation Forest model to detect anomalies in transaction data. 
# It includes methods for training the model and making predictions based on transaction features

import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

class AnomalyDetector:
    def __init__(self):
        self.model_path = 'anomaly_model.pkl'
        self.data_path = 'synthetic_deposits.csv'
        
        # If no model exists, train it immediately on the synthetic data
        if not os.path.exists(self.model_path):
            self.retrain_from_file()

    def retrain_from_file(self):
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            model = IsolationForest(contamination=0.03, random_state=42)
            model.fit(df)
            joblib.dump(model, self.model_path)
            print("Model successfully trained on synthetic data.")
        else:
            print("Error: No training data found. Run generate_data.py first.")

    def predict(self, amount, hour=None, day=None, freq=1):
        import datetime
        now = datetime.datetime.now()
        
        # Use current time/day if not provided
        h = hour if hour is not None else now.hour
        d = day if day is not None else now.weekday()
        
        model = joblib.load(self.model_path)
        # We must provide all 4 features used during training
        features = [[float(amount), h, d, freq]]
        
        pred = model.predict(features)
        score = model.decision_function(features)
        return pred[0], score[0]