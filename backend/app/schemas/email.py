"""Email and NLP Prediction Pydantic schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel


class EmailIngestRequest(BaseModel):
    subject: str | None = None
    body: str | None = None
    sender: str | None = None
    sender_role: str | None = "ADMIN"
    provider_message_id: str | None = None


class EntityItem(BaseModel):
    entity_type: str
    value: str
    normalized_value: str | None = None
    confidence: float = 1.0


class ProposedEventItem(BaseModel):
    title: str
    subject: str | None = None
    event_type: str = "LECTURE"
    old_date: str | None = None
    new_date: str | None = None
    time: str | None = None
    old_location: str | None = None
    new_location: str | None = None
    summary: str | None = None
    raw_evidence: str | None = None


class NLPPredictionResponse(BaseModel):
    category: str
    category_confidence: float
    importance: str
    importance_confidence: float
    uncertain: bool
    review_recommended: bool
    dates: list[str] = []
    normalized_dates: list[str] = []
    times: list[str] = []
    has_deadline: bool = False
    deadline_date: str | None = None
    has_classroom_change: bool = False
    old_location: str | None = None
    new_location: str | None = None
    has_exam: bool = False
    has_assignment: bool = False
    action_items: list[str] = []
    entities: list[EntityItem] = []
    proposed_event: ProposedEventItem | None = None
    model_version: str = "v1.0-tfidf-logreg"


class EmailResponse(BaseModel):
    id: int
    user_id: int
    provider_message_id: str | None = None
    subject: str | None = None
    sender: str | None = None
    sender_role: str | None = None
    received_at: datetime
    body_text: str | None = None
    is_read: bool = False
    category: str | None = None
    category_confidence: float | None = None
    importance: str | None = None
    importance_confidence: float | None = None
    uncertain: bool = False
    review_recommended: bool = False
    entities: list[EntityItem] = []
    proposed_event: ProposedEventItem | None = None

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    total: int
    unread_count: int
    items: list[EmailResponse]
