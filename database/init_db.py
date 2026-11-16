"""
Database initialization and data seeding script for Fleet Digital Twin.
Creates SQLite tables and seeds sample fleet vehicles, historical telemetry, and maintenance records.
"""

import sqlite3
from pathlib import Path
import random
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'database' / 'fleet_data.db'
SCHEMA_PATH = BASE_DIR / 'database' / 'schema.sql'

def initialize_database():
    print(f"Connecting to SQLite database at: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    print("Database tables created successfully.")

    # Reset tables for clean seeding
    cursor.execute("DELETE FROM sensor_telemetry")
    cursor.execute("DELETE FROM failure_predictions")
    cursor.execute("DELETE FROM maintenance_logs")
    cursor.execute("DELETE FROM vehicles")

    # Seed Fleet Vehicles
    sample_vehicles = [
        ('VH-101', 'Tata Prima 5530.S (Heavy Truck)', 2022, 'KA-01-EQ-1001', 'Operational', 45200.5, '2026-01-15'),
        ('VH-102', 'Ashok Leyland AVTR 4220 (Haulage)', 2023, 'KA-01-EQ-1002', 'Warning', 38400.0, '2026-02-10'),
        ('VH-103', 'BharatBenz 2823R (Multi-Axle)', 2021, 'KA-01-EQ-1003', 'Critical', 82150.2, '2025-11-20'),
        ('VH-104', 'Eicher Pro 6028 (Container Carrier)', 2023, 'KA-01-EQ-1004', 'Operational', 29100.8, '2026-03-01'),
        ('VH-105', 'Mahindra Blazo X 49 (Tipper)', 2022, 'KA-01-EQ-1005', 'Operational', 51430.6, '2026-01-28'),
        ('VH-106', 'Volvo FH16 (Long-Haul Puller)', 2024, 'KA-01-EQ-1006', 'Operational', 18250.0, '2026-03-05')
    ]
    
    cursor.executemany("""
        INSERT INTO vehicles (vehicle_id, vehicle_model, manufacture_year, license_plate, current_status, total_mileage_km, last_service_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_vehicles)
    print(f"Seeded {len(sample_vehicles)} fleet vehicles.")

    # Seed Historical Telemetry time-series for each vehicle
    now = datetime.now()
    telemetry_records = []
    
    # Profiles for telemetry:
    # VH-101: Healthy baseline
    # VH-102: Cooling degradation (Warning)
    # VH-103: Lubrication and thermal failure (Critical)
    # Others: Normal operational variation
    
    for v_id, _, _, _, status, _, _ in sample_vehicles:
        for i in range(24, 0, -1):
            ts = (now - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
            
            if v_id == 'VH-103':  # Critical
                rpm = random.randint(350, 600)
                oil_pres = round(random.uniform(0.6, 1.4), 2)
                fuel_pres = round(random.uniform(14.0, 19.5), 2)
                cool_pres = round(random.uniform(0.5, 1.2), 2)
                oil_temp = round(random.uniform(84.0, 89.5), 2)
                cool_temp = round(random.uniform(105.0, 142.0), 2)
                speed = round(random.uniform(20.0, 45.0), 1)
            elif v_id == 'VH-102':  # Warning
                rpm = random.randint(650, 900)
                oil_pres = round(random.uniform(2.1, 2.9), 2)
                fuel_pres = round(random.uniform(7.5, 11.0), 2)
                cool_pres = round(random.uniform(1.4, 2.0), 2)
                oil_temp = round(random.uniform(79.0, 83.5), 2)
                cool_temp = round(random.uniform(92.0, 102.0), 2)
                speed = round(random.uniform(50.0, 68.0), 1)
            else:  # Operational
                rpm = random.randint(750, 950)
                oil_pres = round(random.uniform(3.2, 4.5), 2)
                fuel_pres = round(random.uniform(5.5, 7.2), 2)
                cool_pres = round(random.uniform(2.1, 2.7), 2)
                oil_temp = round(random.uniform(75.0, 78.5), 2)
                cool_temp = round(random.uniform(76.0, 81.0), 2)
                speed = round(random.uniform(60.0, 75.0), 1)
                
            vib = round(random.uniform(0.10, 0.45 if status == 'Critical' else 0.18), 3)
            
            telemetry_records.append((
                v_id, ts, cool_temp, oil_pres, vib, cool_pres, 13.8, rpm, speed
            ))

    cursor.executemany("""
        INSERT INTO sensor_telemetry (
            vehicle_id, timestamp, engine_temp_c, oil_pressure_psi, 
            vibration_amplitude_g, coolant_temp_c, battery_voltage_v, 
            engine_rpm, vehicle_speed_kmh
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, telemetry_records)
    print(f"Seeded {len(telemetry_records)} telemetry logs.")

    # Seed Sample Failure Predictions
    predictions = [
        ('VH-103', '2026-03-10 14:30:00', 0.8842, 'Engine Cooling Circuit', 'CRITICAL', 'Immediate workshop intervention required: Radiator coolant temperature critical (128°C) and oil pressure deficit (0.9 bar).', 0),
        ('VH-102', '2026-03-10 13:15:00', 0.6125, 'Coolant Subsystem', 'HIGH', 'Coolant temperature elevated above 95°C. Check radiator fan and thermostat valve.', 0),
        ('VH-105', '2026-03-09 09:45:00', 0.3850, 'Fuel Injection System', 'MEDIUM', 'Fuel pressure variation detected during cruise speed. Recommend fuel filter inspection.', 1),
        ('VH-101', '2026-03-08 16:20:00', 0.1200, 'None', 'LOW', 'Vehicle operating within nominal health envelope. Routine maintenance schedule active.', 1)
    ]
    cursor.executemany("""
        INSERT INTO failure_predictions (
            vehicle_id, prediction_time, failure_risk_score, 
            predicted_failure_component, severity_level, recommended_action, is_resolved
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, predictions)
    print(f"Seeded {len(predictions)} failure predictions.")

    # Seed Maintenance Logs
    tickets = [
        ('VH-103', 'Emergency Repair', '2026-03-11', None, 'In Progress', 'Radiator hose replacement and oil pump pressure test.'),
        ('VH-102', 'Predictive Alert', '2026-03-14', None, 'Scheduled', 'Coolant system inspection and thermostat diagnostic test.'),
        ('VH-101', 'Scheduled', '2026-01-15', '2026-01-15', 'Completed', 'Standard 45,000 km periodic service and synthetic oil change.')
    ]
    cursor.executemany("""
        INSERT INTO maintenance_logs (
            vehicle_id, service_type, scheduled_date, completed_date, status, technician_notes
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, tickets)
    print(f"Seeded {len(tickets)} maintenance logs.")

    conn.commit()
    conn.close()
    print("Database initialization and population finished.")

if __name__ == '__main__':
    initialize_database()
