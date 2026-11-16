import sqlite3
from flask import current_app, g
from datetime import datetime

def get_db():
    """Retrieve or open a new database connection for current request context."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_all_vehicles():
    """Retrieve all vehicles with their latest failure risk and status."""
    db = get_db()
    query = """
        SELECT v.*, 
            COALESCE(p.failure_risk_score, 0.10) as latest_risk_score,
            COALESCE(p.predicted_failure_component, 'Nominal') as latest_component,
            COALESCE(p.severity_level, 'LOW') as latest_severity
        FROM vehicles v
        LEFT JOIN (
            SELECT vehicle_id, failure_risk_score, predicted_failure_component, severity_level,
                   ROW_NUMBER() OVER(PARTITION BY vehicle_id ORDER BY prediction_time DESC) as rn
            FROM failure_predictions
        ) p ON v.vehicle_id = p.vehicle_id AND p.rn = 1
        ORDER BY v.id ASC
    """
    rows = db.execute(query).fetchall()
    vehicles = []
    for r in rows:
        v = dict(r)
        risk = v.get('latest_risk_score', 0.10)
        v['health_score'] = max(5, int(round((1.0 - risk) * 100)))
        vehicles.append(v)
    return vehicles

def get_vehicle_by_id(vehicle_id):
    """Retrieve a single vehicle by vehicle_id."""
    db = get_db()
    row = db.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,)).fetchone()
    if not row:
        return None
    v = dict(row)
    
    # Get latest prediction
    pred = db.execute("""
        SELECT * FROM failure_predictions 
        WHERE vehicle_id = ? 
        ORDER BY prediction_time DESC LIMIT 1
    """, (vehicle_id,)).fetchone()
    
    if pred:
        v['latest_prediction'] = dict(pred)
        risk = pred['failure_risk_score']
        v['health_score'] = max(5, int(round((1.0 - risk) * 100)))
    else:
        v['latest_prediction'] = None
        v['health_score'] = 95
        
    return v

def get_recent_telemetry(vehicle_id, limit=24):
    """Retrieve time-series telemetry logs for a vehicle in chronological order."""
    db = get_db()
    rows = db.execute("""
        SELECT * FROM (
            SELECT * FROM sensor_telemetry 
            WHERE vehicle_id = ? 
            ORDER BY timestamp DESC LIMIT ?
        ) ORDER BY timestamp ASC
    """, (vehicle_id, limit)).fetchall()
    return [dict(r) for r in rows]

def get_fleet_summary():
    """Retrieve high-level KPI metrics across the fleet."""
    db = get_db()
    vehicles = get_all_vehicles()
    total = len(vehicles)
    operational = sum(1 for v in vehicles if v['current_status'] == 'Operational')
    warning = sum(1 for v in vehicles if v['current_status'] == 'Warning')
    critical = sum(1 for v in vehicles if v['current_status'] == 'Critical')
    
    avg_health = round(sum(v['health_score'] for v in vehicles) / total, 1) if total > 0 else 100.0
    
    # Active unresolved failure alerts
    unresolved_alerts = db.execute("""
        SELECT COUNT(*) FROM failure_predictions WHERE is_resolved = 0 AND severity_level IN ('HIGH', 'CRITICAL')
    """).fetchone()[0]
    
    return {
        "total_vehicles": total,
        "operational_count": operational,
        "warning_count": warning,
        "critical_count": critical,
        "avg_health_score": avg_health,
        "active_alerts": unresolved_alerts
    }

def get_all_predictions(limit=50):
    """Retrieve failure prediction logs."""
    db = get_db()
    rows = db.execute("""
        SELECT p.*, v.vehicle_model, v.license_plate
        FROM failure_predictions p
        JOIN vehicles v ON p.vehicle_id = v.vehicle_id
        ORDER BY p.prediction_time DESC LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_maintenance_tickets(vehicle_id=None):
    """Retrieve maintenance history and active service orders."""
    db = get_db()
    if vehicle_id:
        rows = db.execute("""
            SELECT * FROM maintenance_logs 
            WHERE vehicle_id = ? 
            ORDER BY scheduled_date DESC
        """, (vehicle_id,)).fetchall()
    else:
        rows = db.execute("""
            SELECT m.*, v.vehicle_model, v.license_plate
            FROM maintenance_logs m
            JOIN vehicles v ON m.vehicle_id = v.vehicle_id
            ORDER BY m.scheduled_date DESC
        """).fetchall()
    return [dict(r) for r in rows]

def add_vehicle(vehicle_id, model, year, plate, status, mileage):
    """Insert a new fleet vehicle."""
    db = get_db()
    db.execute("""
        INSERT INTO vehicles (vehicle_id, vehicle_model, manufacture_year, license_plate, current_status, total_mileage_km, last_service_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (vehicle_id, model, year, plate, status, mileage, datetime.now().strftime('%Y-%m-%d')))
    db.commit()

def delete_vehicle(vehicle_id):
    """Delete a vehicle and its cascaded telemetry."""
    db = get_db()
    db.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    db.commit()

def add_maintenance_ticket(vehicle_id, service_type, scheduled_date, notes):
    """Schedule a maintenance service."""
    db = get_db()
    db.execute("""
        INSERT INTO maintenance_logs (vehicle_id, service_type, scheduled_date, status, technician_notes)
        VALUES (?, ?, ?, 'Scheduled', ?)
    """, (vehicle_id, service_type, scheduled_date, notes))
    db.commit()

def resolve_maintenance_ticket(ticket_id):
    """Mark a maintenance ticket as completed."""
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    db.execute("""
        UPDATE maintenance_logs 
        SET status = 'Completed', completed_date = ? 
        WHERE id = ?
    """, (today, ticket_id))
    db.commit()

def save_telemetry_and_prediction(vehicle_id, telemetry_data, prediction_result):
    """Save an incoming telemetry reading and associated ML prediction log."""
    db = get_db()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save telemetry
    db.execute("""
        INSERT INTO sensor_telemetry (
            vehicle_id, timestamp, engine_temp_c, oil_pressure_psi, 
            vibration_amplitude_g, coolant_temp_c, battery_voltage_v, 
            engine_rpm, vehicle_speed_kmh
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vehicle_id, now_str,
        telemetry_data.get('Coolant temp', 78.0),
        telemetry_data.get('Lub oil pressure', 3.2),
        telemetry_data.get('vibration', 0.15),
        telemetry_data.get('Coolant pressure', 2.3),
        13.8,
        telemetry_data.get('Engine rpm', 750),
        telemetry_data.get('speed', 65.0)
    ))
    
    # Save prediction
    risk = prediction_result.get('failure_risk_score', 0.1)
    severity = prediction_result.get('severity', 'LOW')
    component = prediction_result.get('suspect_component', 'None')
    action = prediction_result.get('recommended_action', 'Nominal operation')
    
    db.execute("""
        INSERT INTO failure_predictions (
            vehicle_id, prediction_time, failure_risk_score, 
            predicted_failure_component, severity_level, recommended_action, is_resolved
        ) VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (vehicle_id, now_str, risk, component, severity, action))
    
    # Update vehicle status based on severity
    new_status = 'Operational'
    if severity == 'CRITICAL':
        new_status = 'Critical'
    elif severity in ('HIGH', 'MEDIUM'):
        new_status = 'Warning'
        
    db.execute("""
        UPDATE vehicles SET current_status = ? WHERE vehicle_id = ?
    """, (new_status, vehicle_id))
    
    db.commit()
