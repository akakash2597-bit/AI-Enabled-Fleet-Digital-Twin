"""
Database initialization script for Fleet Digital Twin.
Creates tables and seeds initial fleet vehicle records.
"""

import sqlite3
from pathlib import Path

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

    # Seed sample fleet vehicles if table is empty
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_vehicles = [
            ('VH-101', 'Tata Prima 5530.S', 2022, 'KA-01-EQ-1001', 'Operational', 45200.5, '2026-01-15'),
            ('VH-102', 'Ashok Leyland AVTR 4220', 2023, 'KA-01-EQ-1002', 'Warning', 38400.0, '2026-02-10'),
            ('VH-103', 'BharatBenz 2823R', 2021, 'KA-01-EQ-1003', 'Critical', 82150.2, '2025-11-20'),
            ('VH-104', 'Eicher Pro 6028', 2023, 'KA-01-EQ-1004', 'Operational', 29100.8, '2026-03-01'),
            ('VH-105', 'Mahindra Blazo X 49', 2022, 'KA-01-EQ-1005', 'Operational', 51430.6, '2026-01-28')
        ]
        
        cursor.executemany("""
            INSERT INTO vehicles (vehicle_id, vehicle_model, manufacture_year, license_plate, current_status, total_mileage_km, last_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_vehicles)
        
        conn.commit()
        print(f"Seeded {len(sample_vehicles)} sample fleet vehicles.")
    else:
        print(f"Database already contains {count} vehicle records.")

    conn.close()
    print("Database initialization complete.")

if __name__ == '__main__':
    initialize_database()
