"""
REST API endpoints for Fleet Digital Twin.
Serves telemetry streams, ML predictions, and digital twin state synchronization.
"""

from flask import Blueprint, jsonify, request
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
    summary = get_fleet_summary()
    return jsonify({"status": "success", "data": summary})

@api_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """List all connected vehicles."""
    vehicles = get_all_vehicles()
    return jsonify({"status": "success", "count": len(vehicles), "vehicles": vehicles})

@api_bp.route('/vehicles/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Retrieve metadata and recent status for a vehicle."""
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle:
        return jsonify({"status": "error", "message": f"Vehicle {vehicle_id} not found."}), 404
    return jsonify({"status": "success", "vehicle": vehicle})

@api_bp.route('/vehicles/<vehicle_id>/telemetry', methods=['GET'])
def get_telemetry(vehicle_id):
    """Retrieve time-series sensor telemetry for graphing."""
    limit = int(request.args.get('limit', 24))
    telemetry = get_recent_telemetry(vehicle_id, limit=limit)
    return jsonify({
        "status": "success",
        "vehicle_id": vehicle_id,
        "count": len(telemetry),
        "telemetry": telemetry
    })

@api_bp.route('/digital-twin/<vehicle_id>', methods=['GET'])
def get_twin_state(vehicle_id):
    """Retrieve digital twin subsystem status and health score."""
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
    data = request.get_json() or {}
    
    # Run prediction
    prediction_result = predictor.predict(data)
    
    # Also compute digital twin subsystem health breakdown
    twin = get_digital_twin(data.get('vehicle_id', 'SIMULATED-VEHICLE'))
    twin_state = twin.compute_twin_state(data)

    return jsonify({
        "status": "success",
        "prediction": prediction_result,
        "digital_twin": twin_state
    })

@api_bp.route('/vehicles/<vehicle_id>/telemetry', methods=['POST'])
def ingest_telemetry(vehicle_id):
    """
    Ingest real-time telemetry from vehicle ECU/IoT edge node,
    execute ML model inference, and persist to SQLite.
    """
    data = request.get_json() or {}
    
    # Execute ML failure prediction
    prediction_result = predictor.predict(data)
    
    # Save to database
    save_telemetry_and_prediction(vehicle_id, data, prediction_result)
    
    # Return updated twin state
    twin = get_digital_twin(vehicle_id)
    twin_state = twin.compute_twin_state(data)
    
    return jsonify({
        "status": "success",
        "message": f"Telemetry ingested for vehicle {vehicle_id}.",
        "prediction": prediction_result,
        "digital_twin": twin_state
    })
