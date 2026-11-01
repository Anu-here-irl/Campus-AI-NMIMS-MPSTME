"""Campus AI Core NLP Inference Service.

Packages Person 1's trained models for category (12 classes) and importance (3 classes)
with entity extraction, date normalization, and timetable change proposal synthesis.
"""

from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.sparse import hstack

try:
    from .entity_extraction import (
        DATE_RE,
        TIME_RE,
        ACTION_VERBS,
        extract_deadline_date,
        extract_locations,
        extract_entities,
        detect_timetable_proposal,
        normalize_date,
    )
    from .preprocessing import (
        build_email_text,
        clean_email,
        classification_text,
    )
except ImportError:
    from entity_extraction import (
        DATE_RE,
        TIME_RE,
        ACTION_VERBS,
        extract_deadline_date,
        extract_locations,
        extract_entities,
        detect_timetable_proposal,
        normalize_date,
    )
    from preprocessing import (
        build_email_text,
        clean_email,
        classification_text,
    )

MODEL_DIR = Path(__file__).resolve().parent / "models"

UNCERTAINTY_THRESHOLDS = {
    "category": 0.35,
    "importance": 0.55,
}

MODEL_VERSION = "v1.0-tfidf-logreg"


@lru_cache(maxsize=1)
def _load_models():
    """Load cached model artifacts from local models directory."""
    if not (MODEL_DIR / "category_logreg_tfidf.joblib").exists():
        raise FileNotFoundError(f"Model artifacts not found in {MODEL_DIR}")

    category_vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.joblib")
    category_sender = joblib.load(MODEL_DIR / "sender_role_onehot.joblib")
    category_model = joblib.load(MODEL_DIR / "category_logreg_tfidf.joblib")

    importance_vectorizer = joblib.load(MODEL_DIR / "importance_inference_tfidf.joblib")
    importance_sender = joblib.load(MODEL_DIR / "importance_inference_sender_role.joblib")
    importance_model = joblib.load(MODEL_DIR / "importance_inference_logreg.joblib")

    return (
        category_vectorizer,
        category_sender,
        category_model,
        importance_vectorizer,
        importance_sender,
        importance_model,
    )


def process_email(
    subject: str | None,
    body: str | None,
    sender_role: str | None = None,
) -> dict[str, Any]:
    """Classify and extract actionable entities and proposals from an email."""
    if subject is not None and not isinstance(subject, str):
        raise TypeError("subject must be a string or None")
    if body is not None and not isinstance(body, str):
        raise TypeError("body must be a string or None")
    if sender_role is not None and not isinstance(sender_role, str):
        raise TypeError("sender_role must be a string or None")

    text = clean_email(build_email_text(subject, body))
    class_text = classification_text(text)
    role = sender_role.strip() if sender_role and sender_role.strip() else "-"

    (
        category_vectorizer,
        category_sender,
        category_model,
        importance_vectorizer,
        importance_sender,
        importance_model,
    ) = _load_models()

    category_features = hstack(
        [
            category_vectorizer.transform([class_text]),
            category_sender.transform(pd.DataFrame({"sender_role": [role]})),
        ]
    ).tocsr()

    importance_features = hstack(
        [
            importance_vectorizer.transform([class_text]),
            importance_sender.transform(pd.DataFrame({"sender_role": [role]})),
        ]
    ).tocsr()

    category_probabilities = category_model.predict_proba(category_features)[0]
    importance_probabilities = importance_model.predict_proba(importance_features)[0]

    category_index = int(category_probabilities.argmax())
    importance_index = int(importance_probabilities.argmax())

    category_name = str(category_model.classes_[category_index])
    importance_name = str(importance_model.classes_[importance_index])

    category_confidence = float(category_probabilities[category_index])
    importance_confidence = float(importance_probabilities[importance_index])

    uncertain = (
        category_confidence < UNCERTAINTY_THRESHOLDS["category"]
        or importance_confidence < UNCERTAINTY_THRESHOLDS["importance"]
    )

    dates = DATE_RE.findall(text)
    times = TIME_RE.findall(text)
    normalized_dates = [norm for d in dates if (norm := normalize_date(d))]

    deadline_date = extract_deadline_date(text)
    old_location, new_location = extract_locations(text)

    action_items = [
        verb
        for verb in ACTION_VERBS
        if re.search(rf"\b{re.escape(verb)}\b", text, flags=re.I)
    ]

    has_exam = bool(re.search(r"\b(exam|examination|hall ticket)\b", text, re.I))
    has_assignment = bool(re.search(r"\b(assignment|coursework)\b", text, re.I))
    has_classroom_change = bool(old_location or new_location)

    entities = extract_entities(text)
    proposed_event = detect_timetable_proposal(
        text=text,
        category=category_name,
        dates=dates,
        times=times,
        old_location=old_location,
        new_location=new_location,
    )

    return {
        "category": category_name,
        "category_confidence": category_confidence,
        "importance": importance_name,
        "importance_confidence": importance_confidence,
        "uncertain": uncertain,
        "review_recommended": uncertain,
        "dates": dates,
        "normalized_dates": normalized_dates,
        "times": times,
        "has_deadline": deadline_date is not None,
        "deadline_date": deadline_date,
        "has_classroom_change": has_classroom_change,
        "old_location": old_location,
        "new_location": new_location,
        "has_exam": has_exam,
        "has_assignment": has_assignment,
        "action_items": action_items,
        "entities": entities,
        "proposed_event": proposed_event,
        "model_version": MODEL_VERSION,
    }


def main():
    parser = argparse.ArgumentParser(description="Campus AI NLP Inference CLI")
    parser.add_argument("--subject", default="Exam timetable published")
    parser.add_argument(
        "--body",
        default="The Computer Networks examination scheduled for 12 November has been moved to Room 204 on 14 November at 10 AM.",
    )
    parser.add_argument("--sender-role", default="ADMIN")
    args = parser.parse_args()

    result = process_email(
        subject=args.subject,
        body=args.body,
        sender_role=args.sender_role,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
