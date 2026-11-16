# Comprehensive Exploratory Data Analysis (EDA) Report
## AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

**Author:** Antigravity AI  
**Project:** Final Year B.Tech (AI & DS)  
**Dataset:** Automotive Vehicles Engine Health Dataset (`data/engine_data.csv`)  
**Sample Size:** 19,535 records | 7 features  

---

## 1. Executive Summary
This report presents an exhaustive Exploratory Data Analysis (EDA) on 19,535 vehicle engine telemetry records. The primary objective is to inspect data distribution, identify sensor degradation boundaries, assess target balance, evaluate inter-feature multicollinearity, and establish feature importance rankings before deploying machine learning classification algorithms.

---

## 2. Dataset Overview & Schema

| # | Attribute | Type | Physical Measurement | Real-World Vehicle Function |
|---|---|---|---|---|
| 1 | `Engine rpm` | Integer | Rotations per minute (RPM) | Engine crankshaft rotational velocity |
| 2 | `Lub oil pressure` | Continuous | bar / psi | Lubricating oil circulation pressure |
| 3 | `Fuel pressure` | Continuous | bar / psi | Fuel rail injection hydraulic pressure |
| 4 | `Coolant pressure`| Continuous | bar / psi | Sealed cooling jacket pressure |
| 5 | `lub oil temp` | Continuous | °C | Lubricating fluid thermal condition |
| 6 | `Coolant temp` | Continuous | °C | Engine block coolant fluid temperature |
| 7 | `Engine Condition`| Binary | 0 or 1 | Target: 0 = Normal / Healthy, 1 = Fault / Maintenance Required |

---

## 3. Data Integrity & Completeness Audit
- **Total Records:** 19,535
- **Missing / Null Values:** **0** (0.00% across all columns)
- **Duplicate Rows:** **0** (0.00%)
- **Data Types:** 100% numerical (int64 and float64); zero encoding or imputation required.

---

## 4. Summary Statistics

| Statistic | Engine rpm | Lub oil pressure | Fuel pressure | Coolant pressure | lub oil temp (°C) | Coolant temp (°C) | Engine Condition |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Count** | 19,535 | 19,535 | 19,535 | 19,535 | 19,535 | 19,535 | 19,535 |
| **Mean** | 791.24 | 3.30 | 6.66 | 2.34 | 77.64 | 78.43 | 0.63 |
| **Std Dev** | 267.61 | 1.02 | 2.76 | 1.04 | 3.11 | 6.21 | 0.48 |
| **Min** | 61.00 | 0.0034 | 0.0032 | 0.0025 | 71.32 | 61.67 | 0.00 |
| **25% (Q1)** | 593.00 | 2.52 | 4.92 | 1.60 | 75.73 | 73.90 | 0.00 |
| **50% (Median)**| 746.00 | 3.16 | 6.20 | 2.17 | 76.82 | 78.35 | 1.00 |
| **75% (Q3)** | 934.00 | 4.06 | 7.74 | 2.85 | 78.07 | 82.92 | 1.00 |
| **Max** | 2,239.00 | 7.27 | 21.14 | 7.48 | 89.58 | 195.53 | 1.00 |

---

## 5. Visual Chart Analysis & Explanations

### Chart 1: Failure Distribution & Class Imbalance Analysis
- **Saved Figure:** `reports/eda_figures/class_imbalance.png`
- **Findings:**
  - **Class 1 (Fault / Maintenance Needed):** 12,317 instances (**63.05%**)
  - **Class 0 (Normal / Operational):** 7,218 instances (**36.95%**)
- **Simple Explanation:**  
  The dataset has a natural 63:37 ratio. While fault conditions outnumber healthy conditions slightly, the minority class (healthy vehicles) still accounts for over one-third of all samples. This represents a healthy, moderately balanced distribution for machine learning. Standard accuracy alone will not be misleading, but computing Precision, Recall, F1-Score, and ROC-AUC is recommended.

---

### Chart 2: Correlation Matrix Heatmap
- **Saved Figure:** `reports/eda_figures/correlation_matrix.png`
- **Findings:**
  - `Engine rpm` exhibits the strongest linear correlation with `Engine Condition` ($r = -0.27$).
  - `Fuel pressure` has a positive correlation ($r = +0.12$).
  - `Lub oil pressure` has a modest positive correlation ($r = +0.06$).
  - Inter-feature correlations among the sensor features are low to moderate ($|r| < 0.35$), confirming that the features do **not** suffer from severe multicollinearity.
