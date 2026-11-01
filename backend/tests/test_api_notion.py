"""Unit & Integration Tests for Notion Timetable Sync & Fallback (Phase 7)."""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.event import Event
from app.models.notion import NotionConnection, NotionSyncRecord
from app.models.user import User
from app.security.auth import create_access_token, hash_password


class CampusAINotionSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        user = cls.db.query(User).filter(User.email == "notion_test@campus.edu").first()
        if not user:
            user = User(
                email="notion_test@campus.edu",
                full_name="Notion Test Student",
                hashed_password=hash_password("testpass123"),
                is_active=True,
            )
            cls.db.add(user)
            cls.db.commit()
            cls.db.refresh(user)
        cls.user = user

        token = create_access_token({"sub": str(user.id), "email": user.email})
        cls.headers = {"Authorization": f"Bearer {token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_notion_sync_without_connection(self):
        """Verify sync gracefully falls back to local SQLite when no Notion database is connected."""
        # Ensure connection record is removed for clean test
        self.db.query(NotionConnection).filter(NotionConnection.user_id == self.user.id).delete()
        self.db.commit()

        res = self.client.post("/api/v1/notion/sync", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "FALLBACK_LOCAL")
        self.assertEqual(data["synced_events_count"], 0)
        self.assertIn("local database", data["message"])

    def test_02_notion_connect(self):
        """Authorize and persist Notion database connection."""
        payload = {
            "api_token": "secret_notion_integration_token_test_123",
            "database_id": "notion_db_academics_987654321",
        }
        res = self.client.post("/api/v1/notion/connect", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "CONNECTED")
        self.assertEqual(data["database_id"], "notion_db_academics_987654321")

        # Verify persisted in database
        conn = self.db.query(NotionConnection).filter(NotionConnection.user_id == self.user.id).first()
        self.assertIsNotNone(conn)
        self.assertEqual(conn.status, "CONNECTED")

    def test_03_notion_sync_with_confirmed_event(self):
        """Sync confirmed timetable changes with the connected Notion database."""
        # Seed a confirmed event for this test user
        test_event = Event(
            user_id=self.user.id,
            title="NLP Lab Session Shift",
            subject="Natural Language Processing",
            event_type="LAB",
            location="Room 205 (AI/NLP Lab)",
            status="CONFIRMED",
            start_at=datetime.utcnow() + timedelta(days=1),
            end_at=datetime.utcnow() + timedelta(days=1, hours=2),
        )
        self.db.add(test_event)
        self.db.commit()
        self.db.refresh(test_event)

        # Trigger sync
        res = self.client.post("/api/v1/notion/sync", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SYNCED")
        self.assertGreaterEqual(data["synced_events_count"], 1)

        # Verify sync record in database
        rec = self.db.query(NotionSyncRecord).filter(NotionSyncRecord.event_id == test_event.id).first()
        self.assertIsNotNone(rec)
        self.assertEqual(rec.sync_status, "SYNCED")
        self.assertIsNotNone(rec.notion_page_id)

    def test_04_get_notion_timetable(self):
        """Retrieve confirmed timetable entries indicating Notion synchronization state."""
        res = self.client.get("/api/v1/notion/timetable", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        entries = res.json()
        self.assertGreaterEqual(len(entries), 1)

        titles = [e["title"] for e in entries]
        self.assertIn("NLP Lab Session Shift", titles)
        synced_flag = any(e["notion_synced"] for e in entries if e["title"] == "NLP Lab Session Shift")
        self.assertTrue(synced_flag)


if __name__ == "__main__":
    unittest.main()
