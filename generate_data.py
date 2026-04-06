# File: generate_data.py
# Description: This script generates a synthetic dataset of bank deposit transactions, including both normal and anomalous records. 
# The dataset is saved as 'synthetic_deposits.csv' and includes features such as amount, hour of the day, day of the week, and frequency of deposits. 
# Anomalies are injected to simulate unusual transaction patterns for testing the anomaly detection system.

import pandas as pd
import numpy as np
import datetime

def generate_bank_data(records=2000):
    np.random.seed(42)
    data = []
    
    for i in range(records):
        # NORMAL BEHAVIOR
        amount = np.random.normal(500, 200) # Average $500
        hour = np.random.choice(range(8, 18)) # Banking hours 8am-6pm
        day_of_week = np.random.choice(range(0, 5)) # Mon-Fri
        frequency = np.random.randint(1, 3) # 1-2 deposits a day
        
        # INJECT ANOMALIES (approx 3% of data)
        if np.random.random() < 0.03:
            chance = np.random.random()
            if chance < 0.33:
                amount = np.random.uniform(5000, 10000) # Huge deposit
            elif chance < 0.66:
                hour = np.random.choice([1, 2, 3, 4]) # Late night deposit
            else:
                frequency = np.random.randint(10, 20) # Rapid micro-deposits
        
        data.append([max(1, amount), hour, day_of_week, frequency])

    df = pd.DataFrame(data, columns=['amount', 'hour', 'day_of_week', 'frequency'])
    df.to_csv('synthetic_deposits.csv', index=False)
    print("Dataset 'synthetic_deposits.csv' created with 2000 records.")

if __name__ == "__main__":
    generate_bank_data()