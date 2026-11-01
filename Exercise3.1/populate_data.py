import sqlite3
import os

DB_PATH = 'maintenance.db'
SCHEMA_PATH = 'schema.sql'

def run_schema():
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Equipment
    equipments = [
        ('Excavator', 'CAT320', 'SN001', None, 'Site A', 'active'),
        ('Bulldozer', 'Komatsu D85', 'SN002', None, 'Site B', 'active'),
        ('Crane', 'Liebherr LTM', 'SN003', None, 'Site C', 'active'),
    ]
    cur.executemany('INSERT INTO equipment (name, category, serial_number, purchase_date, location, status) VALUES (?,?,?,?,?,?)', equipments)
    # Technicians
    techs = [
        ('Alice', 'Smith', 'alice@example.com', '555-0101', 'Mechanical'),
        ('Bob', 'Jones', 'bob@example.com', '555-0102', 'Electrical'),
        ('Carol', 'Davis', 'carol@example.com', '555-0103', 'Hydraulics'),
    ]
    cur.executemany('INSERT INTO technicians (first_name, last_name, email, phone, expertise) VALUES (?,?,?,?,?)', techs)
    # Service requests
    requests = [
        (1, 'John Doe', 'Oil leak in hydraulic system', '2026-10-01', '2026-10-05', 'open'),
        (2, 'Mike Lee', 'Blade replacement needed', '2026-10-02', '2026-10-06', 'open'),
    ]
    cur.executemany('INSERT INTO service_requests (equipment_id, reported_by, description, request_date, due_date, status) VALUES (?,?,?,?,?,?)', requests)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    run_schema()
    insert_sample_data()
    print('Database populated.')
