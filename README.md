# Bank Sentinel: `AI-Driven Unusual Deposit Detection System`

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-lightgrey)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Isolation%20Forest%20%2B%20Autoencoder-orange)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Bank Sentinel** is a next-generation financial security platform that integrates hybrid Machine Learning (ML) and Deep Learning (DL) architectures to identify, flag, and audit anomalous banking transactions in real-time.


## Project Overview
Traditional fraud detection systems in banking rely heavily on static, rule-based thresholds (e.g., flagging any deposit over $10,000). While effective for basic compliance, these systems are easily bypassed by sophisticated techniques like **"smurfing"** (rapid micro-deposits) or **behavioral shifts** that stay under the limit.

**Bank Sentinel** addresses this by learning "normal" customer behavior through unsupervised learning. By analyzing the **Amount, Time, Day, and Frequency** of deposits, the system identifies subtle deviations that indicate potential fraud, money laundering, or account takeover.


## The Problem
Financial institutions face three critical challenges:
1.  **Rule Rigidity:** Conventional systems cannot adapt to evolving fraud patterns without manual reprogramming.
2.  **Delayed Intervention:** Manual audits often occur days after a suspicious event, leading to irreversible financial loss.
3.  **Lack of Context:** Most systems look at individual transactions in isolation, ignoring the behavioral frequency and temporal patterns of the user.


## Goals & Objectives

### Main Objective
To develop a scalable web-based application that detects and flags unusual bank deposits by integrating a high-performance machine learning backend with an intuitive administrative frontend.

### Minor Objectives
*   **Analyze** current limitations in rule-based anomaly detection.
*   **Develop** a hybrid ML engine utilizing **Isolation Forests** and **Neural Autoencoders**.
*   **Implement** a secure, real-time dashboard for transaction monitoring.
*   **Provide** comprehensive reporting and forensic audit logs for regulatory compliance (AML/BSA).


## Key Features

*   **Live Monitoring Dashboard:** Real-time visualization of transaction risk using `Chart.js`.
*   **Hybrid AI Engine:** Dual-model verification using statistical outliers and neural reconstruction errors.
*   **Explainable AI (XAI):** The system doesn't just flag; it provides reasons (e.g., "Unusual Hour," "High Frequency").
*   **Forensic Audit Log:** A persistent, searchable ledger of all analyzed transactions.
*   **Compliance Oversight:** Tools to adjust AI sensitivity and monitor system regulatory health.
*   **MLOps Console:** On-demand model retraining to adapt to new datasets.


## Technical Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3.10, Flask |
| **Machine Learning** | Scikit-Learn (Isolation Forest), MLPRegressor (Autoencoder) |
| **Database** | SQLite, SQLAlchemy (ORM) |
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript (ES6) |
| **Visualization** | Chart.js |
| **Icons** | FontAwesome 6 (Free) |


## System Preview

> *Note: Replace these placeholders with your actual project screenshots.*

### 1. Public Landing Page
*Overview of the technical framework and value proposition.*
![Landing Page](/static/screenshots/landing.png)

### 2. Live Monitor
*The real-time analysis center with live risk trending.*
![Live Monitor](/static/screenshots/dashboard.png)

### 3. Audit History
*Searchable database of security flags and timestamps.*
![Audit History](/static/screenshots/audit.png)

### 4. Compliance
*Compliance documents and guidelines*
![Compliance](/static/screenshots/compliance.png)

### 5. ML Settings
*Machine learning engine page controls*
![Settings page](/static/screenshots/settings.png)

### 5. Login
*User portal authenication page*
![User Login](/static/screenshots/login.png)


## Installation & Setup

Ensure you have Python 3.10+ installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/bank-anomaly-system.git
cd bank-anomaly-system
```

### 2. Create a Virtual Environment
This prevents the "externally-managed-environment" error on modern Linux distros.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask flask-sqlalchemy scikit-learn pandas joblib
```

### 4. Initialize the Data & Server
```bash
python3 generate_data.py  # Creates the synthetic training set
python3 app.py            # Starts the production server
```

### 5. Access the Portal
Open your browser and navigate to:
`http://127.0.0.1:5000`


## Machine Learning Methodology
The system employs a **Hybrid Anomaly Score**:
1.  **Isolation Forest:** Partitions data points. Points that isolate quickly are marked as statistical outliers.
2.  **Autoencoder (Neural Network):** Learns the compressed representation of normal transactions. If a new transaction results in a high **Reconstruction Error**, it is flagged as a behavioral anomaly.


## License
Distributed under the MIT License. See `LICENSE` for more information.
