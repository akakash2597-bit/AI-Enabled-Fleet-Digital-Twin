# System Architecture & Technical Specification
## AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

---

## 1. Architectural Philosophy: The Cyber-Physical Twin

A **Digital Twin** is defined as an active virtual representation of a physical asset, synchronized in real time via bidirectional or continuous telemetry streams. In heavy automotive fleet management, traditional maintenance follows either **reactive repair** (repairing after roadside breakdown) or **preventive maintenance** (periodic servicing based on elapsed time or odometer reading, regardless of actual wear).

This project implements **Prescriptive Cyber-Physical Maintenance**:
1. Continuous physical sensor streams measure engine rotational speed, thermal state, and fluid pressures.
2. A trained Scikit-learn statistical model estimates failure probability before components fracture or seize.
3. An internal state engine updates virtual subsystem models (Engine Core, Cooling Circuit, Lubrication, Fuel Injection, Transmission).
4. Automated prescriptive repair orders and Remaining Useful Life (RUL) projections are dispatched to workshop managers.

---

## 2. High-Level System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER 1: PHYSICAL VEHICLE ASSETS                     │
│  [ Commercial Heavy Haulage Fleets (Tata, Ashok Leyland, BharatBenz) ] │
│  Sensors: RPM, Coolant Temp, Oil Pressure, Oil Temp, Fuel Pres, etc.   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Edge CAN Bus / IoT Telemetry (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  LAYER 2: INGESTION & REST GATEWAY                     │
│  Flask REST Ingestion Endpoints (/api/predict, /api/vehicles/telemetry)│
│  Input Validation, Type Coercion, Audit Logging                        │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       LAYER 3: ML INFERENCE          │  │ LAYER 4: STATE SYNCHRONY     │
│  • StandardScaler (scaler.pkl)       │  │  • Digital Twin State Engine │
│  • Logistic Regression (model.pkl)   │  │  • 5 Subsystems Health Model │
│  • Failure Probability & Risk Triage │  │  • RUL Projection Engine     │
└───────────────────┬──────────────────┘  └──────────────┬───────────────┘
                    │                                    │
                    └─────────────────┬──────────────────┘
                                      │ Synchronized State
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                LAYER 5: DATA PERSISTENCE & STORAGE                     │
│  SQLite3 ACID Relational Database (fleet_data.db)                      │
│  Tables: vehicles, sensor_telemetry, failure_predictions, maintenance  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Real-Time Queries
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  LAYER 6: PRESENTATION & USER EXPERIENCE               │
│  • Responsive Operations Dashboard (Chart.js Health Donut & Trends)    │
│  • Interactive 2D Digital Twin Virtualizer (Live Telemetry Simulator)   │
│  • Prescriptive Maintenance Dispatch & Work Orders                     │
│  • Admin Security & Authentication Session Management                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical Foundations of the Predictive Core

### 3.1 Feature Standardization (Z-Score Normalization)
Automotive sensor telemetry spans wildly disparate physical units and dynamic ranges (RPM ~ 700, Oil Pressure ~ 3 bar, Coolant Temp ~ 80°C). Prior to classification, input vector $\mathbf{x} \in \mathbb{R}^6$ is normalized using parameter-wise sample means $\mu_j$ and standard deviations $\sigma_j$:

$$z_j = \frac{x_j - \mu_j}{\sigma_j}$$

Where:
$$\mu = [791.24, 3.30, 6.66, 2.34, 77.64, 78.43]$$
$$\sigma = [267.61, 1.02, 2.76, 1.04, 3.11, 6.21]$$

### 3.2 Probabilistic Failure Classification
Failure risk is evaluated via a logistic sigmoid transformation over normalized log-odds:

$$P(\text{Failure} \mid \mathbf{z}) = \sigma(\mathbf{w}^T \mathbf{z} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{z} + b)}}$$

Where model weights $\mathbf{w}$ and bias $b$ were optimized via Maximum Likelihood Estimation on 15,628 training samples:
- $b = +0.5814$
- $w_{\text{RPM}} = -0.5804$ (negative correlation: lower RPM under load signifies stalling/mechanical drag)
- $w_{\text{Fuel Pres}} = +0.2737$
- $w_{\text{Oil Pres}} = +0.1297$
- $w_{\text{Oil Temp}} = -0.1640$
- $w_{\text{Coolant Pres}} = -0.0679$
- $w_{\text{Coolant Temp}} = -0.0555$

### 3.3 Health Score Formulation
Overall digital twin health $H \in [5, 100]$ represents the inverted risk metric adjusted for critical sensor boundaries:

$$H = \max\left(5, \text{round}\left((1.0 - P(\text{Failure})) \times 100\right)\right)$$

### 3.4 Remaining Useful Life (RUL) Modeling
RUL estimates the operational distance (km) and operating hours before mechanical breakdown:
- For **CRITICAL** risk ($P \ge 0.75$):
  $$\text{RUL}_{\text{km}} = \max\left(20, \text{round}\left((1.0 - P) \times 350\right)\right)$$
- For **HIGH** risk ($0.50 \le P < 0.75$):
  $$\text{RUL}_{\text{km}} = \text{round}\left(500 + (0.75 - P) \times 4000\right)$$
- For **MEDIUM** risk ($0.35 \le P < 0.50$):
  $$\text{RUL}_{\text{km}} = \text{round}\left(3500 + (0.50 - P) \times 9000\right)$$
- For **LOW** risk ($P < 0.35$):
  $$\text{RUL}_{\text{km}} = \text{round}\left(15000 + (0.35 - P) \times 25000\right)$$

$$\text{RUL}_{\text{hours}} = \frac{\text{RUL}_{\text{km}}}{\bar{v}_{\text{avg}}}$$

---

## 4. Subsystem Decomposition & State Engine

The virtual vehicle is modeled across five distinct mechanical subsystems:
1. **Engine Core Assembly**: Evaluates RPM consistency and compound thermal stress.
2. **Cooling Circuit**: Evaluates coolant temperature against thermal runaway ($> 95^\circ\text{C}$) and pressure drops ($< 1.2\text{ bar}$).
3. **Lubrication Subsystem**: Monitors hydraulic oil pressure ($< 2.0\text{ bar}$ flags starvation) and oil degradation temperature ($> 85^\circ\text{C}$).
4. **Fuel Delivery System**: Tracks common rail pressure spikes ($> 11.5\text{ bar}$) or fuel starvation ($< 3.5\text{ bar}$).
5. **Transmission System**: Monitors rotational drag and gearbox synchronization.

---

## 5. Persistence & Schema Design

SQLite relational store provides zero-latency local caching and transactional ACID compliance:
- `vehicles`: Fleet metadata, model, license plate, operational state.
- `sensor_telemetry`: High-frequency sensor log entries with foreign key cascade to `vehicles`.
- `failure_predictions`: Machine learning inference outputs, component diagnoses, and resolution tracking.
- `maintenance_logs`: Dispatched work orders, scheduled dates, and technician work notes.

---

## 6. Security & Session Management

- **Authentication**: Session cookie encryption utilizing `SECRET_KEY`.
- **Role-Based Access Control**: Restricts administrative actions (adding/deleting vehicles, scheduling work orders) behind session validation.
- **Input Sanitization**: All incoming telemetry is type-checked and bounded before execution.
- **Audit Logging**: Production logging captures all requests, prediction outcomes, and exceptions with rotating file handlers in `logs/fleet_twin.log`.
