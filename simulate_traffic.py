import requests
import time
import random
import json

API_URL = "http://127.0.0.1:5000/api/v1/detect"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": "SENTINEL_PROD_KEY"
}

def send_transaction(amount, acc_id):
    payload = {
        "amount": amount,
        "account_id": acc_id
    }
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        result = response.json()
        status = result.get('decision', 'ERROR')
        print(f"[SENTINEL] Account: {acc_id} | Amount: ${amount:<8} | Status: {status}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(" Starting Live Bank Simulation (100 Transactions)...")
    
    for i in range(100):
        # 90% Normal transactions, 10% Anomalies
        if random.random() > 0.9:
            # Injecting an anomaly (High amount or weird behavior)
            amt = random.uniform(5000, 15000)
            acc = f"ACC-{random.randint(9000, 9999)}"
        else:
            amt = random.uniform(10, 800)
            acc = f"ACC-{random.randint(1000, 2000)}"
        
        send_transaction(round(amt, 2), acc)
        
        # Fast processing: 0.1s to 0.5s delay
        time.sleep(random.uniform(0.1, 0.5))

    print("Bingo! Simulation Complete.")