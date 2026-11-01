# Exercise 4.1 — Flask Lost-and-Found Notice Board

A localhost-only notice board built with Flask and SQLite. It supports listing, viewing, creating, filtering, and resolving sample campus item notices.

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. The app creates `notices.db` on first request and seeds it from `sample_notices.json`. The generated database is ignored by Git so local records stay local. Sample contact details are fictional. Do not enter real personal contact information.

## Security notes

- State changes use POST, CSRF tokens, per-form submission tokens, and a redirect after a successful post.
- SQLite writes are parameterized; descriptions and contact fields are rendered through Jinja autoescaping.
- Categories, campus zones, dates, and length limits are validated server-side.
- Unexpected exceptions are logged locally while visitors see a generic error page; basic browser security headers are set.
- Bind only to `127.0.0.1`; debug mode is off.

## Route and validation test table

Run checks using `python -m unittest -v`.

| Scenario | Expected result |
|---|---|
| List notices and filter by category/zone | `GET /` returns matching notices |
| View existing / missing notice | `GET /notice/<id>` returns detail / generic 404 |
| Valid notice submission | `POST /create` persists a unique ID and UTC timestamp, then returns 303 to detail |
| Missing required data, unsupported category/zone, malformed/future date | Form returns 400 with field-level explanation; no row is stored |
| Description over 500 characters | Rejected with 400 |
| Re-submit the same creation form | One-time submission token rejects duplicate POST |
| Resolve a notice | `POST /notice/<id>/resolve` updates the record; repeat is idempotent |
| GET a resolve URL / invalid CSRF token | GET returns 405; invalid token returns 400 |
| Unknown route | Generic 404 page |

## Screenshots

For the lab submission, run the app and capture the notices list, a notice detail, and the create form in your browser.
