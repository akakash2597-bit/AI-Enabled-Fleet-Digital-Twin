# Installation & Setup Guide
## AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

This comprehensive guide details the step-by-step setup procedure for running the **Fleet Digital Twin** platform locally on Windows, macOS, or Linux, as well as containerized via Docker.

---

## 📋 System Prerequisites

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11 / Ubuntu 22.04 LTS |
| **Python** | Python 3.10+ | Python 3.13 |
| **RAM** | 4 GB | 8 GB or higher |
| **Disk Storage** | 1 GB free disk space | 2 GB free disk space |
| **Browser** | Modern Chromium / Firefox / Safari | Chrome or Edge (latest) |

---

## 🚀 Option 1: Native Local Installation (Recommended)

### Step 1: Clone the Repository
Open PowerShell (Windows) or Terminal (macOS/Linux):
```bash
git clone https://github.com/your-username/ai-fleet-digital-twin.git
cd "AI Enabled Prediction ML"
```

### Step 2: Configure Virtual Environment
Using Python's built-in `venv` module to isolate project dependencies:

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

#### Windows (Command Prompt):
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Dependencies
With the virtual environment activated, install all pinned libraries:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installed packages:
```bash
pip list
```
Key packages include:
- `Flask>=3.0.0`
- `scikit-learn>=1.4.0`
- `pandas>=2.1.0`
- `numpy>=1.26.0`
- `xgboost>=3.0.0`
- `matplotlib>=3.8.0`
- `seaborn>=0.13.0`
- `joblib>=1.3.0`

---

### Step 4: Initialize SQLite Fleet Database
Bootstrap the database schema and populate initial mock fleet vehicles, telemetry logs, and maintenance records:
```bash
python database/init_db.py
```
*Output Confirmation:*
```text
Connecting to SQLite database at: .../database/fleet_data.db
Database tables created successfully.
Seeded 6 fleet vehicles.
Seeded 144 telemetry logs.
Seeded 4 failure predictions.
Seeded 3 maintenance logs.
Database initialization and population finished.
```

---

### Step 5: (Optional) Retrain or Verify ML Models
The pre-trained model binaries (`model.pkl` and `scaler.pkl`) are bundled with the repository. If you wish to retrain or generate fresh exploratory figures:
```bash
# Run Exploratory Data Analysis & generate high-resolution figures:
python ml_pipeline/src/perform_eda.py

# Train & benchmark candidate models:
python ml_pipeline/src/train_model.py
```

---

### Step 6: Launch Application Server
Start the Flask development server:
```bash
python run.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🐳 Option 2: Docker Container Deployment

If you have Docker and Docker Compose installed:

### Step 1: Build & Launch with Docker Compose
```bash
docker-compose up --build -d
```

### Step 2: Verify Running Container
```bash
docker ps
```
The application will be accessible at `http://localhost:5000`.

### Step 3: Stop Container
```bash
docker-compose down
```

---

## 🧪 Running Automated Unit Tests
To verify all routes, API endpoints, and Machine Learning services:
```bash
python -m unittest discover tests
```
*Expected Result:*
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.382s

OK
```

---

## 🔑 Default Administrator Credentials
For evaluating vehicle registration, deletion, and work order scheduling:
- **Username:** `admin`
- **Password:** `admin123`
- **Login URL:** `http://127.0.0.1:5000/login`

---

## ❓ Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `Port 5000 already in use` | Another service is using port 5000 | Set a different port: `$env:FLASK_RUN_PORT="5001"` then `python run.py` |
| `ModuleNotFoundError` | Virtual environment is not active | Ensure `(venv)` appears in your terminal prompt before running scripts |
| `database is locked` | Concurrent write lock | Ensure only one server instance is running at a time |
| `Cannot activate script on PowerShell` | Execution Policy restrictions | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
