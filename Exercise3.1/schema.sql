-- Equipment Maintenance and Service Database Schema
-- SQLite dialect

CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    serial_number TEXT UNIQUE NOT NULL,
    purchase_date DATE,
    location TEXT,
    status TEXT CHECK (status IN ('active','inactive','decommissioned')) DEFAULT 'active'
);

CREATE TABLE technicians (
    technician_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    expertise TEXT
);

CREATE TABLE service_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    reported_by TEXT NOT NULL,
    description TEXT NOT NULL,
    request_date DATE NOT NULL,
    due_date DATE,
    status TEXT CHECK (status IN ('open','in_progress','closed','overdue')) DEFAULT 'open',
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE CASCADE
);

CREATE TABLE service_updates (
    update_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    technician_id INTEGER NOT NULL,
    update_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    new_status TEXT CHECK (new_status IN ('open','in_progress','closed','overdue')),
    FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (technician_id) REFERENCES technicians(technician_id) ON DELETE SET NULL
);

-- Indexes to speed up common queries
CREATE INDEX idx_eq_category ON equipment(category);
CREATE INDEX idx_req_status ON service_requests(status);
CREATE INDEX idx_upd_req ON service_updates(request_id);
