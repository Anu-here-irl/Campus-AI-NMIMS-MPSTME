"""NLP Service wrapping Campus AI NLP pipeline for the FastAPI backend."""

import sys
from pathlib import Path
from typing import Any

# Add CAMPUS AI and nlp package to sys.path
CAMPUS_AI_ROOT = Path(__file__).resolve().parents[3]
NLP_DIR = CAMPUS_AI_ROOT / "nlp"

for path_entry in [str(CAMPUS_AI_ROOT), str(NLP_DIR)]:
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

try:
    from nlp.inference import process_email, MODEL_VERSION
except ImportError:
    from inference import process_email, MODEL_VERSION


class NLPService:
    @staticmethod
    def analyze_email(
        subject: str | None,
        body: str | None,
        sender_role: str | None = "ADMIN",
    ) -> dict[str, Any]:
        """Analyze email text and return structured predictions, entities, and proposals."""
        return process_email(
            subject=subject,
            body=body,
            sender_role=sender_role,
        )


nlp_service = NLPService()
