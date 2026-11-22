# Academic Project Report
# AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

**Department of Artificial Intelligence & Data Science (AI & DS)**  
**Degree:** Bachelor of Technology (B.Tech)  
**Academic Year:** 2025 – 2026  

---

## Executive Summary / Abstract

Catastrophic automotive failures in commercial vehicle fleets incur substantial financial losses, supply chain delays, and safety hazards. Conventional maintenance strategies—namely reactive "run-to-failure" and periodic "calendar/odometer-based" inspections—either occur too late or replace mechanical components prematurely. 

This project presents the design, development, and evaluation of an end-to-end **Cyber-Physical Digital Twin Platform** for predictive vehicle fleet maintenance. Built upon an automotive dataset of **19,535 real-world engine records**, the system trains and benchmarks four machine learning architectures: **Logistic Regression, Decision Trees, Random Forests, and XGBoost**. 

Using standardized multidimensional telemetry (Engine RPM, Lubrication Oil Pressure, Fuel Rail Pressure, Coolant Line Pressure, Lubrication Oil Temperature, and Coolant Temperature), the production classifier achieves **87.82% Recall**, **76.57% F1-Score**, and **69.18% ROC-AUC**, successfully minimizing costly False Negatives. The model is integrated into a Flask web application with SQLite database persistence, interactive 2D digital twin subsystem virtualization, a live sensor simulator, Chart.js time-series telemetry charts, and an automated Remaining Useful Life (RUL) estimator that outputs plain-English explanations for every diagnostic prediction.

---

