"""
Integration tests for FastAPI endpoints & REST response schemas.
"""

import unittest
from fastapi.testclient import TestClient
from echosense.product_app import app

class TestAPIRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_healthz_endpoint(self):
        """Verify /healthz returns healthy status and policy version."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["policy_version"], "1.0.0")

    def test_get_recommendations_endpoint(self):
        """Verify /api/recommendations returns recommendation list with factor scores."""
        response = self.client.get("/api/recommendations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(len(data["recommendations"]) > 0)

    def test_get_autopilot_queue_endpoint(self):
        """Verify /api/autopilot returns 5-track Autopilot queue preview."""
        response = self.client.get("/api/autopilot")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(len(data["queue"]) <= 5)

    def test_verified_skip_endpoint(self):
        """Verify /api/skip performs verified skip and returns now playing track."""
        response = self.client.post("/api/skip")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["verified_skip"])

    def test_consent_deletion_endpoint(self):
        """Verify /api/consent/delete returns valid deletion receipt (AC-PRV-03)."""
        response = self.client.post("/api/consent/delete")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("receipt_id", data["receipt"])

if __name__ == '__main__':
    unittest.main()
