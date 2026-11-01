"""Unit and integration tests for Google Calendar OAuth 2.0 and API integration."""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.calendar import GoogleCalendarToken
from app.models.user import User
from app.services.calendar_service import GoogleCalendarService, calendar_service
from app.security.auth import create_access_token
from app.config import settings


class GoogleCalendarOAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Ensure test user exists
        user = cls.db.query(User).filter(User.email == "student_cal_test@campus.edu").first()
        if not user:
            user = User(
                email="student_cal_test@campus.edu",
                full_name="Calendar Test Student",
                hashed_password="hashed_pw_dummy",
                is_active=True,
            )
            cls.db.add(user)
            cls.db.commit()
            cls.db.refresh(user)
        cls.test_user = user

        token = create_access_token({"sub": user.id, "email": user.email})
        cls.headers = {"Authorization": f"Bearer {token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_state_generation_and_validation(self):
        """Test cryptographic state generation, verification, and expiration logic."""
        user_id = self.test_user.id
        state = calendar_service.generate_oauth_state(user_id)
        self.assertIsInstance(state, str)
        self.assertIn(".", state)

        # Validate authentic state
        extracted_id = calendar_service.validate_oauth_state(state)
        self.assertEqual(extracted_id, user_id)

        # Validate tampered state raises 400
        tampered_state = state[:-3] + "xyz"
        with self.assertRaises(Exception):
            calendar_service.validate_oauth_state(tampered_state)

        # Validate expired state raises 400
        with patch("time.time", return_value=1000000.0):
            old_state = calendar_service.generate_oauth_state(user_id)
        with patch("time.time", return_value=1000000.0 + 1000):  # 1000 seconds later (> 900s limit)
            with self.assertRaises(Exception):
                calendar_service.validate_oauth_state(old_state)

    def test_02_auth_url_endpoint(self):
        """Test GET /api/v1/calendar/auth-url generates valid Google OAuth URL with exact scope and redirect URI."""
        res = self.client.get("/api/v1/calendar/auth-url", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("auth_url", data)
        self.assertIn("state", data)
        self.assertEqual(data["redirect_uri"], settings.GOOGLE_CALENDAR_REDIRECT_URI)

        auth_url = data["auth_url"]
        self.assertTrue(auth_url.startswith("https://accounts.google.com/o/oauth2/v2/auth"))
        self.assertIn(settings.GOOGLE_CALENDAR_CLIENT_ID, auth_url)
        self.assertIn("https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.readonly", auth_url)
        self.assertIn("response_type=code", auth_url)
        self.assertIn("access_type=offline", auth_url)

    def test_03_callback_error_handling(self):
        """Test GET /api/v1/calendar/callback error scenarios (denial, missing params, invalid state)."""
        # Google user denied permission
        denied_res = self.client.get("/api/v1/calendar/callback?error=access_denied")
        self.assertEqual(denied_res.status_code, 400)
        self.assertIn("denied", denied_res.json()["detail"].lower())

        # Missing state / code
        missing_res = self.client.get("/api/v1/calendar/callback")
        self.assertEqual(missing_res.status_code, 400)

        # Invalid state
        invalid_state_res = self.client.get("/api/v1/calendar/callback?code=fake_code_123&state=invalid.state")
        self.assertEqual(invalid_state_res.status_code, 400)

    @patch.object(GoogleCalendarService, "exchange_code_for_tokens")
    def test_04_callback_success_and_secure_storage(self, mock_exchange):
        """Test successful OAuth callback, token storage, and secret shielding."""
        mock_exchange.return_value = {
            "access_token": "mock_google_access_token_abc123",
            "refresh_token": "mock_google_refresh_token_xyz987",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "https://www.googleapis.com/auth/calendar.readonly",
        }

        # Generate valid state for test user
        state = calendar_service.generate_oauth_state(self.test_user.id)

        # Call the callback endpoint
        callback_res = self.client.get(
            f"/api/v1/calendar/callback?code=google_auth_code_sample&state={state}"
        )
        self.assertEqual(callback_res.status_code, 200)
        json_data = callback_res.json()
        self.assertEqual(json_data["status"], "CONNECTED")
        # Ensure tokens are never exposed in JSON response
        self.assertNotIn("access_token", json_data)
        self.assertNotIn("refresh_token", json_data)

        # Verify token is stored securely in SQLite
        token_rec = self.db.query(GoogleCalendarToken).filter(GoogleCalendarToken.user_id == self.test_user.id).first()
        self.assertIsNotNone(token_rec)
        self.assertEqual(token_rec.access_token, "mock_google_access_token_abc123")
        self.assertEqual(token_rec.refresh_token, "mock_google_refresh_token_xyz987")
        self.assertTrue(token_rec.is_active)

        # Check status endpoint - must NOT reveal secret tokens
        status_res = self.client.get("/api/v1/calendar/status", headers=self.headers)
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertTrue(status_data["is_connected"])
        self.assertNotIn("access_token", status_data)
        self.assertNotIn("refresh_token", status_data)
        self.assertIn("expires_at", status_data)

    @patch.object(GoogleCalendarService, "fetch_calendar_events")
    def test_05_events_and_sync(self, mock_fetch):
        """Test calendar events retrieval and synchronization into Campus AI timetable."""
        mock_events = [
            {
                "id": "cal_evt_101",
                "summary": "Computer Networks Lecture: Module 4",
                "description": "Room 204 with Prof. Sharma",
                "location": "Room 204",
                "start_time": "2026-11-15T10:00:00Z",
                "end_time": "2026-11-15T11:30:00Z",
                "html_link": "https://calendar.google.com/event?eid=101",
            },
            {
                "id": "cal_evt_102",
                "summary": "Natural Language Processing Midterm Exam",
                "description": "Room 101 Exam Hall",
                "location": "Room 101",
                "start_time": "2026-11-20T14:00:00Z",
                "end_time": "2026-11-20T16:00:00Z",
                "html_link": "https://calendar.google.com/event?eid=102",
            },
        ]
        mock_fetch.return_value = mock_events

        # List events endpoint
        events_res = self.client.get("/api/v1/calendar/events", headers=self.headers)
        self.assertEqual(events_res.status_code, 200)
        events_data = events_res.json()
        self.assertEqual(events_data["total_count"], 2)
        self.assertEqual(events_data["events"][0]["summary"], "Computer Networks Lecture: Module 4")

        # Sync events to timetable
        sync_res = self.client.post("/api/v1/calendar/sync", headers=self.headers)
        self.assertEqual(sync_res.status_code, 200)
        sync_data = sync_res.json()
        self.assertGreaterEqual(sync_data["synced_to_events_count"], 2)

    def test_06_disconnect(self):
        """Test disconnecting Google Calendar account."""
        del_res = self.client.delete("/api/v1/calendar/disconnect", headers=self.headers)
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "DISCONNECTED")

        # Verify status is now disconnected
        status_res = self.client.get("/api/v1/calendar/status", headers=self.headers)
        self.assertEqual(status_res.status_code, 200)
        self.assertFalse(status_res.json()["is_connected"])


if __name__ == "__main__":
    unittest.main()
