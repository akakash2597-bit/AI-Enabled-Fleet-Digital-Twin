"""
Digital Twin Service.
Maintains the virtual representation, subsystem states, and real-time synchrony
for each connected fleet vehicle.
"""

from app.services.predictor import predictor

class VehicleDigitalTwin:
    """Virtual representation of a physical fleet vehicle."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    def compute_twin_state(self, telemetry: dict) -> dict:
        """
        Calculates cyber-physical subsystem health metrics and synchronizes
        twin state with physical sensor stream.
        """
        # Run ML prediction on current telemetry
        pred_result = predictor.predict(telemetry)
        failure_risk = pred_result.get('failure_risk_score', 0.1)
        risk_pct = round(failure_risk * 100, 1)
        overall_health = max(5, int(round((1.0 - failure_risk) * 100)))

        # Extract telemetry sensor values
        rpm = float(telemetry.get('Engine rpm', telemetry.get('engine_rpm', 750)))
        oil_pres = float(telemetry.get('Lub oil pressure', telemetry.get('oil_pressure', 3.2)))
        fuel_pres = float(telemetry.get('Fuel pressure', telemetry.get('fuel_pressure', 6.5)))
        cool_pres = float(telemetry.get('Coolant pressure', telemetry.get('coolant_pressure', 2.3)))
        oil_temp = float(telemetry.get('lub oil temp', telemetry.get('oil_temp', 77.0)))
        cool_temp = float(telemetry.get('Coolant temp', telemetry.get('coolant_temp', 78.0)))

        # 1. Cooling System Subsystem
        cooling_health = 100
        cooling_status = "Optimal"
        if cool_temp > 105.0 or cool_pres < 1.0:
            cooling_health = max(10, int(100 - (cool_temp - 85.0) * 1.5))
            cooling_status = "Critical" if cool_temp > 115 else "Warning"
        elif cool_temp > 88.0 or cool_pres < 1.5:
            cooling_health = 75
            cooling_status = "Warning"

        # 2. Lubrication Subsystem
        lub_health = 100
        lub_status = "Optimal"
        if oil_pres < 1.5 or oil_temp > 85.0:
            lub_health = max(15, int(oil_pres / 3.5 * 100))
            lub_status = "Critical" if oil_pres < 1.0 else "Warning"
        elif oil_pres < 2.2 or oil_temp > 82.0:
            lub_health = 80
            lub_status = "Warning"

        # 3. Fuel Injection Subsystem
        fuel_health = 100
        fuel_status = "Optimal"
        if fuel_pres > 14.0 or fuel_pres < 3.0:
            fuel_health = 45
            fuel_status = "Critical" if fuel_pres > 18.0 else "Warning"
        elif fuel_pres > 9.5 or fuel_pres < 4.5:
            fuel_health = 80
            fuel_status = "Warning"

        # 4. Engine Core Assembly
        engine_health = int((cooling_health * 0.4) + (lub_health * 0.4) + (fuel_health * 0.2))
        engine_status = "Optimal"
        if engine_health < 50 or rpm < 350:
            engine_status = "Critical"
        elif engine_health < 75:
            engine_status = "Warning"

        # 5. Transmission & Drivetrain
        trans_health = 95 if rpm > 400 else 60
        trans_status = "Optimal" if trans_health > 70 else "Warning"

        return {
            "vehicle_id": self.vehicle_id,
            "overall_health_score": overall_health,
            "failure_risk_percentage": risk_pct,
            "failure_risk_score": failure_risk,
            "prediction": pred_result,
            "telemetry": {
                "rpm": rpm,
                "oil_pressure": oil_pres,
                "fuel_pressure": fuel_pres,
                "coolant_pressure": cool_pres,
                "oil_temp": oil_temp,
                "coolant_temp": cool_temp
            },
            "subsystems": {
                "engine_assembly": {
                    "name": "Engine Core & Cylinders",
                    "health": engine_health,
                    "status": engine_status
                },
                "cooling_system": {
                    "name": "Cooling Circuit & Radiator",
                    "health": cooling_health,
                    "status": cooling_status
                },
                "lubrication_system": {
                    "name": "Lubrication & Oil Pump",
                    "health": lub_health,
                    "status": lub_status
                },
                "fuel_injection": {
                    "name": "Fuel Delivery & Injectors",
                    "health": fuel_health,
                    "status": fuel_status
                },
                "transmission": {
                    "name": "Gearbox & Powertrain",
                    "health": trans_health,
                    "status": trans_status
                }
            }
        }

# Factory helper
def get_digital_twin(vehicle_id: str) -> VehicleDigitalTwin:
    return VehicleDigitalTwin(vehicle_id)
