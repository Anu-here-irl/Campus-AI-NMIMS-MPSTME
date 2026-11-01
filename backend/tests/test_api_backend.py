"""Comprehensive integration test suite for Campus AI Backend APIs."""

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User


class CampusAIBackendAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create all tables in test database
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    def test_01_health_and_root(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["nlp_model"], "v1.0-tfidf-logreg")

        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "healthy")

    def test_02_auth_register_and_login(self):
        # Register student
        payload = {
            "email": "student_test_1@campus.edu",
            "full_name": "Test Student",
            "password": "Password123!",
        }
        res = self.client.post("/api/v1/auth/register", json=payload)
        self.assertIn(res.status_code, (201, 400))  # 400 if already created

        # Login
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": "student_test_1@campus.edu", "password": "Password123!"},
        )
        self.assertEqual(login_res.status_code, 200)
        token_data = login_res.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "bearer")

        # Get profile with bearer token
        token = token_data["access_token"]
        me_res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], "student_test_1@campus.edu")

    def test_03_nlp_direct_predict(self):
        email_payload = {
            "subject": "Exam notice: Machine Learning test",
            "body": "The Machine Learning exam will take place on 22 August 2026. Submit your assignments before 20 August 2026.",
            "sender_role": "FACULTY",
        }
        res = self.client.post("/api/v1/nlp/predict", json=email_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("category", data)
        self.assertIn("importance", data)
        self.assertIn("22 August 2026", data["dates"])
        self.assertTrue(data["has_exam"])

    def test_04_email_ingestion_and_proposal_creation(self):
        # Email containing a timetable and classroom shift
        import time
        unique_id = f"msg-test-{int(time.time() * 1000)}"
        shift_email = {
            "provider_message_id": unique_id,
            "subject": "Rescheduled Computer Networks Exam",
            "body": "The Computer Networks examination scheduled for 12 November has been moved to Room 204 on 14 November at 10 AM.",
            "sender": "exam-cell@campus.edu",
            "sender_role": "ADMIN",
        }
        res = self.client.post("/api/v1/emails/sync", json=shift_email)
        self.assertEqual(res.status_code, 201)
        email_data = res.json()
        self.assertEqual(email_data["provider_message_id"], unique_id)
        self.assertIn(email_data["category"], ("EXAM", "CLASSROOM / TIMETABLE", "ADMINISTRATIVE"))
        self.assertIsNotNone(email_data["proposed_event"])

        # Check deduplication on re-ingesting the exact same provider_message_id
        dup_res = self.client.post("/api/v1/emails/sync", json=shift_email)
        self.assertEqual(dup_res.status_code, 201)
        self.assertEqual(dup_res.json()["id"], email_data["id"])

        # List emails
        list_res = self.client.get("/api/v1/emails")
        self.assertEqual(list_res.status_code, 200)
        self.assertGreaterEqual(list_res.json()["total"], 1)

    def test_05_proposals_confirm_flow(self):
        # Fetch pending proposals
        prop_res = self.client.get("/api/v1/events/proposals")
        self.assertEqual(prop_res.status_code, 200)
        proposals = prop_res.json()

        # If no proposal is pending due to prior tests, ingest one
        if not proposals:
            import time
            shift_email = {
                "provider_message_id": f"msg-prop-{int(time.time() * 1000)}",
                "subject": "Room Change Notice",
                "body": "The Database Systems class is moved to Room 102 on 15 November at 2 PM.",
                "sender": "exam-cell@campus.edu",
                "sender_role": "FACULTY",
            }
            self.client.post("/api/v1/emails/sync", json=shift_email)
            prop_res = self.client.get("/api/v1/events/proposals")
            proposals = prop_res.json()

        self.assertGreaterEqual(len(proposals), 1)

        target_id = proposals[0]["id"]


        # Confirm proposal
        confirm_res = self.client.post(
            f"/api/v1/events/{target_id}/confirm",
            json={"action": "confirm"},
        )
        self.assertEqual(confirm_res.status_code, 200)
        self.assertEqual(confirm_res.json()["status"], "CONFIRMED")

    def test_06_dashboard_summary(self):
        dash_res = self.client.get("/api/v1/dashboard")
        self.assertEqual(dash_res.status_code, 200)
        data = dash_res.json()
        self.assertIn("unread_email_count", data)
        self.assertIn("total_email_count", data)
        self.assertIn("high_priority_emails", data)
        self.assertIn("upcoming_schedule", data)

    def test_07_campus_map_and_routes(self):
        # Floors
        floors_res = self.client.get("/api/v1/campus/floors")
        self.assertEqual(floors_res.status_code, 200)
        floors = floors_res.json()
        self.assertGreaterEqual(len(floors), 4)

        # Room search
        search_res = self.client.get("/api/v1/campus/search?q=204")
        self.assertEqual(search_res.status_code, 200)
        rooms = search_res.json()
        self.assertTrue(any(r["room_code"] == "204" for r in rooms))

        # Route between rooms
        route_res = self.client.get("/api/v1/campus/routes?from_room=101&to_room=204")
        self.assertEqual(route_res.status_code, 200)
        route = route_res.json()
        self.assertGreater(len(route["steps"]), 0)
        self.assertGreater(route["total_distance"], 0.0)

    def test_08_notion_sync_flow(self):
        sync_res = self.client.post("/api/v1/notion/sync")
        self.assertEqual(sync_res.status_code, 200)
        self.assertIn(sync_res.json()["status"], ("SYNCED", "FALLBACK_LOCAL"))

    def test_09_chat_notes_and_campus_qa(self):
        # Ask question about library
        chat_res = self.client.post(
            "/api/v1/chat",
            json={"message": "Where is the library located and what are its timings?"},
        )
        self.assertEqual(chat_res.status_code, 200)
        data = chat_res.json()
        self.assertTrue(data["grounded"])
        self.assertIn("Library", data["answer"])


if __name__ == "__main__":
    unittest.main()
