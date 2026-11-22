"""
REST API endpoints for Fleet Digital Twin.
Serves telemetry streams, ML predictions, and digital twin state synchronization
with full input validation, exception handling, and audit logging.
"""

from flask import Blueprint, jsonify, request, current_app
from app.models.db import (
    get_all_vehicles,
    get_vehicle_by_id,
    get_recent_telemetry,
    get_fleet_summary,
    save_telemetry_and_prediction
)
from app.services.predictor import predictor
from app.services.digital_twin import get_digital_twin

api_bp = Blueprint('api', __name__)

@api_bp.route('/fleet/summary', methods=['GET'])
def fleet_summary():
    """Retrieve high-level fleet metrics."""
    try:
        summary = get_fleet_summary()
        return jsonify({"status": "success", "data": summary})
    except Exception as e:
        current_app.logger.error(f"Error retrieving fleet summary: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to retrieve fleet summary."}), 500

@api_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """List all connected vehicles."""
    try:
        vehicles = get_all_vehicles()
        return jsonify({"status": "success", "count": len(vehicles), "vehicles": vehicles})
    except Exception as e:
        current_app.logger.error(f"Error retrieving vehicles list: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to retrieve vehicles list."}), 500

@api_bp.route('/vehicles/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Retrieve metadata and recent status for a vehicle."""
    try:
        vehicle = get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return jsonify({"status": "error", "message": f"Vehicle {vehicle_id} not found."}), 404
        return jsonify({"status": "success", "vehicle": vehicle})
    except Exception as e:
        current_app.logger.error(f"Error retrieving vehicle {vehicle_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Failed to retrieve vehicle {vehicle_id}."}), 500

@api_bp.route('/vehicles/<vehicle_id>/telemetry', methods=['GET'])
def get_telemetry(vehicle_id):
    """Retrieve time-series sensor telemetry for graphing."""
    try:
        limit = int(request.args.get('limit', 24))
        if limit <= 0 or limit > 500:
            return jsonify({"status": "error", "message": "Limit must be an integer between 1 and 500."}), 400
        telemetry = get_recent_telemetry(vehicle_id, limit=limit)
        return jsonify({
            "status": "success",
            "vehicle_id": vehicle_id,
            "count": len(telemetry),
            "telemetry": telemetry
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Query parameter 'limit' must be an integer."}), 400
    except Exception as e:
        current_app.logger.error(f"Error retrieving telemetry for {vehicle_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to retrieve telemetry records."}), 500

@api_bp.route('/digital-twin/<vehicle_id>', methods=['GET'])
def get_twin_state(vehicle_id):
    """Retrieve digital twin subsystem status and health score."""
    try:
        telemetry = get_recent_telemetry(vehicle_id, limit=1)
        twin = get_digital_twin(vehicle_id)
        
        current_reading = telemetry[0] if telemetry else {
            'Engine rpm': 750,
            'Lub oil pressure': 3.2,
            'Fuel pressure': 6.5,
            'Coolant pressure': 2.3,
            'lub oil temp': 77.0,
            'Coolant temp': 78.0
        }
        
        twin_data = twin.compute_twin_state(current_reading)
        return jsonify({"status": "success", "digital_twin": twin_data})
    except Exception as e:
        current_app.logger.error(f"Error computing twin state for {vehicle_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to compute digital twin state."}), 500

@api_bp.route('/predict', methods=['POST'])
def run_prediction():
    """
    Run Machine Learning failure inference on provided sensor inputs.
    Expects JSON:
    {
        "Engine rpm": 750,
        "Lub oil pressure": 3.2,
        "Fuel pressure": 6.5,
        "Coolant pressure": 2.3,
        "lub oil temp": 77.0,
        "Coolant temp": 78.0
    }
    """
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid JSON payload. Expected a dictionary of sensor readings."
        }), 400

    # Validate numeric types
    for key, val in data.items():
        if key != 'vehicle_id':
            try:
                float(val)
            except (ValueError, TypeError):
                return jsonify({
                    "status": "error",
                    "message": f"Sensor value for '{key}' must be numeric (received: '{val}')."
                }), 400

    try:
        prediction_result = predictor.predict(data)
        twin = get_digital_twin(data.get('vehicle_id', 'SIMULATED-VEHICLE'))
        twin_state = twin.compute_twin_state(data)

        current_app.logger.info(
            f"Prediction computed: Risk={prediction_result.get('risk_level')}, "
            f"Prob={prediction_result.get('failure_risk_percentage')}%, "
            f"Health={prediction_result.get('health_score')}%"
        )

        return jsonify({
            "status": "success",
            "prediction": prediction_result,
            "digital_twin": twin_state
        })
    except Exception as e:
        current_app.logger.error(f"Prediction inference error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Inference engine failure: {str(e)}"
        }), 500

@api_bp.route('/vehicles/<vehicle_id>/telemetry', methods=['POST'])
def ingest_telemetry(vehicle_id):
    """
    Ingest real-time telemetry from vehicle ECU/IoT edge node,
    execute ML model inference, and persist to SQLite.
    """
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Invalid JSON telemetry payload."}), 400

    try:
        # Verify vehicle exists
        vehicle = get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return jsonify({"status": "error", "message": f"Vehicle {vehicle_id} does not exist in fleet registry."}), 404

        # Execute ML failure prediction
        prediction_result = predictor.predict(data)
        
        # Save to database
        save_telemetry_and_prediction(vehicle_id, data, prediction_result)
        
        # Return updated twin state
        twin = get_digital_twin(vehicle_id)
        twin_state = twin.compute_twin_state(data)
        
        current_app.logger.info(f"Telemetry ingested for {vehicle_id}. New status: {vehicle.get('current_status')}")
        
        return jsonify({
            "status": "success",
            "message": f"Telemetry ingested for vehicle {vehicle_id}.",
            "prediction": prediction_result,
            "digital_twin": twin_state
        })
    except Exception as e:
        current_app.logger.error(f"Error ingesting telemetry for {vehicle_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Failed to ingest telemetry: {str(e)}"}), 500
