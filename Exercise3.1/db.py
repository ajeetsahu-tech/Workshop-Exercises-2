import sqlite3
from contextlib import closing

DB_PATH = 'maintenance.db'

def get_connection():
    " Return a new SQLite connection with row factory for dict-like access.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Equipment ----------
def get_all_equipment():
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM equipment')
        return [dict(row) for row in cur]

def add_equipment(name, category, location):
    with closing(get_connection()) as conn:
        conn.execute('INSERT INTO equipment (name, category, location) VALUES (?,?,?)', (name, category, location))
        conn.commit()

# ---------- Technicians ----------
def get_all_technicians():
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM technicians')
        return [dict(row) for row in cur]

def add_technician(first_name, last_name, email, phone, expertise):
    with closing(get_connection()) as conn:
        conn.execute('INSERT INTO technicians (first_name, last_name, email, phone, expertise) VALUES (?,?,?,?,?)',
                     (first_name, last_name, email, phone, expertise))
        conn.commit()

# ---------- Service Requests ----------
def get_all_requests():
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM service_requests')
        return [dict(row) for row in cur]

def get_request_by_id(req_id):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM service_requests WHERE request_id = ?', (req_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def create_request(equipment_id, reported_by, description, request_date, due_date=None, status='open'):
    with closing(get_connection()) as conn:
        conn.execute('''INSERT INTO service_requests (equipment_id, reported_by, description, request_date, due_date, status)
                         VALUES (?,?,?,?,?,?)''',
                     (equipment_id, reported_by, description, request_date, due_date, status))
        conn.commit()

# ---------- Service Updates ----------
def get_updates_for_request(req_id):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM service_updates WHERE request_id = ?', (req_id,))
        return [dict(row) for row in cur]

def add_update(request_id, technician_id, notes, new_status=None):
    with closing(get_connection()) as conn:
        conn.execute('INSERT INTO service_updates (request_id, technician_id, notes, new_status) VALUES (?,?,?,?)',
                     (request_id, technician_id, notes, new_status))
        conn.commit()

# ---------- Transaction Demo ----------
def update_request_status_with_history(req_id, new_status, technician_id, notes):
    Atomically update status and add a history note.
    with closing(get_connection()) as conn:
        try:
            conn.execute('BEGIN')
            conn.execute('UPDATE service_requests SET status = ? WHERE request_id = ?', (new_status, req_id))
            conn.execute('INSERT INTO service_updates (request_id, technician_id, notes, new_status) VALUES (?,?,?,?)',
                         (req_id, technician_id, notes, new_status))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
