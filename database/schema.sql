-- SQLite Schema for AI-Enabled Fleet Digital Twin

-- 1. Fleet Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT UNIQUE NOT NULL,
    vehicle_model TEXT NOT NULL,
    manufacture_year INTEGER NOT NULL,
    license_plate TEXT NOT NULL,
    current_status TEXT DEFAULT 'Operational', -- 'Operational', 'Warning', 'Critical', 'In-Service'
    total_mileage_km REAL DEFAULT 0.0,
    last_service_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Real-time Telemetry & Sensor Readings (Digital Twin Inputs)
CREATE TABLE IF NOT EXISTS sensor_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    engine_temp_c REAL NOT NULL,
    oil_pressure_psi REAL NOT NULL,
    vibration_amplitude_g REAL NOT NULL,
    coolant_temp_c REAL NOT NULL,
    battery_voltage_v REAL NOT NULL,
    engine_rpm INTEGER NOT NULL,
    vehicle_speed_kmh REAL NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- 3. Predictive Maintenance ML Output Logs
CREATE TABLE IF NOT EXISTS failure_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_risk_score REAL NOT NULL, -- Probability (0.00 to 1.00)
    predicted_failure_component TEXT NOT NULL, -- e.g., 'Engine Cooling', 'Transmission', 'Brake System', 'None'
    severity_level TEXT NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    recommended_action TEXT,
    is_resolved INTEGER DEFAULT 0,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- 4. Maintenance Service History & Logs
CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    service_type TEXT NOT NULL, -- 'Scheduled', 'Predictive Alert', 'Emergency Repair'
    scheduled_date TEXT NOT NULL,
    completed_date TEXT,
    status TEXT DEFAULT 'Scheduled', -- 'Scheduled', 'In Progress', 'Completed'
    technician_notes TEXT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);
