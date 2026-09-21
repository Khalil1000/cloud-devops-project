import contextlib
import io
import json
import unittest

from app.app import create_app


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "APP_VERSION": "test-release"})
        self.client = self.app.test_client()

    def test_home_shows_release_and_message(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"test-release", response.data)
        self.assertIn(b"Hello from my cloud project!", response.data)

    def test_release_endpoint_identifies_deployed_build(self):
        response = self.client.get("/version")
        self.assertEqual(response.json["version"], "test-release")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_liveness_remains_ok_when_readiness_fails(self):
        self.app.config["FORCE_NOT_READY"] = True
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/readyz").status_code, 503)

    def test_normal_readiness(self):
        self.assertEqual(self.client.get("/readyz").json, {"status": "ready"})

    def test_error_exercise_is_disabled_by_default(self):
        self.assertEqual(self.client.post("/demo/error").status_code, 404)

    def test_error_exercise_requires_post(self):
        self.app.config["ENABLE_DEMO_ERRORS"] = True
        self.assertEqual(self.client.get("/demo/error").status_code, 405)

    def test_error_emits_structured_record_for_alarm(self):
        self.app.config["ENABLE_DEMO_ERRORS"] = True
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            response = self.client.post("/demo/error")
        record = json.loads(output.getvalue())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(record["event"], "request")
        self.assertEqual(record["level"], "ERROR")
        self.assertEqual(record["status"], 500)
        self.assertGreaterEqual(record["duration_ms"], 0)


if __name__ == "__main__":
    unittest.main()
