# Bank Sentinel: `Hybrid AI Anomaly Detection System`

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-lightgrey)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Isolation%20Forest%20%2B%20Autoencoder-orange)](https://scikit-learn.org/)
[![Security](https://img.shields.io/badge/security-Talisman%20%2B%20CSP-red)](https://github.com/40874/flask-talisman)
[![Docker](https://img.shields.io/badge/docker-ready-cyan)](https://www.docker.com/)

**Bank Sentinel** is a financial security platform designed for African FinTechs, SACCOs, and Banks. It integrates **Hybrid Machine Learning** and **Deep Learning** architectures to provide real-time identification, forensic auditing, and autonomous flagging of anomalous banking transactions.


## Project Goal
To implement a AI platform that integrates hybrid machine learning to automate the real-time detection, forensic auditing, and autonomous flagging of anomalous bank deposits.

## The Gap Solved
This system bridges the critical failure of static, threshold-based monitoring by identifying sophisticated behavioral fraud patterns—such as rapid smurfing and non-linear irregularities—that bypass traditional banking rules.

## The Problem
Financial institutions across Africa face three critical security gaps:
1.  **Rule Rigidity:** Conventional systems fail to adapt to evolving fraud patterns (e.g., account takeovers) without manual reprogramming.
2.  **Delayed Intervention:** Manual audits often occur days after a suspicious event, making fund recovery impossible.
3.  **Context Blindness:** Standard checks look at transaction amounts in isolation, ignoring the **temporal frequency** and **behavioral patterns** of the account holder.


## Key Features

*   **Hybrid AI Core:** Dual-brain verification using **Isolation Forest** (Statistical Outliers) and **Neural Autoencoders** (Behavioral Reconstruction Error).
*   **Live Monitoring Dashboard:** Premium Glassmorphic UI featuring real-time risk trending via `Chart.js`.
*   **API-First Architecture:** RESTful endpoints (`/api/v1/detect`) designed for seamless integration with Core Banking Systems and Mobile Money Gateways.
*   **Explainable AI (XAI):** Provides human-readable justifications for flags (e.g., *"High-Frequency Smurfing Pattern"*).
*   **Forensic Ledger:** A persistent, searchable audit trail with **Excel/PDF Export** capabilities for regulatory compliance.
*   **Production Security:** Integrated `Flask-Talisman` for CSP/HSTS protection and `Flask-Migrate` for schema versioning.


## Technical Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3.10, Flask (Production-optimized) |
| **Machine Learning** | Scikit-Learn (Isolation Forest), MLPRegressor (Autoencoder) |
| **Security** | Flask-Talisman (CSP/HSTS), Flask-Migrate, Dotenv |
| **Database** | SQLite / SQLAlchemy (PostgreSQL Ready) |
| **Frontend** | HTML5, CSS3 (Premium Glassmorphism), Bootstrap 5, SweetAlert2 |
| **Visualization** | Chart.js 4.x |


## System Preview

### 1. Public Landing Page
*Executive overview of the technical framework and value proposition.*
![Landing Page](static/screenshots/landing.png)

### 2. Live Monitor
*Real-time analysis center with live behavioral stream and risk trending.*
![Live Monitor](static/screenshots/dashboard.png)

### 3. Audit History
*Searchable database of security flags and automated forensic reasons.*
![Audit History](static/screenshots/audit.png)

### 4. Compliance Oversight
*Regulatory health scoring and AI sensitivity policy controls.*
![Compliance](static/screenshots/compliance.png)

### 5. ML Engine Settings
*MLOps console for neural weight retraining and model health monitoring.*
![Settings](static/screenshots/settings.png)

### 6. Secure Login
*Auth-protected gateway with session encryption.*
![User Login](static/screenshots/login.png)

---

## Installation & Setup

### 1. Environment Preparation
```bash
# Clone the repository
git clone https://github.com/yourusername/bank-anomaly-system.git
cd bank-anomaly-system

# Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependency Installation
```bash
pip install -r requirements.txt
```

### 3. System Initialization
```bash
# Generate baseline synthetic behavioral data
python3 generate_data.py

# Launch the Sentinel Production Server
python3 app.py
```

### 4. Live Simulation (For Demonstrations)
To see the system act automatically, run the traffic simulator in a second terminal:
```bash
python3 simulate_traffic.py
```


## Machine Learning Methodology
The system employs a **Hybrid Decision Logic**:
1.  **Isolation Forest (IF):** Detects statistical "Global Outliers" by measuring how easily a transaction is isolated in a decision tree.
2.  **Neural Autoencoder (AE):** A deep learning model that learns the "Identity" of normal behavior. Transactions that produce a high **Reconstruction Error (MSE)** are flagged as complex behavioral deviations.

## Enterprise Integration
Bank Sentinel is designed as a **pluggable security module**. 
*   **Credit Intelligence:** Anomaly scores can be fed into credit scoring models to identify high-risk borrowers.
*   **Automated AML:** Replaces manual KYC/AML checks for SACCOs with an automated API-driven ledger.
*   **Scalability:** Docker-ready containerization for deployment in AWS/Azure clusters.


## License
Distributed under the MIT License. Developed by **ERIC NZYOKA**.

