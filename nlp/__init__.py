"""Campus AI NLP Package."""

from .inference import process_email, MODEL_VERSION
from .preprocessing import build_email_text, clean_email, classification_text
from .entity_extraction import (
    extract_entities,
    extract_deadline_date,
    extract_locations,
    detect_timetable_proposal,
    normalize_date,
    normalize_time,
)

__all__ = [
    "process_email",
    "MODEL_VERSION",
    "build_email_text",
    "clean_email",
    "classification_text",
    "extract_entities",
    "extract_deadline_date",
    "extract_locations",
    "detect_timetable_proposal",
    "normalize_date",
    "normalize_time",
]
