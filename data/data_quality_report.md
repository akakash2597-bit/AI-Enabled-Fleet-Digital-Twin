# Data Quality & Integrity Report: Automotive Vehicles Engine Health Dataset

**Dataset File:** `data/engine_data.csv`  
**Dataset Source:** Kaggle — Automotive Vehicles Engine Health Dataset  
**Domain:** Automotive Engineering & Predictive Maintenance  

---

## 1. Executive Summary
The selected dataset contains real-world telemetry readings from automotive internal combustion engines. It contains **19,535 records** across **7 numerical attributes**, including a binary target label `Engine Condition`. The dataset contains zero missing values and zero duplicate rows, providing a clean and robust baseline for machine learning models (Random Forest, Gradient Boosting, XGBoost, Logistic Regression, etc.).

---

## 2. Dataset Dimensions & Schema
- **Total Records (Rows):** 19,535
- **Total Features (Columns):** 7
- **File Format:** CSV (`.csv`)
- **Memory Footprint:** ~1.24 MB (in-memory ~1.04 MB)

| Column Name | Data Type | Physical Unit | Description | Min | Mean | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Engine rpm` | `int64` | RPM | Engine crankshaft rotational speed | 61 | 791.24 | 2,239 |
| `Lub oil pressure` | `float64` | bar / psi | Lubrication oil circulating pressure | 0.0034 | 3.30 | 7.27 |
| `Fuel pressure` | `float64` | bar / psi | Fuel injection line pressure | 0.0032 | 6.66 | 21.14 |
| `Coolant pressure` | `float64` | bar / psi | Cooling circuit hydraulic pressure | 0.0025 | 2.34 | 7.48 |
| `lub oil temp` | `float64` | °C | Lubrication oil operating temperature | 71.32 | 77.64 | 89.58 |
| `Coolant temp` | `float64` | °C | Engine coolant circulating temperature | 61.67 | 78.43 | 195.53 |
| `Engine Condition` | `int64` | Binary (0 / 1) | Target: 0 = Normal / Healthy, 1 = Fault / Maintenance Required | 0 | 0.63 | 1 |

---

## 3. Data Completeness & Quality Checks
- **Missing / Null Values:** `0` (0.00%) across all 7 columns.
- **Duplicate Records:** `0` (0.00%) duplicate rows.
- **Data Type Consistency:** 100% numerical (int64 and float64); no non-numerical artifacts or corrupt strings.
- **Class Balance:**
  - Class `1` (Maintenance Required / Faulty): **12,317** samples (63.05%)
  - Class `0` (Normal / Healthy): **7,218** samples (36.95%)
  - **Verdict:** Well-balanced target ratio (approx. 63:37); no extreme class imbalance requiring artificial resampling (SMOTE), though class-weight tuning can be applied.

---

## 4. Statistical Distribution & Sensor Anomaly Highlights
1. **Coolant Temperature Spikes:** The 75th percentile is 82.91°C, but the maximum reaches 195.53°C, indicating critical overheating conditions strongly associated with engine failure events.
2. **Engine RPM Range:** Mean RPM is ~791 RPM, spanning low idle speeds (~61 RPM) up to high revving loads (~2,239 RPM).
3. **Oil & Coolant Pressure Drops:** Minimum recorded values approach zero (0.0025 - 0.0034), simulating oil starvation and coolant line pressure drops, which are classic mechanical precursors to catastrophic engine seizure.
