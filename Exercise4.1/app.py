"""Local lost-and-found notice board for the workshop."""

import os
import secrets
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException

BASE_DIR = Path(__file__).resolve().parent
CATEGORIES = ["Electronics", "Books", "Clothing", "Keys", "ID card", "Other"]
CONTACT_PREFERENCES = ["Campus desk", "Email", "Phone"]
ZONES = ["Library", "Workshop Hall", "Cafeteria", "Computer Lab", "Auditorium", "Other"]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        DATABASE=str(BASE_DIR / "notices.db"),
        SEED_SAMPLE_DATA=True,
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    def initialize_db():
        db = get_db()
        db.execute("""CREATE TABLE IF NOT EXISTS notices (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            description TEXT NOT NULL CHECK(length(description) <= 500),
            location_zone TEXT NOT NULL,
            item_date TEXT NOT NULL,
            contact_preference TEXT NOT NULL,
            contact_details TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            resolved INTEGER NOT NULL DEFAULT 0 CHECK(resolved IN (0, 1))
        )""")
        db.commit()
        if app.config.get("SEED_SAMPLE_DATA"):
            count = db.execute("SELECT COUNT(*) FROM notices").fetchone()[0]
            if count == 0:
                import json

                seed = json.loads((BASE_DIR / "sample_notices.json").read_text(encoding="utf-8"))
                db.executemany(
                    "INSERT INTO notices (id, category, description, location_zone, item_date, contact_preference, contact_details, created_at, resolved) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [(
                        item["id"], item["category"], item["description"], item["location_zone"],
                        item["item_date"], item["contact_preference"], item["contact_details"],
                        item["created_at"], int(item["resolved"]),
                    ) for item in seed],
                )
                db.commit()

    @app.before_request
    def ensure_schema():
        initialize_db()
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)

    @app.teardown_appcontext
    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'"
        return response

    @app.get("/")
    def index():
        category = request.args.get("category", "").strip()
        zone = request.args.get("zone", "").strip()
        if category and category not in CATEGORIES:
            category = ""
        if zone and zone not in ZONES:
            zone = ""
        query = "SELECT * FROM notices WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if zone:
            query += " AND location_zone = ?"
            params.append(zone)
        query += " ORDER BY created_at DESC"
        notices = get_db().execute(query, params).fetchall()
        return render_template("index.html", notices=notices, categories=CATEGORIES, zones=ZONES,
                               selected_category=category, selected_zone=zone)

    @app.get("/notice/<notice_id>")
    def detail(notice_id):
        notice = get_db().execute("SELECT * FROM notices WHERE id = ?", (notice_id,)).fetchone()
        if notice is None:
            abort(404)
        return render_template("detail.html", notice=notice)

    @app.route("/create", methods=["GET", "POST"])
    def create_notice():
        if request.method == "GET":
            session["submission_token"] = secrets.token_urlsafe(24)
            return render_template("create.html", categories=CATEGORIES, zones=ZONES,
                                   contact_preferences=CONTACT_PREFERENCES, form={}, errors={}, today=date.today().isoformat())

        if (request.form.get("csrf_token") != session.get("csrf_token")
                or request.form.get("submission_token") != session.get("submission_token")):
            abort(400)
        form = {key: request.form.get(key, "").strip() for key in
                ("category", "description", "location_zone", "item_date", "contact_preference", "contact_details")}
        errors = {}
        if form["category"] not in CATEGORIES:
            errors["category"] = "Choose a supported item category."
        if not form["description"]:
            errors["description"] = "Description is required."
        elif len(form["description"]) > 500:
            errors["description"] = "Description must be 500 characters or fewer."
        if form["location_zone"] not in ZONES:
            errors["location_zone"] = "Choose a supported campus zone."
        try:
            submitted_date = date.fromisoformat(form["item_date"])
            if submitted_date > date.today():
                errors["item_date"] = "Date cannot be in the future."
        except ValueError:
            errors["item_date"] = "Enter a valid date."
        if form["contact_preference"] not in CONTACT_PREFERENCES:
            errors["contact_preference"] = "Choose a contact preference."
        if len(form["contact_details"]) > 120:
            errors["contact_details"] = "Contact detail must be 120 characters or fewer."

        if errors:
            return render_template("create.html", categories=CATEGORIES, zones=ZONES,
                                   contact_preferences=CONTACT_PREFERENCES, form=form, errors=errors,
                                   today=date.today().isoformat()), 400

        notice_id = uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        get_db().execute(
            "INSERT INTO notices (id, category, description, location_zone, item_date, contact_preference, contact_details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (notice_id, form["category"], form["description"], form["location_zone"], form["item_date"],
             form["contact_preference"], form["contact_details"], created_at),
        )
        get_db().commit()
        session.pop("submission_token", None)
        flash("Notice posted.", "success")
        return redirect(url_for("detail", notice_id=notice_id), code=303)

    @app.post("/notice/<notice_id>/resolve")
    def resolve_notice(notice_id):
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)
        cursor = get_db().execute("UPDATE notices SET resolved = 1 WHERE id = ?", (notice_id,))
        get_db().commit()
        if cursor.rowcount == 0:
            abort(404)
        flash("Notice marked as resolved.", "success")
        return redirect(url_for("detail", notice_id=notice_id), code=303)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="That notice or page could not be found."), 404

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template("error.html", code=400, message="The request could not be accepted. Please refresh and try again."), 400

    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unexpected application error", exc_info=error)
        return render_template("error.html", code=500, message="Something went wrong. Please try again later."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
