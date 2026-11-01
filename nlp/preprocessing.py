"""Campus AI NLP Preprocessing Module.

Preserves Person 1's exact cleaning and text normalization pipelines
to guarantee zero feature drift from trained models.
"""

from __future__ import annotations

import html
import re
import string
import unicodedata

HTML_TAG_RE = re.compile(r"<[^>]+>")
EMAIL_ADDR_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
TRACKING_QS_RE = re.compile(r"(\?|&)(utm_[^=&]+|ref|src)=[^&\s]*")
SPACE_RE = re.compile(r"[ \t]+")
REPEAT_PUNCT_RE = re.compile(r"([!?.,])\1{1,}")


def build_email_text(subject: str | None, body: str | None) -> str:
    """Concatenate subject and body into a unified text string."""
    subject_text = "" if subject is None or subject.strip() == "-" else subject.strip()
    body_text = "" if body is None or body.strip() == "-" else body.strip()
    if subject_text and body_text:
        return f"{subject_text}. {body_text}"
    return subject_text or body_text


def clean_email(text: str) -> str:
    """Clean raw email text removing HTML, headers, signatures, emojis, and tracking params."""
    text = unicodedata.normalize("NFKC", html.unescape(text))
    text = HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"(?m)^>.*$", " ", text)
    text = re.sub(
        r"(?m)^-{2,}\s*(?:forwarded message|original message)\s*-{2,}.*$",
        " ",
        text,
        flags=re.I,
    )
    text = re.sub(r"(?m)^(?:from|sent|to|subject):.*$", " ", text, flags=re.I)
    text = re.sub(r"\n--\s*\n.*$", "", text, flags=re.S)
    text = re.sub(
        r"(?im)^(?:regards|thanks|thank you|best regards|sincerely|warm regards)[,.]?\s*\n[\s\S]{0,150}$",
        "",
        text,
    )
    text = URL_RE.sub(lambda match: TRACKING_QS_RE.sub("", match.group(0)), text)
    text = EMAIL_ADDR_RE.sub("[EMAIL]", text)
    text = re.sub(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+", "", text)
    text = REPEAT_PUNCT_RE.sub(r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return SPACE_RE.sub(" ", text).strip()


def classification_text(text: str) -> str:
    """Normalize cleaned text for TF-IDF classification (lowercase, allowed punctuation)."""
    allowed = string.ascii_lowercase + string.digits + " %-."
    return SPACE_RE.sub(
        " ",
        "".join(char if char in allowed else " " for char in text.lower()),
    ).strip()
