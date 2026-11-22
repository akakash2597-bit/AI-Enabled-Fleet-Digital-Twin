# REST API Documentation
## AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

The Fleet Digital Twin platform exposes a high-throughput, structured REST API for edge IoT devices, commercial vehicle ECUs, and dispatch dashboards.

---

## 🌐 Base URL
```text
http://<host>:<port>/api
```

All requests containing JSON bodies must include the header:
```http
Content-Type: application/json
```

---

## 📑 Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/fleet/summary` | High-level fleet metrics (Operational, Warning, Critical counts, Health score). |
| `GET` | `/api/vehicles` | List all registered vehicles and their latest twin states. |
| `GET` | `/api/vehicles/<vehicle_id>` | Detailed metadata and latest prediction for a single vehicle. |
| `GET` | `/api/vehicles/<vehicle_id>/telemetry` | Time-series historical sensor telemetry logs for charting. |
| `GET` | `/api/digital-twin/<vehicle_id>` | Real-time subsystem health decomposition (Engine, Cooling, Lubrication, etc.). |
| `POST`| `/api/predict` | Executes Scikit-learn failure inference on raw sensor readings. |
| `POST`| `/api/vehicles/<vehicle_id>/telemetry` | Ingests real-time telemetry from ECU, updates twin, and persists to database. |

---

## 📌 Endpoint Details

### 1. Run Machine Learning Failure Prediction
Executes predictive failure analysis on incoming sensor readings.

- **URL:** `/api/predict`
- **Method:** `POST`
- **Request Headers:** `Content-Type: application/json`

#### Request Body Example:
```json
{
  "Engine rpm": 780,
  "Coolant temp": 128.5,
  "Lub oil pressure": 1.2,
  "lub oil temp": 89.0,
  "Fuel pressure": 7.2,
  "Coolant pressure": 0.85
}
```

#### Response Body Example (`200 OK`):
```json
{
  "status": "success",
  "prediction": {
    "health_score": 28,
    "failure_predicted": true,
    "failure_probability": 0.7245,
    "failure_risk_percentage": 72.45,
    "risk_level": "CRITICAL",
    "suspect_component": "Engine Cooling Circuit",
    "recommended_maintenance": "Cooling circuit distress detected (Coolant: 128.5°C, Pressure: 0.85 bar). Flush radiator, inspect coolant pump impeller, check for line leaks, and test the thermostat valve.",
    "maintenance_checklist": [
      "Pressure test radiator cap and sealed water jacket",
      "Inspect radiator cooling fan clutch and thermal switch",
      "Flush coolant mixture and bleed air pockets",
      "Inspect water pump belt tension and mechanical seals"
    ],
    "estimated_remaining_life": {
      "estimated_km": 96,
      "estimated_hours": 2.1,
      "formatted_display": "96 km (~2.1 Operating Hours)",
      "status_badge": "critical",
      "urgency_text": "IMMEDIATE ATTENTION: Engine breakdown imminent within 24 hours. Halt vehicle for roadside service."
    },
    "explanation": {
      "summary_text": "The AI model predicts a CRITICAL FAILURE RISK (72.5% probability). This high risk score is primarily triggered by Overheating Coolant (128.5°C), Coolant Pressure Loss (0.85 bar), Low Lubrication Pressure (1.20 bar). Operating under these conditions will lead to mechanical seizure in the Engine Cooling Circuit. Estimated remaining life is limited to approximately 96 km (~2.1 Operating Hours). Immediate workshop service is required to prevent an expensive on-road breakdown.",
      "key_contributing_factors": [
        "Overheating Coolant (128.5°C)",
        "Coolant Pressure Loss (0.85 bar)",
        "Low Lubrication Pressure (1.20 bar)"
      ],
      "sensor_details": [
        {
          "analysis": "Coolant temperature is 128.5°C (nominal max is 85.0°C). Excessive heat causes cylinder head warping and gasket failure.",
          "impact_direction": "Risk Increased",
          "nominal_range": "72.0 - 85.0 °C",
          "raw_value": 128.5,
          "sensor_name": "Coolant Temperature",
          "status": "Critical (High)",
          "unit": "°C"
        }
      ]
    },
    "model_used": "Logistic Regression (Standardized Sensor Features)"
  },
  "digital_twin": {
    "vehicle_id": "SIMULATED-VEHICLE",
    "overall_health_score": 28,
    "failure_risk_percentage": 72.5,
    "subsystems": {
      "cooling_system": { "health": 35, "status": "Critical", "name": "Cooling Circuit & Radiator" },
      "lubrication_system": { "health": 34, "status": "Critical", "name": "Lubrication & Oil Pump" },
      "engine_assembly": { "health": 44, "status": "Critical", "name": "Engine Core & Cylinders" },
      "fuel_injection": { "health": 100, "status": "Optimal", "name": "Fuel Delivery & Injectors" },
      "transmission": { "health": 95, "status": "Optimal", "name": "Gearbox & Powertrain" }
    }
  }
}
```

---

### 2. Retrieve Fleet Health Summary
- **URL:** `/api/fleet/summary`
- **Method:** `GET`

#### Response (`200 OK`):
```json
{
  "status": "success",
  "data": {
    "total_vehicles": 6,
    "operational_count": 4,
    "warning_count": 1,
    "critical_count": 1,
    "avg_health_score": 81.3,
    "active_alerts": 2
  }
}
```

---

### 3. Ingest Live Telemetry Stream
Ingests a single observation from a physical vehicle's onboard telematics unit, triggers predictive inference, and writes both to the database.

- **URL:** `/api/vehicles/<vehicle_id>/telemetry`
- **Method:** `POST`

#### Request Example:
```bash
curl -X POST http://localhost:5000/api/vehicles/VH-101/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "Engine rpm": 810,
    "Coolant temp": 78.4,
    "Lub oil pressure": 3.45,
    "lub oil temp": 77.2,
    "Fuel pressure": 6.3,
    "Coolant pressure": 2.35,
    "speed": 64.5
  }'
```

#### Response (`200 OK`):
```json
{
  "status": "success",
  "message": "Telemetry ingested for vehicle VH-101.",
  "prediction": {
    "health_score": 93,
    "risk_level": "LOW",
    "failure_probability": 0.068
  }
}
```

---

### 4. Error Responses
All API error responses adhere to standard HTTP status codes:

#### Example `400 Bad Request`:
```json
{
  "status": "error",
  "code": 400,
  "message": "Sensor value for 'Coolant temp' must be numeric (received: 'invalid_string')."
}
```

#### Example `404 Not Found`:
```json
{
  "status": "error",
  "code": 404,
  "message": "Vehicle VH-999 not found in fleet registry."
}
```
