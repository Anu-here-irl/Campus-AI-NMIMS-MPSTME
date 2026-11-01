"""End-to-End System Integration Test for Campus AI (Phase 8).
Simulates a full student lifecycle:
Registration -> Email Ingestion -> NLP Classification & Entity Extraction ->
Timetable Proposal Generation -> Student Confirmation -> Notion Sync ->
RAG Chatbot Study Q&A -> Indoor Campus Navigation -> Dashboard Stats.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.email import Email
from app.models.event import Event
from app.models.notion import NotionConnection
from app.models.user import User
from app.services.notes_indexer import notes_indexer


class CampusAIE2EIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        cls.unique_suffix = int(datetime.utcnow().timestamp())

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_full_student_journey_e2e(self):
        """Execute end-to-end multi-service student journey across all Campus AI features."""
        student_email = f"e2e_student_{self.unique_suffix}@campus.edu"
        password = "e2ePassword123!"

        # =========================================================================
        # Step 1: User Registration & Authentication
        # =========================================================================
        reg_res = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": student_email,
                "password": password,
                "full_name": "E2E Test Student",
            },
        )
        self.assertIn(reg_res.status_code, [200, 201])

        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": student_email, "password": password},
        )
        self.assertEqual(login_res.status_code, 200)
        auth_data = login_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = auth_data["user"]["id"]

        # =========================================================================
        # Step 2: Email Ingestion & NLP Classification
        # =========================================================================
        email_payload = {
            "subject": "URGENT: Machine Learning Lecture Relocation to Room 204",
            "sender": "ANJALI.UPADHYAY43@nmims.in",
            "body": (
                "Dear Students,\n\n"
                "Please note that tomorrow's Machine Learning lecture has been moved from Classroom 101 "
                "to Classroom 204 (Smart Lecture Theater) on October 30, 2026 at 11:30 AM due to scheduled maintenance.\n"
                "Attendance is mandatory.\n\nRegards,\nAcademic Coordinator"
            ),
            "provider_message_id": f"msg_e2e_{self.unique_suffix}",
        }
        ingest_res = self.client.post("/api/v1/emails/sync", json=email_payload, headers=headers)
        self.assertEqual(ingest_res.status_code, 201)
        email_data = ingest_res.json()
        self.assertEqual(email_data["importance"], "HIGH")
        self.assertIn("CLASSROOM", email_data["category"])

        # Check extracted entities and proposal
        entities = email_data.get("entities", [])
        self.assertGreater(len(entities), 0)
        self.assertIsNotNone(email_data.get("proposed_event"))
        self.assertIn("204", email_data["proposed_event"]["new_location"])

        # =========================================================================
        # Step 3: Timetable Proposals Review & Confirmation Flow
        # =========================================================================
        props_res = self.client.get("/api/v1/events/proposals", headers=headers)
        self.assertEqual(props_res.status_code, 200)
        proposals = props_res.json()
        self.assertGreaterEqual(len(proposals), 1)

        target_prop = proposals[0]
        prop_id = target_prop["id"]
        self.assertEqual(target_prop["status"], "PROPOSED")

        # Confirm the proposal
        confirm_res = self.client.post(
            f"/api/v1/events/{prop_id}/confirm",
            json={"action": "confirm", "updated_location": "Classroom 204"},
            headers=headers,
        )
        self.assertEqual(confirm_res.status_code, 200)
        confirmed_data = confirm_res.json()
        self.assertEqual(confirmed_data["status"], "CONFIRMED")
        self.assertIn("204", confirmed_data["location"])

        # =========================================================================
        # Step 4: Notion Timetable Synchronization
        # =========================================================================
        # Connect Notion
        self.client.post(
            "/api/v1/notion/connect",
            json={"api_token": "notion_test_secret", "database_id": "notion_e2e_db"},
            headers=headers,
        )
        sync_res = self.client.post("/api/v1/notion/sync", headers=headers)
        self.assertEqual(sync_res.status_code, 200)
        sync_data = sync_res.json()
        self.assertEqual(sync_data["status"], "SYNCED")
        self.assertGreaterEqual(sync_data["synced_events_count"], 1)

        # =========================================================================
        # Step 5: RAG Study Assistant Q&A
        # =========================================================================
        # Seed Semester 5 notes for this student
        notes_indexer.index_sample_library(self.db, user_id)

        # Ask study question on Operating Systems deadlock
        chat_res = self.client.post(
            "/api/v1/chat",
            json={"message": "What are the Coffman conditions for deadlock in Operating Systems?"},
            headers=headers,
        )
        self.assertEqual(chat_res.status_code, 200)
        chat_data = chat_res.json()
        self.assertTrue(chat_data["grounded"])
        self.assertGreater(len(chat_data["sources"]), 0)
        self.assertEqual(chat_data["sources"][0]["title"], "Operating Systems")

        # =========================================================================
        # Step 6: Indoor Campus Navigation
        # =========================================================================
        # Navigate from Ground Floor Central Library (002) to rescheduled room (204)
        route_res = self.client.get("/api/v1/campus/routes?from_room=002&to_room=204", headers=headers)
        self.assertEqual(route_res.status_code, 200)
        route_data = route_res.json()
        self.assertGreater(route_data["total_distance"], 30.0)
        self.assertGreaterEqual(len(route_data["steps"]), 3)
        self.assertIn("Library", route_data["from_room"])
        self.assertIn("204", route_data["to_room"])

        # =========================================================================
        # Step 7: Dashboard Unified Statistics
        # =========================================================================
        dash_res = self.client.get("/api/v1/dashboard", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertGreaterEqual(dash_data["unread_email_count"], 1)
        self.assertGreaterEqual(dash_data["total_email_count"], 1)
        self.assertGreaterEqual(len(dash_data["high_priority_emails"]), 1)
        self.assertGreaterEqual(len(dash_data["upcoming_schedule"]), 1)
        self.assertEqual(dash_data["pending_proposals_count"], 0)


if __name__ == "__main__":
    unittest.main()
