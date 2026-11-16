"""
Predictive Maintenance Service.
Loads the trained ML model and feature scaler to perform real-time failure risk inference.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from flask import current_app

class FailurePredictor:
    """Predictive failure engine interface."""

    def __init__(self, model_path=None, scaler_path=None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.model_path = model_path or (base_dir / 'ml_pipeline' / 'saved_models' / 'model.pkl')
        self.scaler_path = scaler_path or (base_dir / 'ml_pipeline' / 'saved_models' / 'scaler.pkl')
        self.model = None
        self.scaler = None
        self.feature_cols = [
            'Engine rpm',
            'Lub oil pressure',
            'Fuel pressure',
            'Coolant pressure',
            'lub oil temp',
            'Coolant temp'
        ]
        self.load_model()

    def load_model(self):
        """Loads serialized model and scaler artifacts from disk."""
        try:
            if Path(self.model_path).exists() and Path(self.scaler_path).exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print(f"Loaded ML model from {self.model_path}")
            else:
                print(f"Warning: Model or scaler artifact not found at {self.model_path}")
        except Exception as e:
            print(f"Error loading ML artifacts: {e}")

    def predict(self, telemetry: dict) -> dict:
        """
        Runs failure risk estimation on incoming sensor telemetry dictionary.
        Accepts:
            - Engine rpm (or engine_rpm)
            - Lub oil pressure (or lub_oil_pressure / oil_pressure_psi)
            - Fuel pressure (or fuel_pressure)
            - Coolant pressure (or coolant_pressure)
            - lub oil temp (or lub_oil_temp / oil_temp)
            - Coolant temp (or coolant_temp / engine_temp_c)
        """
        if self.model is None or self.scaler is None:
            self.load_model()
            if self.model is None:
                return {
                    "error": "Model not loaded",
                    "failure_predicted": False,
                    "failure_risk_score": 0.0
                }

        # Extract features with sensible defaults if missing
        rpm = float(telemetry.get('Engine rpm', telemetry.get('engine_rpm', 750)))
        oil_pres = float(telemetry.get('Lub oil pressure', telemetry.get('oil_pressure', telemetry.get('oil_pressure_psi', 3.2))))
        fuel_pres = float(telemetry.get('Fuel pressure', telemetry.get('fuel_pressure', 6.5)))
        cool_pres = float(telemetry.get('Coolant pressure', telemetry.get('coolant_pressure', 2.3)))
        oil_temp = float(telemetry.get('lub oil temp', telemetry.get('oil_temp', 77.0)))
        cool_temp = float(telemetry.get('Coolant temp', telemetry.get('coolant_temp', telemetry.get('engine_temp_c', 78.0))))

        df_features = pd.DataFrame([{
            'Engine rpm': rpm,
            'Lub oil pressure': oil_pres,
            'Fuel pressure': fuel_pres,
            'Coolant pressure': cool_pres,
            'lub oil temp': oil_temp,
            'Coolant temp': cool_temp
        }])

        scaled_features = self.scaler.transform(df_features)
        prediction = int(self.model.predict(scaled_features)[0])
        probabilities = self.model.predict_proba(scaled_features)[0]
        failure_prob = float(probabilities[1])

        # Diagnostic component breakdown based on sensor deviations
        component = "None"
        severity = "LOW"
        action = "Routine monitoring; system operating within optimal thresholds."

        if failure_prob >= 0.75:
            severity = "CRITICAL"
        elif failure_prob >= 0.50:
            severity = "HIGH"
        elif failure_prob >= 0.35:
            severity = "MEDIUM"

        # Determine offending component
        if cool_temp > 95.0 or cool_pres < 1.0:
            component = "Engine Cooling Circuit"
            action = "Immediate coolant flush, check radiator fan and water pump pressure."
        elif oil_pres < 1.5 or oil_temp > 85.0:
            component = "Lubrication Subsystem"
            action = "Inspect oil pump, replace oil filter, inspect for bearing journal wear."
        elif fuel_pres > 12.0 or fuel_pres < 3.0:
            component = "Fuel Injection System"
            action = "Inspect fuel rail pressure regulator and fuel injection nozzles."
        elif rpm < 300 or rpm > 1800:
            component = "Transmission & Powertrain"
            action = "Check gearbox synchronization and idle RPM governor."
        elif failure_prob >= 0.50:
            component = "Engine Assembly"
            action = "Schedule preventive overhaul and sensor recalibration."

        return {
            "failure_predicted": bool(prediction == 1),
            "failure_risk_score": round(failure_prob, 4),
            "failure_risk_percentage": round(failure_prob * 100, 2),
            "severity": severity,
            "suspect_component": component,
            "recommended_action": action,
            "model_used": "Logistic Regression (Standardized Features)"
        }

# Global singleton instance
predictor = FailurePredictor()
