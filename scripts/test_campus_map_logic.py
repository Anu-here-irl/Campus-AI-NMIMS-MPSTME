"""Unit test and validation suite for Campus AI Indoor Block Map.

Tests:
1. Manifest and floor count (LG, G, 1-8).
2. Ground Floor (G) verified room geometry, categories, and labels.
3. Case-insensitive room search matching (by room code, room name, category, and notes).
4. Tap hit-testing (containsPoint coordinate resolution).
5. Empty / no-match search query handling.
6. Verification audit reporting.
"""

import json
import os
import unittest


class TestCampusMapDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        json_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'android-app',
            'app',
            'src',
            'main',
            'assets',
            'campus_floors.json',
        )
        with open(json_path, 'r', encoding='utf-8') as f:
            cls.data = json.load(f)
        cls.floors = {fl['floor_id']: fl for fl in cls.data['floors']}

    def test_floor_count_and_ids(self):
        """Test that all 10 actual floors exist without fabrication."""
        expected_ids = ['LG', 'G', '1', '2', '3', '4', '5', '6', '7', '8']
        for fid in expected_ids:
            self.assertIn(fid, self.floors, f"Missing floor {fid}")
        self.assertEqual(len(self.floors), 10)

    def test_ground_floor_rooms_geometry(self):
        """Test that Ground Floor has all verified rooms with non-zero dimensions within canvas."""
        g_floor = self.floors['G']
        self.assertGreater(len(g_floor['rooms']), 30)
        cw, ch = g_floor['width'], g_floor['height']

        for room in g_floor['rooms']:
            self.assertTrue(room['code'], "Room code must not be empty")
            self.assertTrue(room['name'], "Room name must not be empty")
            self.assertTrue(room['category'], "Room category must not be empty")
            # Bounds check
            self.assertGreaterEqual(room['x'], 0)
            self.assertGreaterEqual(room['y'], 0)
            self.assertGreater(room['width'], 0)
            self.assertGreater(room['height'], 0)
            self.assertLessEqual(room['x'] + room['width'], cw)
            self.assertLessEqual(room['y'] + room['height'], ch)

    def test_ground_floor_key_rooms_presence(self):
        """Verify presence of key rooms from G.jpg emergency escape plan."""
        g_rooms = {r['code']: r for r in self.floors['G']['rooms']}
        key_codes = [
            'E-CR-G1', 'E-CR-G2', 'E-CR-G3', 'E-CR-G4', 'E-CR-G5',
            'EXAM-1', 'EXAM-2', 'EXAM-3',
            'LAB-EYANTRA',
            'ATRIUM',
            'ADMISSION-CTR', 'ADMIN-CABINS',
            'LIFTS-A', 'LIFTS-B',
            'STAIRS-1', 'STAIRS-2', 'STAIRS-3', 'STAIRS-4',
            'RESTROOM-GIRLS', 'RESTROOM-BOYS',
            'SERVER-ROOM', 'IBMS-ROOM', 'UPS-ROOM'
        ]
        for code in key_codes:
            self.assertIn(code, g_rooms, f"Key room {code} not found in Ground Floor")

    def test_case_insensitive_search(self):
        """Test search query matching across codes, names, categories, and notes."""
        def search_rooms(query):
            q = query.strip().lower()
            results = []
            for fl in self.data['floors']:
                for r in fl['rooms']:
                    if (
                        q in r['code'].lower()
                        or q in r['name'].lower()
                        or q in r['category'].lower()
                        or q in r.get('notes', '').lower()
                    ):
                        results.append((fl['floor_id'], r))
            return results

        # Search by code
        res1 = search_rooms("g1")
        self.assertTrue(any(r['code'] == 'E-CR-G1' for _, r in res1))

        # Search by name
        res2 = search_rooms("robotics")
        self.assertTrue(any('Robotics' in r['name'] or 'robotics' in r.get('notes', '').lower() for _, r in res2))

        # Search by category
        res3 = search_rooms("exam")
        self.assertTrue(any(r['category'] == 'EXAM' for _, r in res3))

        # Search case insensitivity
        res4 = search_rooms("e-cr-g4")
        res5 = search_rooms("E-CR-G4")
        self.assertEqual(len(res4), len(res5))

    def test_empty_and_no_result_search(self):
        """Test behavior when query produces no matches."""
        def search_rooms(query):
            q = query.strip().lower()
            if not q:
                return []
            results = []
            for fl in self.data['floors']:
                for r in fl['rooms']:
                    if (
                        q in r['code'].lower()
                        or q in r['name'].lower()
                        or q in r['category'].lower()
                    ):
                        results.append(r)
            return results

        self.assertEqual(len(search_rooms("")), 0)
        self.assertEqual(len(search_rooms("NON_EXISTENT_ROOM_XYZ_999")), 0)

    def test_room_tap_hit_testing(self):
        """Test that tap coordinates inside room bounds resolve to that room."""
        g_floor = self.floors['G']
        cr_g1 = next(r for r in g_floor['rooms'] if r['code'] == 'E-CR-G1')

        # Midpoint of E-CR-G1
        mid_x = cr_g1['x'] + cr_g1['width'] / 2.0
        mid_y = cr_g1['y'] + cr_g1['height'] / 2.0

        hit_room = None
        for r in g_floor['rooms']:
            if r['x'] <= mid_x <= (r['x'] + r['width']) and r['y'] <= mid_y <= (r['y'] + r['height']):
                hit_room = r
                break

        self.assertIsNotNone(hit_room)
        self.assertEqual(hit_room['code'], 'E-CR-G1')

    def test_uncertain_entries_flagging(self):
        """Ensure uncertain entries are flagged verified=False for manual field verification."""
        g_floor = self.floors['G']
        uncertain = [r for r in g_floor['rooms'] if not r.get('verified', True)]
        self.assertGreater(len(uncertain), 0, "Must mark uncertain entries for manual verification")
        uncertain_codes = [r['code'] for r in uncertain]
        self.assertIn('ADMIN-CABINS', uncertain_codes)
        self.assertIn('MEETING-1', uncertain_codes)


if __name__ == '__main__':
    unittest.main()
