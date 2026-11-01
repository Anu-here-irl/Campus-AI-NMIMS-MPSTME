"""Comprehensive unit tests for Campus AI NLP module.

Combines Person 1's baseline regression tests with Phase 1 additions:
- Normalized ISO date parsing
- Standardized time formatting
- Rich entity extraction
- Timetable proposal synthesis
- Uncertainty & review flag semantics
"""

import sys
import unittest
from pathlib import Path

NLP_DIR = Path(__file__).resolve().parent
if str(NLP_DIR) not in sys.path:
    sys.path.insert(0, str(NLP_DIR))

from inference import process_email, UNCERTAINTY_THRESHOLDS
from entity_extraction import normalize_date, normalize_time, extract_deadline_date


class CampusAINLPComprehensiveTests(unittest.TestCase):
    # --- Regression Tests from Baseline ---

    def test_normal_email_returns_classifications_and_dates(self):
        res = process_email(
            subject="Exam and assignment notice",
            body="The exam will take place on 20 August 2026. Submit the assignment by 22 August 2026.",
            sender_role="FACULTY",
        )
        self.assertIn("category", res)
        self.assertIn("importance", res)
        self.assertIn("category_confidence", res)
        self.assertIn("importance_confidence", res)
        self.assertEqual(res["dates"], ["20 August 2026", "22 August 2026"])
        self.assertEqual(res["times"], [])
        self.assertTrue(res["has_deadline"])
        self.assertEqual(res["deadline_date"], "22 August 2026")
        self.assertFalse(res["has_classroom_change"])
        self.assertIsNone(res["old_location"])
        self.assertIsNone(res["new_location"])
        self.assertTrue(res["has_exam"])
        self.assertTrue(res["has_assignment"])
        self.assertIn("submit", res["action_items"])
        self.assertIn("2026-08-20", res["normalized_dates"])
        self.assertIn("2026-08-22", res["normalized_dates"])

    def test_unavailable_gold_fields_are_not_required(self):
        res = process_email(
            subject="Brief note",
            body="Meeting tomorrow at 10 AM in Seminar Hall.",
            sender_role=None,
        )
        self.assertIsInstance(res["category"], str)
        self.assertIsInstance(res["importance"], str)
        self.assertIsInstance(res["category_confidence"], float)
        self.assertIsInstance(res["importance_confidence"], float)

    def test_empty_inputs_are_supported(self):
        res = process_email(subject="", body=None, sender_role=None)
        self.assertIsInstance(res["category"], str)
        self.assertIsInstance(res["importance"], str)
        self.assertTrue(res["uncertain"])
        self.assertTrue(res["review_recommended"])

    def test_malformed_input_types_raise(self):
        with self.assertRaises(TypeError):
            process_email(subject=123, body="Sample")
        with self.assertRaises(TypeError):
            process_email(subject="Sample", body=["Not a string"])
        with self.assertRaises(TypeError):
            process_email(subject="Sample", body="Body", sender_role=999)

    def test_confidences_are_model_probabilities_and_uncertainty_is_additive(self):
        res = process_email(
            subject="General update",
            body="Please find the attached newsletter.",
            sender_role="ADMIN",
        )
        self.assertGreaterEqual(res["category_confidence"], 0.0)
        self.assertLessEqual(res["category_confidence"], 1.0)
        self.assertGreaterEqual(res["importance_confidence"], 0.0)
        self.assertLessEqual(res["importance_confidence"], 1.0)
        expected_uncertain = (
            res["category_confidence"] < UNCERTAINTY_THRESHOLDS["category"]
            or res["importance_confidence"] < UNCERTAINTY_THRESHOLDS["importance"]
        )
        self.assertEqual(res["uncertain"], expected_uncertain)

    def test_no_date_does_not_invent_deadline(self):
        res = process_email(
            subject="Urgent action required",
            body="Submit the verification form immediately without delay.",
            sender_role="FACULTY",
        )
        self.assertFalse(res["has_deadline"])
        self.assertIsNone(res["deadline_date"])

    def test_event_date_is_not_assumed_to_be_a_deadline(self):
        res = process_email(
            subject="Annual sports meet",
            body="The annual sports meet will take place on 22 August 2026 in the auditorium.",
            sender_role="ADMIN",
        )
        self.assertEqual(res["dates"], ["22 August 2026"])
        self.assertFalse(res["has_deadline"])
        self.assertIsNone(res["deadline_date"])

    def test_deadline_extracts_date_and_action_cue(self):
        res = process_email(
            subject="Assignment submission",
            body="Submit your completed report by 22 August 2026.",
            sender_role="FACULTY",
        )
        self.assertTrue(res["has_deadline"])
        self.assertEqual(res["deadline_date"], "22 August 2026")
        self.assertIn("submit", res["action_items"])

    def test_hall_ticket_submission_before_date_is_deadline(self):
        res = process_email(
            subject="Hall ticket collection",
            body="Collect your hall ticket before 22 August 2026.",
            sender_role="ADMIN",
        )
        self.assertTrue(res["has_deadline"])
        self.assertEqual(res["deadline_date"], "22 August 2026")
        self.assertIn("collect", res["action_items"])

    def test_multiple_dates_choose_only_explicit_deadline(self):
        res = process_email(
            subject="Project schedule",
            body=(
                "The project presentation is on 15 August 2026. "
                "Submit the written draft by 22 August 2026."
            ),
            sender_role="FACULTY",
        )
        self.assertEqual(res["dates"], ["15 August 2026", "22 August 2026"])
        self.assertTrue(res["has_deadline"])
        self.assertEqual(res["deadline_date"], "22 August 2026")

    def test_classroom_change_extracts_old_and_new_locations(self):
        res = process_email(
            subject="Classroom reallocation",
            body="Lecture shifted from Room 101 to Lab 3 due to maintenance.",
            sender_role="FACULTY",
        )
        self.assertTrue(res["has_classroom_change"])
        self.assertEqual(res["old_location"], "Room 101")
        self.assertEqual(res["new_location"], "Lab 3")

    def test_classroom_change_without_date_is_not_a_deadline(self):
        res = process_email(
            subject="Location update",
            body="The seminar has been moved to Seminar Hall from Room 204.",
            sender_role="ADMIN",
        )
        self.assertTrue(res["has_classroom_change"])
        self.assertEqual(res["old_location"], "Room 204")
        self.assertEqual(res["new_location"], "Seminar Hall")
        self.assertFalse(res["has_deadline"])
        self.assertIsNone(res["deadline_date"])

    # --- Phase 1 Enhancement Tests ---

    def test_iso_date_normalization(self):
        self.assertEqual(normalize_date("22 August 2026"), "2026-08-22")
        self.assertEqual(normalize_date("22nd August 2026"), "2026-08-22")
        self.assertEqual(normalize_date("1st September 2026"), "2026-09-01")
        self.assertEqual(normalize_date("14/11/2026"), "2026-11-14")
        self.assertEqual(normalize_date("14-11-2026"), "2026-11-14")

    def test_time_normalization(self):
        self.assertEqual(normalize_time("10 AM"), "10:00 AM")
        self.assertEqual(normalize_time("02:30 PM"), "02:30 PM")
        self.assertEqual(normalize_time("9:15 AM"), "09:15 AM")

    def test_timetable_proposal_synthesis(self):
        res = process_email(
            subject="Computer Networks Exam Postponed",
            body="The Computer Networks examination scheduled for 12 November has been moved to Room 204 on 14 November at 10 AM.",
            sender_role="ADMIN",
        )
        self.assertIsNotNone(res["proposed_event"])
        proposal = res["proposed_event"]
        self.assertEqual(proposal["subject"], "Computer Networks")
        self.assertEqual(proposal["event_type"], "EXAM")
        self.assertEqual(proposal["new_location"], "Room 204")
        self.assertEqual(proposal["old_date"], "2026-11-12")
        self.assertEqual(proposal["new_date"], "2026-11-14")
        self.assertEqual(proposal["time"], "10:00 AM")
        self.assertIn("Date rescheduled", proposal["summary"])

    def test_structured_entities_extraction(self):
        res = process_email(
            subject="Database Management Systems Lab",
            body="The practical test will be held in Lab 2 on 18 October 2026 at 11:00 AM.",
            sender_role="FACULTY",
        )
        entities = res["entities"]
        types = {e["entity_type"] for e in entities}
        self.assertIn("DATE", types)
        self.assertIn("TIME", types)
        self.assertIn("ROOM", types)
        self.assertIn("SUBJECT", types)
        self.assertTrue(all("confidence" in e for e in entities))
        self.assertTrue(all("normalized_value" in e for e in entities))


if __name__ == "__main__":
    unittest.main()
