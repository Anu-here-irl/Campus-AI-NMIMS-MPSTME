"""Campus AI Information Extraction & Entity Normalization Module.

Extracts dates, normalized dates, times, rooms/venues, subjects,
deadlines, action items, and generates structured timetable change proposals.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

# Date regular expression matching "20 August 2026", "October 30, 2026", "17 Oct 2026", "17th Oct", "10.09.2026", "12/11/2026", "14-11-2026"
DATE_RE = re.compile(
    r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    r"(?:\s+\d{4})?|"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?|"
    r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b",
    re.I,
)

# Time regular expression matching "10 AM", "10:30 PM", "02:00 PM", "11:15 AM"
TIME_RE = re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:AM|PM)\b", re.I)

LOCATION_PATTERN = (
    r"(?:Room\s+[A-Za-z0-9-]+|Classroom\s+[A-Za-z0-9-]+|Lecture Hall\s+[A-Za-z0-9-]+|Lab\s+[A-Za-z0-9-]+|Seminar Hall|"
    r"Conference Room\s+[A-Za-z0-9]+|MBA Block Room\s+\d+|Auditorium|Online)"
)
LOCATION_RE = re.compile(LOCATION_PATTERN, re.I)

ACTION_VERBS = (
    "submit", "register", "attend", "pay", "download", "verify", "report",
    "apply", "upload", "respond", "complete", "check", "contact", "collect",
    "return", "confirm", "clear", "select", "move", "ensure", "bring",
)

KNOWN_SUBJECTS = [
    # Full names first
    "Computer Networks",
    "Natural Language Processing",
    "Database Management Systems",
    "Deep Learning",
    "Mobile Application Development",
    "Intelligence Systems 2",
    "Intelligence Systems 1",
    "Drone Technology",
    "Drone Theory & Lab",
    "Drone Theory",
    "Drone Lab",
    "Intro to Forensic Science",
    "Introduction to Forensic Science",
    "Intro for Forensic Science",
    "Data Structures & Algorithms",
    "Data Structures",
    "Design and Analysis of Algorithms",
    "Machine Learning",
    "Computer Architecture",
    "Operating Systems",
    "Signal and Image Processing",
    "Signal & Image Processing",
    "Artificial Intelligence",
    # Acronyms & Subject codes
    "CN",
    "NLP",
    "DBMS",
    "DL",
    "MAD",
    "IS 2",
    "IS-II",
    "IS -II",
    "IS 1",
    "IS-I",
    "IS -I",
    "Drone",
    "Intro to FC",
    "IFS",
    "DAA",
    "DSA",
    "ML",
    "COA",
    "OS",
    "SIP",
    "AI",
]

MONTH_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9, "october": 10, "oct": 10,
    "november": 11, "nov": 11, "december": 12, "dec": 12
}


def normalize_date(raw_date: str, default_year: int = 2026) -> str | None:
    """Normalize raw date strings into ISO format YYYY-MM-DD."""
    cleaned = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", raw_date.strip(), flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Case 1: Numeric dd/mm/yyyy or dd-mm-yyyy or dd.mm.yyyy
    num_match = re.match(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$", cleaned)
    if num_match:
        day, month, year = int(num_match.group(1)), int(num_match.group(2)), int(num_match.group(3))
        if year < 100:
            year += 2000
        try:
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # Case 2: Named month (e.g., "20 August 2026" or "20 August")
    alpha_match = re.match(r"^(\d{1,2})\s+([A-Za-z]+)(?:\s+(\d{4}))?$", cleaned)
    if alpha_match:
        day = int(alpha_match.group(1))
        month_str = alpha_match.group(2).lower()
        year = int(alpha_match.group(3)) if alpha_match.group(3) else default_year
        month = MONTH_MAP.get(month_str)
        if month:
            try:
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None

    # Case 3: Named month first (e.g., "October 30, 2026" or "October 30")
    clean_commas = cleaned.replace(",", "")
    month_first_match = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:\s+(\d{4}))?$", clean_commas)
    if month_first_match:
        month_str = month_first_match.group(1).lower()
        day = int(month_first_match.group(2))
        year = int(month_first_match.group(3)) if month_first_match.group(3) else default_year
        month = MONTH_MAP.get(month_str)
        if month:
            try:
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None

    return None


def normalize_time(raw_time: str) -> str | None:
    """Normalize time strings like '10 AM' or '09:30 pm' into standard '10:00 AM'."""
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$", raw_time.strip(), re.I)
    if not match:
        return raw_time.upper()
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    meridiem = match.group(3).upper()
    return f"{hour:02d}:{minute:02d} {meridiem}"


def extract_locations(text: str) -> tuple[str | None, str | None]:
    """Extract (old_location, new_location) from text indicating classroom shifts."""
    match = re.search(
        rf"\b(?:shifted|moved|relocated)\s+from\s+({LOCATION_PATTERN})\s+to\s+({LOCATION_PATTERN})",
        text,
        flags=re.I,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()

    match = re.search(
        rf"\bmoved\s+to\s+({LOCATION_PATTERN}).*?\bfrom\s+({LOCATION_PATTERN})",
        text,
        flags=re.I,
    )
    if match:
        return match.group(2).strip(), match.group(1).strip()

    match = re.search(
        rf"\brelocated\s+to\s+({LOCATION_PATTERN}).*?\bdue to .*?\bin\s+({LOCATION_PATTERN})",
        text,
        flags=re.I,
    )
    if match:
        return match.group(2).strip(), match.group(1).strip()

    match = re.search(
        rf"\b(?:shifted|moved|relocated)\s+to\s+({LOCATION_PATTERN})",
        text,
        flags=re.I,
    )
    if match:
        return None, match.group(1).strip()

    match = re.search(r"\bconducted online\b", text, flags=re.I)
    if match:
        return None, "Online"

    return None, None


def extract_deadline_date(text: str) -> str | None:
    """Extract explicit deadline date governed by cue words like 'by', 'due', 'deadline'."""
    for match in DATE_RE.finditer(text):
        sentence_start = max(
            text.rfind(mark, 0, match.start()) for mark in ".!?\n"
        ) + 1
        sentence_ends = [
            text.find(mark, match.end())
            for mark in ".!?\n"
            if text.find(mark, match.end()) >= 0
        ]
        sentence_end = min(sentence_ends) if sentence_ends else len(text)
        before_date = text[sentence_start:match.start()]
        after_date = text[match.end():sentence_end]

        explicit_prefix = re.search(
            r"(?:\b(?:by|before|no later than)\s+(?:the\s+)?"
            r"|\b(?:due|deadline)\s*(?:date\s*)?(?:is|:|on)?\s*)$",
            before_date,
            flags=re.I,
        )
        explicit_suffix = re.match(
            r"\s*(?:is|was)?\s*(?:the\s+)?deadline\b",
            after_date,
            flags=re.I,
        )
        if explicit_prefix or explicit_suffix:
            return match.group(0)
    return None


def extract_subject(text: str) -> str | None:
    """Identify the academic subject mentioned in the text."""
    # Check known subjects
    for subj in KNOWN_SUBJECTS:
        if re.search(rf"\b{re.escape(subj)}\b", text, re.I):
            return subj

    # Heuristic pattern: e.g. "Computer Networks examination", "Advanced Java lecture"
    match = re.search(
        r"\b([A-Z][a-zA-Z\s]{2,25})\s+(?:examination|exam|lecture|class|practical|lab)\b",
        text,
    )
    if match:
        cand = match.group(1).strip()
        if cand.lower() not in ("the", "final", "upcoming", "scheduled", "postponed", "mid", "term", "regular"):
            return cand
    return None


def detect_timetable_proposal(
    text: str,
    category: str,
    dates: list[str],
    times: list[str],
    old_location: str | None,
    new_location: str | None,
) -> dict[str, Any] | None:
    """Detect if an email implies a schedule or classroom change and construct a proposal."""
    change_signals = (
        bool(old_location or new_location)
        or bool(re.search(r"\b(moved|shifted|rescheduled|postponed|preponed|relocated|cancelled)\b", text, re.I))
        or category in ("CLASSROOM / TIMETABLE", "TIMETABLE_CHANGE")
    )
    if not change_signals:
        return None

    subject = extract_subject(text) or "Class / Examination"
    event_type = "EXAM" if re.search(r"\b(exam|examination)\b", text, re.I) else "LECTURE"

    # Identify date changes (e.g. from 12 November to 14 November)
    date_shift_match = re.search(
        r"(?:scheduled for|from)\s+([A-Za-z0-9\s]+?)\s+(?:has been\s+)?(?:moved|postponed|rescheduled|shifted)\s+(?:to\s+)?.*?(?:on\s+)?([A-Za-z0-9\s]+)",
        text,
        re.I,
    )
    old_date = None
    new_date = None

    if date_shift_match:
        cand_old = DATE_RE.search(date_shift_match.group(1))
        cand_new = DATE_RE.search(date_shift_match.group(2))
        if cand_old:
            old_date = normalize_date(cand_old.group(0))
        if cand_new:
            new_date = normalize_date(cand_new.group(0))

    if not new_date and dates:
        new_date = normalize_date(dates[-1])
        if len(dates) > 1 and not old_date:
            old_date = normalize_date(dates[0])

    time_val = normalize_time(times[0]) if times else None

    # Summary description
    summary_parts = []
    if old_location and new_location:
        summary_parts.append(f"Location changed from {old_location} to {new_location}")
    elif new_location:
        summary_parts.append(f"Location set to {new_location}")

    if old_date and new_date and old_date != new_date:
        summary_parts.append(f"Date rescheduled from {old_date} to {new_date}")
    elif new_date:
        summary_parts.append(f"Date set to {new_date}")

    if time_val:
        summary_parts.append(f"Time: {time_val}")

    summary = "; ".join(summary_parts) if summary_parts else "Timetable schedule update requested"

    return {
        "title": f"{subject} Schedule Change",
        "subject": subject,
        "event_type": event_type,
        "old_date": old_date,
        "new_date": new_date,
        "time": time_val,
        "old_location": old_location,
        "new_location": new_location,
        "summary": summary,
        "raw_evidence": text[:300].strip(),
    }


def extract_entities(text: str) -> list[dict[str, Any]]:
    """Return a flat list of normalized entities extracted from text."""
    entities: list[dict[str, Any]] = []

    # Dates
    for d in DATE_RE.findall(text):
        entities.append({
            "entity_type": "DATE",
            "value": d,
            "normalized_value": normalize_date(d),
            "confidence": 0.95,
        })

    # Times
    for t in TIME_RE.findall(text):
        entities.append({
            "entity_type": "TIME",
            "value": t,
            "normalized_value": normalize_time(t),
            "confidence": 0.95,
        })

    # Locations
    for loc in set(LOCATION_RE.findall(text)):
        entities.append({
            "entity_type": "ROOM",
            "value": loc,
            "normalized_value": loc.strip(),
            "confidence": 0.90,
        })

    # Subject
    subj = extract_subject(text)
    if subj:
        entities.append({
            "entity_type": "SUBJECT",
            "value": subj,
            "normalized_value": subj,
            "confidence": 0.88,
        })

    return entities
