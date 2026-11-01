"""Integration test suite for RAG Study Notes System & Chatbot (Phase 5)."""

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
from app.security.auth import create_access_token


class CampusAIRAGChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        user = cls.db.query(User).filter(User.email == "student_rag_test@campus.edu").first()
        if not user:
            from app.security.auth import hash_password
            user = User(
                email="student_rag_test@campus.edu",
                full_name="RAG Test Student",
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

    def test_01_index_sample_library(self):
        """Index the Semester 5 notes library (CN, OS, DBMS, NLP/ML)."""
        res = self.client.post("/api/v1/notes/index-samples", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreaterEqual(data["notes_indexed_count"], 4)

        # Verify notes list endpoint
        list_res = self.client.get("/api/v1/notes", headers=self.headers)
        self.assertEqual(list_res.status_code, 200)
        notes = list_res.json()
        self.assertGreaterEqual(len(notes), 4)

        titles = [n["title"] for n in notes]
        self.assertIn("Computer Networks", titles)
        self.assertIn("Operating Systems", titles)
        self.assertIn("Database Management Systems", titles)

    def test_02_query_computer_networks_tcp_vs_udp(self):
        """Query TCP vs UDP differences from Computer Networks notes."""
        payload = {
            "message": "What is the difference between TCP and UDP?",
            "subject_filter": "Computer Networks",
        }
        res = self.client.post("/api/v1/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["grounded"])
        self.assertGreaterEqual(data["confidence"], 0.70)
        self.assertGreaterEqual(len(data["sources"]), 1)

        source_titles = [s["title"] for s in data["sources"]]
        self.assertIn("Computer Networks", source_titles)
        self.assertIn("page_number", data["sources"][0])

        ans = data["answer"].lower()
        self.assertTrue("tcp" in ans and "udp" in ans)

    def test_03_query_dbms_acid_properties(self):
        """Query ACID transaction properties from DBMS notes."""
        payload = {
            "message": "Explain the ACID properties in database transactions",
            "subject_filter": None,
        }
        res = self.client.post("/api/v1/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["grounded"])
        self.assertGreaterEqual(data["confidence"], 0.70)
        source_titles = [s["title"] for s in data["sources"]]
        self.assertIn("Database Management Systems", source_titles)

        ans = data["answer"].lower()
        self.assertTrue("atomicity" in ans or "isolation" in ans or "durability" in ans)

    def test_04_query_operating_systems_deadlock(self):
        """Query Coffman deadlock conditions from Operating Systems notes."""
        payload = {
            "message": "What are the four necessary conditions for deadlocks in an operating system?",
            "subject_filter": "Operating Systems",
        }
        res = self.client.post("/api/v1/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["grounded"])
        ans = data["answer"].lower()
        self.assertTrue("mutual exclusion" in ans or "circular wait" in ans or "hold and wait" in ans)

    def test_05_campus_faq_retrieval(self):
        """Test fallback retrieval for campus directory questions."""
        payload = {
            "message": "Where is the library located?",
        }
        res = self.client.post("/api/v1/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["grounded"])
        self.assertIn("Ground Floor", data["answer"])
        self.assertEqual(data["sources"][0]["title"], "Campus AI Handbook")

    def test_06_hallucination_guardrail(self):
        """Verify out-of-domain nonsense is rejected without hallucinations."""
        payload = {
            "message": "How do quantum astrophysics culinary recipes bake extraterrestrial sourdough?",
        }
        res = self.client.post("/api/v1/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertFalse(data["grounded"])
        self.assertEqual(len(data["sources"]), 0)
        self.assertLessEqual(data["confidence"], 0.30)
        self.assertIn("could not find relevant information", data["answer"].lower())

    def test_07_upload_custom_note(self):
        """Test uploading a custom note file and querying it."""
        file_content = (
            "# Advanced Cryptography\n"
            "RSA algorithm is an asymmetric cryptographic algorithm relying on the practical difficulty "
            "of factoring the product of two large prime numbers. Key generation produces a public key (e, n) "
            "and a private decryption key (d, n)."
        )
        files = {
            "file": ("crypto_notes.txt", file_content.encode("utf-8"), "text/plain")
        }
        data = {
            "title": "Cryptography & Network Security",
            "subject_name": "Information Security",
        }
        upload_res = self.client.post(
            "/api/v1/notes/upload",
            data=data,
            files=files,
            headers=self.headers,
        )
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.json()
        self.assertGreaterEqual(upload_data["chunks_indexed"], 1)

        # Query the newly uploaded note
        chat_res = self.client.post(
            "/api/v1/chat",
            json={"message": "How does the RSA algorithm work in cryptography?"},
            headers=self.headers,
        )
        self.assertEqual(chat_res.status_code, 200)
        chat_data = chat_res.json()
        self.assertTrue(chat_data["grounded"])
        self.assertIn("rsa", chat_data["answer"].lower())


if __name__ == "__main__":
    unittest.main()
