"""Unit & Integration Tests for Campus AI Indoor Navigation & Pathfinding (Phase 6)."""

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.campus import CampusFloor, CampusRoom
from app.services.campus_service import campus_service


class CampusAINavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        campus_service.seed_campus_data_if_empty(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_get_all_floors(self):
        """Verify all 4 college floors and attached rooms are returned."""
        res = self.client.get("/api/v1/campus/floors")
        self.assertEqual(res.status_code, 200)
        floors = res.json()
        self.assertGreaterEqual(len(floors), 4)

        names = [f["floor_name"] for f in floors]
        self.assertIn("Ground Floor", names)
        self.assertIn("First Floor", names)
        self.assertIn("Second Floor", names)
        self.assertIn("Third Floor", names)

        # Check rooms are embedded
        ground_floor = next(f for f in floors if f["floor_order"] == 0)
        self.assertGreater(len(ground_floor["rooms"]), 0)
        ground_codes = [r["room_code"] for r in ground_floor["rooms"]]
        self.assertIn("001", ground_codes)  # Auditorium
        self.assertIn("002", ground_codes)  # Central Library

    def test_02_get_rooms_by_floor(self):
        """Retrieve rooms belonging to a specific floor and verify 404 on invalid floor."""
        # Query Ground Floor rooms
        first_floor = self.db.query(CampusFloor).filter(CampusFloor.floor_order == 1).first()
        self.assertIsNotNone(first_floor)

        res = self.client.get(f"/api/v1/campus/floors/{first_floor.id}/rooms")
        self.assertEqual(res.status_code, 200)
        rooms = res.json()
        self.assertGreater(len(rooms), 0)
        for r in rooms:
            self.assertEqual(r["floor_id"], first_floor.id)

        # 404 for nonexistent floor
        err_res = self.client.get("/api/v1/campus/floors/99999/rooms")
        self.assertEqual(err_res.status_code, 404)

    def test_03_search_rooms(self):
        """Search rooms by code, full name, or room type."""
        # Search by room code "204"
        res_code = self.client.get("/api/v1/campus/search?q=204")
        self.assertEqual(res_code.status_code, 200)
        data_code = res_code.json()
        self.assertGreaterEqual(len(data_code), 1)
        self.assertEqual(data_code[0]["room_code"], "204")

        # Search by name "Library"
        res_name = self.client.get("/api/v1/campus/search?q=Library")
        self.assertEqual(res_name.status_code, 200)
        data_name = res_name.json()
        self.assertGreaterEqual(len(data_name), 1)
        self.assertIn("Library", data_name[0]["room_name"])

        # Search by type "LAB"
        res_type = self.client.get("/api/v1/campus/search?q=LAB")
        self.assertEqual(res_type.status_code, 200)
        data_type = res_type.json()
        self.assertGreaterEqual(len(data_type), 3)

    def test_04_same_floor_navigation(self):
        """Test corridor routing between two classrooms on the Second Floor."""
        res = self.client.get("/api/v1/campus/routes?from_room=201&to_room=204")
        self.assertEqual(res.status_code, 200)
        route = res.json()

        self.assertIn("201", route["from_room"])
        self.assertIn("204", route["to_room"])
        self.assertGreater(route["total_distance"], 10.0)
        self.assertGreaterEqual(len(route["steps"]), 3)

        # Check turn-by-turn steps
        instructions = [s["instruction"] for s in route["steps"]]
        self.assertTrue(any("corridor" in inst.lower() for inst in instructions))
        self.assertTrue(any("arrive" in inst.lower() for inst in instructions))

        # Check waypoint nodes
        self.assertGreaterEqual(len(route["nodes"]), 2)

    def test_05_cross_floor_navigation(self):
        """Test inter-floor routing from Ground Floor (Library) to 2nd Floor (AI/NLP Lab)."""
        res = self.client.get("/api/v1/campus/routes?from_room=002&to_room=205")
        self.assertEqual(res.status_code, 200)
        route = res.json()

        self.assertIn("Library", route["from_room"])
        self.assertIn("AI/NLP", route["to_room"])
        # Ground Floor to Floor 2 is 2 floors vertical distance (2 * 15m = 30m) + horizontal walks
        self.assertGreaterEqual(route["total_distance"], 45.0)

        instructions = [s["instruction"] for s in route["steps"]]
        self.assertTrue(any("stairs" in inst.lower() or "elevator" in inst.lower() for inst in instructions))
        self.assertTrue(any("ascend" in inst.lower() for inst in instructions))

        # Check stairs waypoints included
        stairs_nodes = [n for n in route["nodes"] if n.get("type") == "STAIRS"]
        self.assertGreaterEqual(len(stairs_nodes), 2)

    def test_06_route_by_descriptive_name(self):
        """Verify routing works using natural descriptive names (e.g. 'Central Library')."""
        res = self.client.get("/api/v1/campus/routes?from_room=Central Library&to_room=Classroom 204")
        self.assertEqual(res.status_code, 200)
        route = res.json()
        self.assertIn("Library", route["from_room"])
        self.assertIn("204", route["to_room"])

    def test_07_route_with_room_prefix(self):
        """Verify routing gracefully handles 'Room 101' to 'Room 204' prefix format."""
        res = self.client.get("/api/v1/campus/routes?from_room=Room 101&to_room=Room 204")
        self.assertEqual(res.status_code, 200)
        route = res.json()
        self.assertIn("101", route["from_room"])
        self.assertIn("204", route["to_room"])

    def test_08_invalid_room_error(self):
        """Verify 404 error returned when starting or destination room does not exist."""
        res = self.client.get("/api/v1/campus/routes?from_room=99999&to_room=204")
        self.assertEqual(res.status_code, 404)
        err = res.json()
        self.assertIn("detail", err)
        self.assertIn("99999", err["detail"])


if __name__ == "__main__":
    unittest.main()
