# AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

**Final Year B.Tech Project | Artificial Intelligence & Data Science (AI & DS)**

---

## 📌 Project Overview
This project presents an end-to-end cyber-physical **Digital Twin** system for connected fleet management. By streaming multidimensional sensor telemetry (engine temperature, vibration levels, oil pressure, coolant temperature, battery voltage, and RPM) into a machine learning classification engine, the system predicts vehicle component failures before they occur and reflects live telemetry on an interactive web dashboard.

---

## 🏗️ Technology Stack
- **Backend**: Python 3.13+, Flask
- **Machine Learning**: Scikit-learn, Pandas, NumPy, Joblib
- **Database**: SQLite3
- **Frontend / Visualization**: HTML5, CSS3, JavaScript (ES6+), Chart.js

---

## 📂 Project Folder Structure

```text
AI Enabled Prediction ML/
├── app/                           # Core Flask Application Package
│   ├── __init__.py                # App factory initialization & Blueprint registration
│   ├── config.py                  # Environment configurations & filesystem paths
│   ├── models/                    # Database models and connection management
│   │   ├── __init__.py
│   │   └── db.py                  # SQLite request-scoped connection helpers
│   ├── routes/                    # Route handlers & Blueprints
│   │   ├── __init__.py
│   │   ├── api.py                 # REST API endpoints (telemetry, predictions, twin state)
│   │   └── views.py               # Template view controllers (Dashboard, Twin View, Alerts)
│   ├── services/                  # Business logic & background engines
│   │   ├── __init__.py
│   │   ├── digital_twin.py        # Digital Twin state machine & synchronization
│   │   └── predictor.py           # ML model inference & risk scoring service
│   ├── static/                    # Frontend static assets
│   │   ├── css/
│   │   │   ├── style.css          # Global styling, responsive layout, dark theme
│   │   │   └── dashboard.css      # Dashboard components, KPI cards, status badges
│   │   ├── js/
│   │   │   ├── charts.js          # Chart.js time-series charts for vehicle telemetry
│   │   │   ├── digital_twin.js    # Client-side twin state controller
│   │   │   └── main.js            # General DOM interactions
│   │   └── assets/                # Schematic icons and diagrams
│   └── templates/                 # Jinja2 HTML templates
│       ├── base.html              # Base shell with navigation, styles, and Chart.js CDN
│       ├── index.html             # Project overview & hero landing page
│       ├── dashboard.html         # Fleet-wide digital twin dashboard with KPI cards
│       ├── vehicle_detail.html    # Specific vehicle digital twin telemetry view
│       └── predictions.html       # Predictive maintenance failure alerts log
├── database/                      # Data persistence layer
│   ├── schema.sql                 # Relational schema for vehicles, telemetry, alerts
│   └── init_db.py                 # SQLite bootstrap & mock fleet seeder script
├── ml_pipeline/                   # Machine Learning training & evaluation
│   ├── dataset/
│   │   └── sample_telemetry.csv   # Historical sensor telemetry & failure labels
│   ├── notebooks/                 # Jupyter notebooks for EDA and experimentation
│   ├── saved_models/              # Serialized model (.pkl) & scaler artifacts
│   └── src/                       # Production ML scripts
│       ├── data_preprocessing.py  # Data cleaning, scaling, feature engineering
│       ├── train_model.py         # Model training script
│       └── evaluate.py            # Classification metrics & confusion matrix
├── tests/                         # Automated unit & integration tests
│   ├── test_ml.py
│   └── test_routes.py
├── .gitignore                     # Git exclusion rules
├── requirements.txt               # Pinned Python package dependencies
├── run.py                         # Application entry point
└── README.md                      # Project documentation
```

---

## ⚙️ Quickstart & Setup

### 1. Activate the Virtual Environment
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

### 2. Verify Dependencies
Dependencies are pre-installed in `venv`:
```bash
pip list
```

### 3. Initialize SQLite Database
```bash
python database/init_db.py
```

### 4. Run the Application
```bash
python run.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
