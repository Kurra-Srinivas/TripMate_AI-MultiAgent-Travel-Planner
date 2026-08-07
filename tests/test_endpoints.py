import sys
from pathlib import Path
import unittest

# Ensure project root directory is in sys.path when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi.testclient import TestClient
from app import app


class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test the /health API endpoint returns 200 OK and expected features."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("TripMate AI API is running", data.get("message", ""))
        self.assertIn("supervisor_agent", data.get("features", []))

    def test_travel_endpoint_empty_message(self):
        """Test validation error response on empty prompt input."""
        response = self.client.post("/api/travel", json={"message": "   "})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("Message cannot be empty", data.get("error", ""))

    def test_travel_approve_endpoint_missing_feedback(self):
        """Test validation error response when rejection feedback is missing."""
        response = self.client.post(
            "/api/travel/approve",
            json={"thread_id": "test_thread_123", "approved": False, "feedback": ""},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("revision feedback", data.get("error", "").lower())


if __name__ == "__main__":
    unittest.main()
