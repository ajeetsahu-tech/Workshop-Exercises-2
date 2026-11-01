# Exercise 3.1 – Equipment Maintenance and Service Database

## Overview
This repository contains a complete self‑contained SQLite‑based equipment maintenance system with:
- **Database schema** (`schema.sql`) defining tables for equipment, technicians, service requests and updates.
- **Python data‑access layer** (`db.py`) exposing CRUD operations, parameterised queries and transaction handling.
- **Sample data loader** (`populate_data.py`) that inserts synthetic equipment and service request records.
- **Flask API** (`app.py`) that serves a tiny REST interface used by the web front‑end.
- **Web front‑end** (`static/index.html`, `static/styles.css`, `static/app.js`) built with vanilla HTML, CSS and JavaScript, showcasing a premium glass‑morphism UI.
- **Documentation & reports** (`ER_diagram.md`, `reports.md`, `security_notes.md`).

The solution follows the learning objectives of the exercise – relational modelling, parameterised CRUD, joins/aggregates, transactions, and security testing – while also delivering a polished user interface.

---
### Directory layout
```
Exercise3.1/
│   README.md                # you are reading it
│   schema.sql               # SQLite schema
│   db.py                    # Python DB helper module
│   populate_data.py         # inserts synthetic records
│   app.py                   # Flask backend exposing REST endpoints
│   ER_diagram.md            # ER diagram in Mermaid syntax
│   reports.md               # Example query results (6 reports)
│   security_notes.md        # Security & edge‑case test notes
│
└───static/                 # Front‑end assets
    │   index.html
    │   styles.css
    │   app.js
```
---
### Getting started
1. **Install dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install flask
   ```
2. **Create the database**
   ```bash
   sqlite3 maintenance.db < schema.sql
   ```
3. **Populate synthetic data**
   ```bash
   python populate_data.py
   ```
4. **Run the API server**
   ```bash
   python app.py
   ```
   The server listens on http://127.0.0.1:5000.
5. **Open the UI**
   Open `static/index.html` in a browser (or navigate to http://127.0.0.1:5000/ when using Flask’s static route).
---
### Highlights
- **Parameterised queries**: All user‑supplied values are sent via SQLite placeholders (`?`).
- **Transaction demo**: Updating a request’s status together with inserting a service update is wrapped in a single transaction; a simulated error triggers a rollback (see `db.update_request_status_with_history`).
- **Security tests**: `populate_data.py` attempts duplicate primary keys, invalid enum values and strings containing SQL metacharacters – all safely rejected.
- **Premium UI**: Glass‑morphism cards, subtle hover animations, Inter font from Google Fonts, and responsive layout.
---
Feel free to explore the code, run the reports, and extend the system (e.g., monthly maintenance‑cost summary).
