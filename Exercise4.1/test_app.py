"""Route, validation, persistence, and error-path checks."""

import tempfile
import unittest
from pathlib import Path

from app import create_app


class NoticeBoardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = str(Path(self.temp_dir.name) / "test.sqlite")
        self.app = create_app({
            "TESTING": True,
            "DATABASE": database,
            "SEED_SAMPLE_DATA": False,
            "SECRET_KEY": "test-secret",
        })
        self.client = self.app.test_client()
        self.csrf = self._csrf()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _csrf(self):
        self.client.get("/create")
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def _submission_token(self):
        with self.client.session_transaction() as session:
            return session["submission_token"]

    def _valid_form(self, **overrides):
        data = {
            "csrf_token": self.csrf,
            "submission_token": self._submission_token(),
            "category": "Books",
            "description": "Green notebook, sample only",
            "location_zone": "Library",
            "item_date": "2026-10-30",
            "contact_preference": "Campus desk",
            "contact_details": "Campus desk extension 0000 (dummy)",
        }
        data.update(overrides)
        return data

    def test_list_page_and_unknown_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lost &amp; found notices", response.data)
        self.assertEqual(self.client.get("/not-a-route").status_code, 404)

    def test_create_notice_redirects_and_persists(self):
        form = self._valid_form()
        response = self.client.post("/create", data=form)
        self.assertEqual(response.status_code, 303)
        detail = self.client.get(response.headers["Location"])
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"Green notebook", detail.data)
        self.assertEqual(self.client.post("/create", data=form).status_code, 400)

    def test_missing_fields_unsupported_category_and_long_description_rejected(self):
        cases = [
            self._valid_form(description=""),
            self._valid_form(category="Unsupported"),
            self._valid_form(description="x" * 501),
            self._valid_form(location_zone="Unknown zone"),
            self._valid_form(item_date="not-a-date"),
        ]
        for form in cases:
            with self.subTest(form=form):
                self.assertEqual(self.client.post("/create", data=form).status_code, 400)
        self.assertEqual(self.client.get("/").data.count(b"notice-card"), 0)

    def test_missing_record_and_resolve_are_safe(self):
        self.assertEqual(self.client.get("/notice/missing").status_code, 404)
        self.assertEqual(self.client.post("/notice/missing/resolve", data={"csrf_token": self.csrf}).status_code, 404)

    def test_resolve_requires_post_and_repeated_post_is_idempotent(self):
        created = self.client.post("/create", data=self._valid_form())
        url = created.headers["Location"]
        notice_id = url.rsplit("/", 1)[-1]
        self.assertEqual(self.client.get(f"/notice/{notice_id}/resolve").status_code, 405)
        for _ in range(2):
            response = self.client.post(f"/notice/{notice_id}/resolve", data={"csrf_token": self.csrf})
            self.assertEqual(response.status_code, 303)
        self.assertIn(b"Resolved", self.client.get(url).data)

    def test_invalid_csrf_token_rejected(self):
        response = self.client.post("/create", data=self._valid_form(csrf_token="wrong"))
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
