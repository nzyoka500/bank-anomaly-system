import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        
    def train_model(self, data):
        # Features: [Amount, HourOfDay, DayOfWeek, Frequency]
        self.model.fit(data)
        joblib.dump(self.model, 'anomaly_model.pkl')

    def predict(self, transaction_features):
        model = joblib.load('anomaly_model.pkl')
        # Predict returns -1 for anomalies and 1 for normal
        prediction = model.predict([transaction_features])
        score = model.decision_function([transaction_features])
        return prediction[0], score[0]
        