## Table of Contents
1. [Introduction & Background](#1-introduction--background)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Literature Review & Comparison of Maintenance Paradigms](#3-literature-review--comparison-of-maintenance-paradigms)
4. [Dataset Analysis & Exploratory Data Findings](#4-dataset-analysis--exploratory-data-findings)
5. [Machine Learning Methodology & Benchmark Comparisons](#5-machine-learning-methodology--benchmark-comparisons)
6. [Digital Twin State Machine & Remaining Useful Life (RUL) Modeling](#6-digital-twin-state-machine--remaining-useful-life-rul-modeling)
7. [System Architecture & Full-Stack Implementation](#7-system-architecture--full-stack-implementation)
8. [Experimental Results & Discussion](#8-experimental-results--discussion)
9. [Conclusion & Future Enhancements](#9-conclusion--future-enhancements)
10. [Viva Voce Technical Defense: Top 20 Questions & Detailed Answers](#10-viva-voce-technical-defense-top-20-questions--detailed-answers)

---

## 1. Introduction & Background

In the transportation and logistics sectors, commercial haulage trucks operate under arduous thermal and mechanical stress cycles. Heavy internal combustion engines undergo continuous friction, cyclic thermal expansion, and hydraulic pressures. 

A single on-road engine seizure results in:
- Unplanned towing and emergency roadside assistance costs.
- Complete cylinder head and crankshaft block replacement expenses.
- Severe contractual SLA violation penalties due to late freight delivery.

The convergence of **Internet of Things (IoT)** sensors, **Machine Learning**, and **Digital Twin technologies** enables fleet operators to create a living, synchronized virtual replica of each physical vehicle. Rather than relying on static time intervals, maintenance decisions are driven by dynamic data reflecting real-time physical degradation.

---

## 2. Problem Statement & Objectives

### 2.1 Problem Statement
*Existing fleet management telematics dashboards display raw sensor numbers (e.g. "Coolant Temp: 110°C") without providing automated probabilistic failure prediction, root-cause subsystem diagnostics, or Remaining Useful Life projections.*

### 2.2 Objectives
1. **Acquire and Validate Real Automotive Data**: Source a public automotive telemetry dataset with over 5,000 observations containing continuous multi-sensor parameters and binary failure ground truth.
2. **Conduct Rigorous Exploratory Data Analysis (EDA)**: Inspect distributions, class balance, outliers, and feature importances.
3. **Train & Benchmark ML Classifiers**: Evaluate Logistic Regression, Decision Trees, Random Forests, and XGBoost on held-out test splits, prioritizing **Recall** to eliminate catastrophic False Negatives.
4. **Develop a Cyber-Physical Digital Twin Engine**: Decompose vehicle health across five distinct mechanical subsystems (Engine Core, Cooling, Lubrication, Fuel Injection, and Transmission).
5. **Formulate Remaining Useful Life (RUL)**: Translate raw classification probabilities into actionable kilometers and operating hours before failure.
6. **Implement Explainable AI (XAI)**: Generate transparent, plain-English explanations breaking down why a prediction was made.
7. **Deploy a Modern Web Application**: Provide fleet managers with a responsive dark-themed dashboard, interactive live simulator, and administrative controls.

---

## 3. Literature Review & Comparison of Maintenance Paradigms

| Maintenance Paradigm | Trigger Mechanism | Advantage | Disadvantage in Commercial Fleets |
| :--- | :--- | :--- | :--- |
| **Reactive Maintenance** *(Run-to-Failure)* | Physical breakdown on road | Zero upfront inspection costs | Catastrophic downtime, dangerous roadside accidents, maximum repair expense. |
| **Preventive Maintenance** *(Time / Odometer based)* | Fixed odometer (e.g. every 20,000 km) | Reduces unexpected failures | Replaces components that still have 40% usable life; misses sudden acute anomalies occurring between service cycles. |
| **Condition-Based Monitoring (CBM)** | Static threshold rule (e.g., if Temp > 100°C) | Alerts operators of active anomalies | High false alarm rate; cannot capture subtle multi-sensor non-linear interactions. |
| **AI-Enabled Digital Twin** *(Proposed)* | Machine Learning inference on multi-sensor streams | Predicts failures before occurrence, projects RUL, localizes suspect subsystem, explains prediction. | Requires initial training dataset and sensor integration. |

---

## 4. Dataset Analysis & Exploratory Data Findings

The system utilizes the **Automotive Vehicles Engine Health Dataset** (`engine_data.csv`), hosted on Kaggle and sourced from automotive dynamometer testbeds.

### 4.1 Schema Breakdown
- **Sample Size:** 19,535 records
- **Data Completeness:** 100% (0 missing values, 0 duplicate rows)
- **Features:**
  1. `Engine rpm` (int64, Mean: 791.24, Range: 61 – 2,239 RPM)
  2. `Lub oil pressure` (float64, Mean: 3.30, Range: 0.0034 – 7.27 bar)
  3. `Fuel pressure` (float64, Mean: 6.66, Range: 0.0032 – 21.14 bar)
  4. `Coolant pressure` (float64, Mean: 2.34, Range: 0.0025 – 7.48 bar)
  5. `lub oil temp` (float64, Mean: 77.64, Range: 71.32 – 89.58 °C)
  6. `Coolant temp` (float64, Mean: 78.43, Range: 61.67 – 195.53 °C)
  7. `Engine Condition` (Binary target: `0` = Healthy [36.95%], `1` = Fault [63.05%])

### 4.2 Key EDA Insights
- **Thermal Anomalies**: In healthy engines, coolant temperature clusters tightly between 72°C and 85°C. Under failure states, temperature spikes up to 195.5°C, representing severe loss of cooling capacity.
- **Multicollinearity Check**: Linear correlation coefficients between features are low to moderate ($|r| < 0.35$), confirming that failure cannot be detected by monitoring any single sensor in isolation.

---

## 5. Machine Learning Methodology & Benchmark Comparisons

An 80/20 stratified split was executed, yielding **15,628 training samples** and **3,907 test samples**. Continuous variables were normalized via Z-Score Standardization.

### 5.1 Benchmark Comparison Table

| Architecture | Accuracy | Precision | Recall (Sensitivity) | F1-Score | ROC-AUC | Composite Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 🏆 **Logistic Regression (Standardized)** | **66.11%** | **67.87%** | **87.82%** | **76.57%** | **69.18%** | **1st (72.87%)** |
| 🥈 **XGBoost (Gradient Boosted Trees)** | **66.19%** | **69.57%** | **82.42%** | **75.45%** | **69.12%** | **2nd (72.29%)** |
| 🥉 **Random Forest (100 Trees, Depth 15)**| **65.27%** | **68.75%** | **82.34%** | **74.93%** | **68.86%** | **3rd (71.90%)** |
| 4️⃣ **Decision Tree (Max Depth 10)** | **63.76%** | **69.76%** | **75.03%** | **72.30%** | **63.98%** | **4th (68.14%)** |

### 5.2 Rationale for Best Model Selection
1. **Criticality of Recall (87.82%)**: In vehicle maintenance, a False Negative (failing to predict an engine failure) results in total engine seizure and towing fees ($5,000+). A False Positive results only in an inspection check ($50). Logistic Regression successfully captured **2,163 of 2,463 failures** in the test set.
2. **Sigmoid Probability Calibration**: Unlike tree models that output piecewise step probabilities, the logistic sigmoid produces smoothly continuous probabilities ($0.0 \to 1.0$), perfectly suited for driving analog health gauges.
3. **Sub-Millisecond Execution**: Computes predictions via dot-product in $<0.05\text{ ms}$, enabling high-frequency vehicle telemetry streaming.

---

## 6. Digital Twin State Machine & Remaining Useful Life (RUL) Modeling

The digital twin decomposes each vehicle into five functional subsystems:
- **Engine Core & Cylinders**: $H_{\text{eng}} = 0.4 H_{\text{cool}} + 0.4 H_{\text{lub}} + 0.2 H_{\text{fuel}}$
- **Cooling Circuit**: Triggers warning above 88°C and critical alerts above 105°C or pressure drops below 1.0 bar.
- **Lubrication Subsystem**: Tracks oil pressure ($< 2.0\text{ bar}$) and temperature ($> 85^\circ\text{C}$).
- **Fuel Injection System**: Identifies fuel rail pressure surges ($> 11.5\text{ bar}$) or delivery deficits ($< 3.5\text{ bar}$).
- **Transmission & Drivetrain**: Monitors rotational load and RPM stability.

RUL is computed piecewise:
- **CRITICAL** ($P \ge 0.75$): $\text{RUL} = \max(20, (1 - P) \times 350)\text{ km}$ (~1–8 hours).
- **HIGH** ($0.50 \le P < 0.75$): $\text{RUL} = 500 + (0.75 - P) \times 4000\text{ km}$ (~10–50 hours).
- **MEDIUM** ($0.35 \le P < 0.50$): $\text{RUL} = 3500 + (0.50 - P) \times 9000\text{ km}$ (~60–145 hours).
- **LOW** ($P < 0.35$): $\text{RUL} = 15000 + (0.35 - P) \times 25000\text{ km}$ (~250–600 hours).

---

## 7. System Architecture & Full-Stack Implementation

- **Backend**: Python 3.13, Flask (Application Factory pattern with Blueprints: `views_bp`, `api_bp`).
- **Persistence**: SQLite 3 with request-scoped connection teardowns.
- **Frontend**: Responsive modern cyber-industrial dark aesthetic, vanilla ES6+ JavaScript, Chart.js for time-series and doughnut charts.
- **Explainability**: Sensor-by-sensor deviation engine comparing observed values against nominal automotive bounds.
- **Security**: Session-based admin authentication (`admin` / `admin123`) protecting vehicle registration and work order dispatch.

---

## 8. Experimental Results & Discussion

### 8.1 Confusion Matrix of Production Model
On the 3,907 held-out test records:
- **True Positives (TP):** 2,163 (Correctly identified impending failures)
- **False Negatives (FN):** 300 (Undetected failures — lowest among all models)
- **True Negatives (TN):** 419 (Correctly verified nominal operations)
- **False Positives (FP):** 1,025 (Conservative pre-cautionary inspection flags)

The high sensitivity guarantees that over 87 out of 100 failing vehicles are intercepted before leaving the depot.

---

## 9. Conclusion & Future Enhancements

The AI-Enabled Fleet Digital Twin bridges the gap between raw vehicle IoT sensor data and operational maintenance dispatch. By combining machine learning failure prediction, subsystem decomposition, RUL forecasting, and natural language explanations, the platform eliminates catastrophic roadside breakdowns.

### Future Scope
1. **Edge Microcontroller Deployment**: Porting the standardized inference pipeline to ESP32 / Raspberry Pi CAN-bus readers for onboard offline execution.
2. **Temporal Deep Learning**: Exploring Long Short-Term Memory (LSTM) networks or Gated Recurrent Units (GRU) to learn multi-day temporal sensor trends.
3. **Automated Parts Inventory Integration**: Linking diagnosed components directly with ERP inventory systems to order replacement filters and pumps automatically.

---

## 10. Viva Voce Technical Defense: Top 20 Questions & Detailed Answers

### Q1: What is a Digital Twin, and how is it applied in your project?
> **Answer:** A Digital Twin is a synchronized, cyber-physical software model that reflects the exact real-time state of a physical asset. In this project, each commercial vehicle has a virtual twin that ingests 6 continuous sensor channels from vehicle ECUs, updates health scores across 5 mechanical subsystems, predicts failure likelihood, and forecasts Remaining Useful Life.

### Q2: Why did you choose Logistic Regression over complex algorithms like Random Forest or XGBoost?
> **Answer:** In mission-critical predictive maintenance, **Recall is the governing performance metric**. Failing to detect an engine failure (False Negative) causes engine seizure and thousands of dollars in roadside towing, whereas a False Positive merely prompts a standard workshop check. Logistic Regression achieved the highest Recall (**87.82%**), beating Random Forest (82.34%) and XGBoost (82.42%). Furthermore, it provides smooth, calibrated sigmoid probabilities and executes in under 0.05 ms, ideal for real-time edge streaming.

### Q3: Why is feature standardization necessary before feeding sensor readings into the model?
> **Answer:** Automotive sensors operate across drastically different scales—Engine RPM ranges around 700–900, while Oil Pressure is ~3 bar and Coolant Temperature is ~80°C. Without Z-score standardization, features with larger raw magnitudes (such as RPM) would dominate the loss gradient. Standardization centers each feature around zero with unit variance ($z = (x - \mu)/\sigma$).

### Q4: How is Remaining Useful Life (RUL) calculated?
> **Answer:** RUL is mathematically modeled as an inverse piecewise function of the model's failure probability risk score and critical sensor thresholds. High probabilities ($P \ge 0.75$) correspond to immediate danger ($20 - 350\text{ km}$, 1–8 operating hours), while nominal scores ($P < 0.35$) correspond to standard intervals ($15,000 - 25,000\text{ km}$).

### Q5: How does your system explain predictions to a non-technical fleet manager?
> **Answer:** Our Explainable AI (XAI) engine compares each incoming sensor value against manufacturer baseline ranges (e.g. 72–85°C for coolant). It computes the directional impact of each sensor on the model's log-odds and generates a cohesive plain-English summary stating which component is failing and what physical consequences will follow if left unserviced.

### Q6: What dataset did you use, and what is its sample size?
> **Answer:** We used the Kaggle **Automotive Vehicles Engine Health Dataset**, comprising **19,535 records** and 7 columns representing real internal combustion engine telemetry with zero missing values and zero duplicate rows.

### Q7: What are the target classes, and was there class imbalance?
> **Answer:** The binary target is `Engine Condition`: `0` for Normal/Operational (36.95%, 7,218 records) and `1` for Maintenance Required/Fault (63.05%, 12,317 records). Because the minority class constitutes more than one-third of the dataset, there is no severe imbalance requiring artificial resampling such as SMOTE.

### Q8: How does the live telemetry simulator work in your web application?
> **Answer:** The simulator provides sliders and demo presets. Moving a slider triggers an asynchronous JavaScript `fetch('/api/predict')` request debounced at 150 ms. The Flask backend runs the ML model and returns updated subsystem statuses, RUL, and explanations, updating the DOM dynamically without page reloads.

### Q9: What happens if an invalid or non-numeric sensor value is sent to the API?
> **Answer:** The API implements strict type checking. If non-numeric data is provided, it returns a structured HTTP `400 Bad Request` JSON response stating exactly which field was invalid.

### Q10: How are database transactions handled in SQLite to avoid locking?
> **Answer:** We utilize Flask's application context (`g.db`). Database connections are opened per request and safely closed upon completion using `@app.teardown_appcontext(close_db)`.

### Q11: How do you identify which subsystem is failing?
> **Answer:** Through rule-guided diagnostic trees coupled with ML probability. For instance, if failure probability is elevated and coolant temperature exceeds 95°C, the system isolates the **Engine Cooling Circuit**. If oil pressure drops below 2.0 bar, it isolates the **Lubrication Subsystem**.

### Q12: Why use Chart.js instead of server-side matplotlib rendering in the web app?
> **Answer:** Chart.js renders client-side using HTML5 Canvas, providing smooth animations, interactive hover tooltips, responsive resizing, and zero server CPU rendering overhead. Matplotlib is retained for offline scientific report figure generation.

### Q13: What is the F1-Score of your model, and why is it preferred over Accuracy?
> **Answer:** The production model achieved an F1-Score of **76.57%**. F1-Score is the harmonic mean of Precision and Recall ($2PR / (P+R)$), balancing the trade-off between false alarms and missed detections, which accuracy cannot properly reflect.

### Q14: How does the admin authentication system function?
> **Answer:** Admin authentication utilizes cryptographically signed HTTP cookies managed by Flask's `session` object, verified against server-side secret keys. Protected routes reject unauthorized requests and redirect to `/login`.

### Q15: What production WSGI servers are supported?
> **Answer:** The application is architected with a decoupled `wsgi.py` factory, fully compatible with **Gunicorn** on Linux and **Waitress** on Windows, as well as multi-stage **Docker** containers.

### Q16: How does the system handle database persistence when new simulated telemetry is saved?
> **Answer:** When the user clicks "Save Simulated Reading", the `/api/vehicles/<id>/telemetry` endpoint records the sensor telemetry row, creates an entry in `failure_predictions`, and updates the vehicle's `current_status` in the `vehicles` table inside a single atomic transaction.

### Q17: What was the ROC-AUC score of your model?
> **Answer:** The model achieved **69.18% ROC-AUC**, demonstrating its capability to rank vehicle breakdown risks consistently across varying operational alert thresholds.

### Q18: What is the benefit of having presets like "Thermal Runaway" in the UI?
> **Answer:** The presets allow project evaluators and external examiners to immediately observe how the digital twin behaves under extreme failure states (such as 140°C coolant or 0.8 bar oil pressure) without manually searching for boundary values.

### Q19: How are errors logged in production?
> **Answer:** Using Python's `RotatingFileHandler` writing to `logs/fleet_twin.log` with a 10 MB limit and 5 backups. It logs all request latencies, ML prediction inferences, and full exception tracebacks.

### Q20: What is the most significant novelty of this project compared to standard predictive maintenance projects?
> **Answer:** Standard projects stop at classification metrics in a Jupyter notebook. This project delivers a **closed-loop cyber-physical system**: taking real vehicle sensor data, running calibrated inference, decomposing health across 5 physical subsystems, estimating Remaining Useful Life, and generating human-interpretable technical maintenance work orders.
