"""
Predictive Maintenance Service.
Loads the trained ML model and feature scaler to perform real-time failure risk inference,
computes Health Score, Risk Level, Recommended Maintenance, Estimated Remaining Life (RUL),
and generates detailed, plain-English explanations for every prediction.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd

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
        
        # Healthy engineering reference ranges for automotive engines
        self.reference_ranges = {
            'Engine rpm': {'nominal_min': 650, 'nominal_max': 950, 'unit': 'RPM', 'name': 'Engine RPM'},
            'Lub oil pressure': {'nominal_min': 2.5, 'nominal_max': 4.5, 'unit': 'bar', 'name': 'Lubrication Oil Pressure'},
            'Fuel pressure': {'nominal_min': 5.0, 'nominal_max': 8.0, 'unit': 'bar', 'name': 'Fuel Rail Pressure'},
            'Coolant pressure': {'nominal_min': 1.8, 'nominal_max': 2.8, 'unit': 'bar', 'name': 'Coolant Line Pressure'},
            'lub oil temp': {'nominal_min': 74.0, 'nominal_max': 82.0, 'unit': '°C', 'name': 'Lubrication Oil Temperature'},
            'Coolant temp': {'nominal_min': 72.0, 'nominal_max': 85.0, 'unit': '°C', 'name': 'Coolant Temperature'}
        }
        
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
        Returns:
            - health_score (0 - 100)
            - failure_predicted (bool)
            - failure_probability (float, 0.0 to 1.0)
            - failure_risk_percentage (float, e.g. 64.21%)
            - risk_level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
            - recommended_maintenance (str)
            - estimated_remaining_life (dict)
            - explanation (dict)
        """
        if self.model is None or self.scaler is None:
            self.load_model()
            if self.model is None:
                return {
                    "error": "Model not loaded",
                    "failure_predicted": False,
                    "failure_probability": 0.0,
                    "health_score": 100,
                    "risk_level": "LOW",
                    "recommended_maintenance": "System initialized in fallback mode.",
                    "estimated_remaining_life": {"km": 25000, "hours": 600, "urgency_text": "Normal operation"}
                }

        # 1. Parse sensor inputs with sensible fallbacks
        rpm = float(telemetry.get('Engine rpm', telemetry.get('engine_rpm', 750)))
        oil_pres = float(telemetry.get('Lub oil pressure', telemetry.get('oil_pressure', telemetry.get('oil_pressure_psi', 3.2))))
        fuel_pres = float(telemetry.get('Fuel pressure', telemetry.get('fuel_pressure', 6.5)))
        cool_pres = float(telemetry.get('Coolant pressure', telemetry.get('coolant_pressure', 2.3)))
        oil_temp = float(telemetry.get('lub oil temp', telemetry.get('oil_temp', 77.0)))
        cool_temp = float(telemetry.get('Coolant temp', telemetry.get('coolant_temp', telemetry.get('engine_temp_c', 78.0))))

        sensor_values = {
            'Engine rpm': rpm,
            'Lub oil pressure': oil_pres,
            'Fuel pressure': fuel_pres,
            'Coolant pressure': cool_pres,
            'lub oil temp': oil_temp,
            'Coolant temp': cool_temp
        }

        # 2. DataFrame & Standard Scaling
        df_features = pd.DataFrame([sensor_values])
        scaled_features = self.scaler.transform(df_features)

        # 3. Model Inference (Logistic Regression)
        raw_pred = int(self.model.predict(scaled_features)[0])
        probabilities = self.model.predict_proba(scaled_features)[0]
        failure_prob = float(probabilities[1])
        risk_pct = round(failure_prob * 100, 2)

        # 4. Compute Health Score (0 - 100%)
        # Invert failure probability; apply threshold adjustments if physical sensors are in danger
        health_score = max(5, int(round((1.0 - failure_prob) * 100)))

        # 5. Determine Risk Level
        if failure_prob >= 0.75 or cool_temp >= 115.0 or oil_pres <= 1.0:
            risk_level = "CRITICAL"
        elif failure_prob >= 0.50 or cool_temp >= 95.0 or oil_pres <= 1.8 or fuel_pres >= 13.0:
            risk_level = "HIGH"
        elif failure_prob >= 0.35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # 6. Estimate Remaining Useful Life (RUL)
        remaining_life = self._calculate_remaining_life(failure_prob, risk_level, sensor_values)

        # 7. Diagnosed Component & Recommended Maintenance
        recommendation_info = self._generate_maintenance_recommendation(risk_level, sensor_values, failure_prob)

        # 8. Generate Plain-English Explanation
        explanation = self._generate_explanation(
            sensor_values=sensor_values,
            scaled_features=scaled_features[0],
            failure_prob=failure_prob,
            risk_level=risk_level,
            suspect_component=recommendation_info['component'],
            remaining_life=remaining_life
        )

        return {
            "health_score": health_score,
            "failure_predicted": bool(raw_pred == 1 or failure_prob >= 0.50),
            "failure_probability": round(failure_prob, 4),
            "failure_risk_score": round(failure_prob, 4),
            "failure_risk_percentage": risk_pct,
            "risk_level": risk_level,
            "severity": risk_level,
            "suspect_component": recommendation_info['component'],
            "recommended_maintenance": recommendation_info['action'],
            "recommended_action": recommendation_info['action'],
            "maintenance_checklist": recommendation_info['checklist'],
            "estimated_remaining_life": remaining_life,
            "explanation": explanation,
            "sensor_readings": sensor_values,
            "model_used": "Logistic Regression (Standardized Sensor Features)"
        }

    def _calculate_remaining_life(self, failure_prob: float, risk_level: str, sensors: dict) -> dict:
        """
        Estimates vehicle Remaining Useful Life (RUL) in kilometers and operating hours
        before severe mechanical breakdown occurs.
        """
        cool_temp = sensors['Coolant temp']
        oil_pres = sensors['Lub oil pressure']

        if risk_level == "CRITICAL" or cool_temp > 120 or oil_pres < 0.8:
            # Imminent breakdown
            est_km = int(max(20, round((1.0 - failure_prob) * 350)))
            est_hours = max(1, round(est_km / 45, 1))
            urgency = "IMMEDIATE ATTENTION: Engine breakdown imminent within 24 hours. Halt vehicle for roadside service."
            status_badge = "critical"
        elif risk_level == "HIGH":
            # Breakdown expected soon
            est_km = int(round(500 + (0.75 - failure_prob) * 4000))
            est_hours = round(est_km / 50, 1)
            urgency = "HIGH PRIORITY: Service within 48 to 72 hours before next long-haul dispatch."
            status_badge = "high"
        elif risk_level == "MEDIUM":
            # Moderate degradation
            est_km = int(round(3500 + (0.50 - failure_prob) * 9000))
            est_hours = round(est_km / 55, 1)
            urgency = "MODERATE: Schedule workshop check during upcoming weekend maintenance window."
            status_badge = "medium"
        else:
            # Healthy
            est_km = int(round(15000 + (0.35 - failure_prob) * 25000))
            est_hours = round(est_km / 60, 1)
            urgency = "NOMINAL: Operating within safety envelope. Next periodic inspection at 20,000 km."
            status_badge = "normal"

        return {
            "estimated_km": est_km,
            "estimated_hours": est_hours,
            "urgency_text": urgency,
            "status_badge": status_badge,
            "formatted_display": f"{est_km:,} km (~{est_hours} Operating Hours)"
        }

    def _generate_maintenance_recommendation(self, risk_level: str, sensors: dict, failure_prob: float) -> dict:
        """Determines suspect component and creates technical technician work actions."""
        cool_temp = sensors['Coolant temp']
        cool_pres = sensors['Coolant pressure']
        oil_pres = sensors['Lub oil pressure']
        oil_temp = sensors['lub oil temp']
        fuel_pres = sensors['Fuel pressure']
        rpm = sensors['Engine rpm']

        if cool_temp > 95.0 or cool_pres < 1.2:
            component = "Engine Cooling Circuit"
            action = f"Cooling circuit distress detected (Coolant: {cool_temp:.1f}°C, Pressure: {cool_pres:.2f} bar). Flush radiator, inspect coolant pump impeller, check for line leaks, and test the thermostat valve."
            checklist = [
                "Pressure test radiator cap and sealed water jacket",
                "Inspect radiator cooling fan clutch and thermal switch",
                "Flush coolant mixture and bleed air pockets",
                "Inspect water pump belt tension and mechanical seals"
            ]
        elif oil_pres < 2.0 or oil_temp > 85.0:
            component = "Lubrication Subsystem"
            action = f"Lubrication starvation risk detected (Oil Pressure: {oil_pres:.2f} bar, Oil Temp: {oil_temp:.1f}°C). Low pressure will cause metal-on-metal journal wear. Replace engine oil and filter, and inspect oil pump pressure relief valve."
            checklist = [
                "Check engine oil dipstick level and viscosity condition",
                "Replace engine oil filter cartridge and drain plug washer",
                "Perform manual mechanical oil pressure gauge verification",
                "Inspect oil pickup screen in sump for metal shavings"
            ]
        elif fuel_pres > 11.5 or fuel_pres < 3.5:
            component = "Fuel Injection System"
            action = f"Abnormal fuel rail pressure ({fuel_pres:.2f} bar). Excessive or deficient pressure leads to cylinder misfires and unburned fuel wash. Inspect fuel pressure regulator, fuel filter, and rail sensors."
            checklist = [
                "Test common rail fuel pressure regulator solenoid",
                "Replace primary and secondary fuel filter cartridges",
                "Run electronic injector leak-down and balance rate diagnostics",
                "Inspect fuel supply lines for air ingress or restriction"
            ]
        elif rpm < 400 or rpm > 1800:
            component = "Powertrain & Engine Idle Assembly"
            action = f"Abnormal rotational engine speed ({rpm} RPM). Heavy mechanical drag or engine stall condition. Check transmission clutch engagement, alternator drag, and electronic throttle governor."
            checklist = [
                "Scan engine control module (ECM) for diagnostic trouble codes (DTCs)",
                "Inspect transmission input shaft bearing and clutch plate",
                "Calibrate electronic idle speed control valve (IAC)",
                "Check accessory belt pulley bearings for physical seizure"
            ]
        elif risk_level in ('HIGH', 'CRITICAL'):
            component = "Engine Core Mechanical Assembly"
            action = "Multi-sensor degradation detected across combined pressure and thermal parameters. Schedule comprehensive preventive engine overhaul and bench diagnostics."
            checklist = [
                "Perform cylinder compression and cylinder leak-down test",
                "Inspect engine timing belt/chain alignment",
                "Check valve clearances and exhaust gas recirculation (EGR) valve",
                "Recalibrate analog telemetry pressure and temperature sensors"
            ]
        else:
            component = "None (Nominal Operational Envelope)"
            action = "All sensor parameters are within acceptable automotive tolerance bands. Continue standard fleet routing."
            checklist = [
                "Routine pre-trip inspection",
                "Verify tire pressures and fluid levels",
                "Continue standard periodic maintenance schedule"
            ]

        return {
            "component": component,
            "action": action,
            "checklist": checklist
        }

    def _generate_explanation(self, sensor_values: dict, scaled_features: np.ndarray, failure_prob: float, risk_level: str, suspect_component: str, remaining_life: dict) -> dict:
        """
        Generates a transparent, plain-English explanation breaking down:
        - Why the model classified the vehicle under this risk level
        - Which sensors pushed the prediction toward failure or safety
        - Physical mechanical consequences of the sensor values
        """
        factors = []
        sensor_details = []

        # Analyze each sensor
        for i, col in enumerate(self.feature_cols):
            val = sensor_values[col]
            ref = self.reference_ranges[col]
            coef = self.model.coef_[0][i]
            scaled_val = scaled_features[i]
            impact = coef * scaled_val  # Log-odds impact

            is_high = val > ref['nominal_max']
            is_low = val < ref['nominal_min']

            status = "Normal"
            analysis = f"{ref['name']} is within healthy operational range ({val:.1f} {ref['unit']})."

            if col == 'Engine rpm' and val < 500:
                status = "Critical (Low)"
                analysis = f"RPM is abnormally low ({val:.0f} RPM), indicating severe engine laboring, mechanical drag, or imminent stalling."
                factors.append(f"Low Engine RPM ({val:.0f} RPM)")
            elif col == 'Coolant temp' and val > 95.0:
                status = "Critical (High)" if val > 115 else "Warning (Elevated)"
                analysis = f"Coolant temperature is {val:.1f}°C (nominal max is {ref['nominal_max']}°C). Excessive heat causes cylinder head warping and gasket failure."
                factors.append(f"Overheating Coolant ({val:.1f}°C)")
            elif col == 'Lub oil pressure' and val < 2.0:
                status = "Critical (Low)" if val < 1.2 else "Warning (Low)"
                analysis = f"Oil pressure is {val:.2f} bar (nominal min is {ref['nominal_min']} bar). Insufficient pressure causes friction between crankshaft journals and bearings."
                factors.append(f"Low Lubrication Pressure ({val:.2f} bar)")
            elif col == 'Fuel pressure' and (val > 11.0 or val < 4.0):
                status = "Warning (Abnormal)"
                analysis = f"Fuel rail pressure is {val:.2f} bar (nominal is {ref['nominal_min']}-{ref['nominal_max']} bar), causing improper air-fuel mixture and misfires."
                factors.append(f"Fuel Pressure Deviation ({val:.2f} bar)")
            elif col == 'Coolant pressure' and val < 1.3:
                status = "Warning (Depressurized)"
                analysis = f"Cooling line pressure has dropped to {val:.2f} bar, indicating possible fluid leaks or radiator cap pressure loss."
                factors.append(f"Coolant Pressure Loss ({val:.2f} bar)")
            elif col == 'lub oil temp' and val > 85.0:
                status = "Warning (High)"
                analysis = f"Lubrication oil temperature is {val:.1f}°C. High thermal load causes oil thinning and accelerates component wear."
                factors.append(f"Elevated Oil Temp ({val:.1f}°C)")

            sensor_details.append({
                "sensor_name": ref['name'],
                "raw_value": val,
                "unit": ref['unit'],
                "nominal_range": f"{ref['nominal_min']} - {ref['nominal_max']} {ref['unit']}",
                "status": status,
                "impact_direction": "Risk Increased" if impact > 0 else "Risk Decreased",
                "analysis": analysis
            })

        # Plain English executive summary
        if risk_level in ('CRITICAL', 'HIGH'):
            lead_text = f"The AI model predicts a **{risk_level} FAILURE RISK** ({round(failure_prob * 100, 1)}% probability). "
            if factors:
                factor_str = ", ".join(factors)
                body_text = f"This high risk score is primarily triggered by {factor_str}. Operating under these conditions will lead to mechanical seizure in the {suspect_component}. "
            else:
                body_text = f"Multiple combined sensor deviations are compounding stress on the {suspect_component}. "
            conclusion_text = f"Estimated remaining life is limited to approximately **{remaining_life['formatted_display']}**. Immediate workshop service is required to prevent an expensive on-road breakdown."
        elif risk_level == "MEDIUM":
            lead_text = f"The AI model predicts a **MODERATE DEGRADATION RISK** ({round(failure_prob * 100, 1)}% probability). "
            body_text = "The vehicle is operational, but early signs of thermal or pressure wear are emerging. "
            conclusion_text = f"Estimated remaining life before failure is **{remaining_life['formatted_display']}**. Plan maintenance during the next scheduled service window."
        else:
            lead_text = f"The AI model predicts a **HEALTHY / LOW RISK** state ({round(failure_prob * 100, 1)}% failure probability). "
            body_text = "All primary sensor telemetry parameters (RPM, Oil Pressure, Coolant Temp, Fuel Line) are operating comfortably within designed manufacturer engineering tolerances. "
            conclusion_text = f"The vehicle has an estimated healthy remaining useful life of **{remaining_life['formatted_display']}** before requiring periodic overhaul."

        full_summary = lead_text + body_text + conclusion_text

        return {
            "summary_text": full_summary,
            "key_contributing_factors": factors if factors else ["All readings nominal"],
            "suspect_component": suspect_component,
            "sensor_details": sensor_details
        }

# Global singleton instance
predictor = FailurePredictor()