- **Simple Explanation:**  
  No single sensor alone reveals engine breakdown. The low linear correlation coefficients demonstrate that engine failures are **multi-variate and non-linear**—a combination of temperature spikes, pressure drops, and RPM fluctuations together trigger a failure. This proves that complex non-linear machine learning models (like Random Forests, Gradient Boosted Trees, or Neural Networks) are essential.

---

### Chart 3: Sensor Feature Histograms & Density Curves
- **Saved Figure:** `reports/eda_figures/histograms.png`
- **Findings:**
  - `Engine rpm` is right-skewed with a peak around 650–850 RPM (idle/cruising speeds). Under fault conditions (`Engine Condition == 1`), there is a significant cluster of low-RPM records, indicating engine bogging or stalling.
  - `Coolant temp` shows a tight bell curve centered at ~78°C, with a long right tail stretching up to ~195°C during severe overheating anomalies.
  - `Lub oil temp` has a concentrated distribution between 74°C and 82°C.
  - `Fuel pressure` and `Coolant pressure` exhibit moderate positive skewness.
- **Simple Explanation:**  
  Healthy engines operate within narrow, predictable bell curves. When an engine develops a fault, its sensor values drift significantly into the outer tails (very low RPMs or extreme temperature spikes).

---

### Chart 4: Boxplots & Outlier Breakdown
- **Saved Figure:** `reports/eda_figures/boxplots.png`
- **Findings:**
  - `Coolant temp` exhibits prominent upper outliers extending past 100°C up to 195.5°C in the failure class, representing critical cooling failure events.
  - `Fuel pressure` reaches up to 21.14 bar under failure conditions (compared to the median of 6.2 bar), indicating fuel pressure regulator failure or line blockage.
  - `Lub oil pressure` shows values approaching zero (< 0.005 bar), representing loss of lubrication pressure.
- **Simple Explanation:**  
  Boxplots highlight the "normal spread" (the central box) versus extreme anomalies (dots beyond whiskers). For a predictive maintenance digital twin, these outliers are not noise or data errors—they represent genuine catastrophic failure events that our ML model must detect.

---

### Chart 5: Feature Importance Suggestions
- **Saved Figure:** `reports/eda_figures/feature_importance.png`
- **Rankings (Random Forest Gini Impurity):**
  1. **`Engine rpm`**: **22.15%**
  2. **`Fuel pressure`**: **16.60%**
  3. **`lub oil temp`**: **15.95%**
  4. **`Lub oil pressure`**: **15.47%**
  5. **`Coolant pressure`**: **15.01%**
  6. **`Coolant temp`**: **14.82%**
- **Simple Explanation:**  
  All six sensor parameters contribute substantially (each between 14.8% and 22.2%) to predicting engine breakdown. `Engine rpm` is the leading predictor, followed by `Fuel pressure` and thermal attributes. Because every feature has meaningful predictive power, **all 6 sensor features should be retained** without dropping any.

---

### Chart 6: Thermal Anomaly Scatter (Coolant Temp vs Lub Oil Temp)
- **Saved Figure:** `reports/eda_figures/thermal_anomaly_scatter.png`
- **Findings:**
  - Healthy engines (`0`) remain tightly clustered in the thermal safety zone (72°C–84°C oil, 65°C–88°C coolant).
  - Faulty engines (`1`) scatter into extreme thermal envelopes, particularly vertical columns where coolant temperature exceeds 100°C–180°C while oil temperature tries to compensate.
- **Simple Explanation:**  
  When an engine's cooling system fails, coolant temperature spikes drastically before the oil temperature can stabilize, providing a strong visual signature for the Digital Twin's thermal monitoring gauge.

---

## 6. Recommendations for Machine Learning Pipeline
1. **Feature Scaling:** Since features span different units (RPM ~ 700 vs Pressure ~ 3 bar vs Temp ~ 80°C), apply `StandardScaler` or `RobustScaler` (to handle temperature spikes).
2. **Model Selection:** Tree-based ensemble models (`RandomForestClassifier`, `GradientBoostingClassifier`, `XGBoost`) are ideal due to the non-linear multi-sensor degradation dynamics.
3. **Evaluation Metric:** Use ROC-AUC, Precision, Recall, and F1-Score alongside Confusion Matrix, prioritizing high Recall to avoid undetected vehicle breakdowns (False Negatives).
