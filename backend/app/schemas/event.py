"""Event and Timetable Proposal Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel


class EventResponse(BaseModel):
    id: int
    user_id: int
    source_email_id: int | None = None
    title: str
    subject: str | None = None
    event_type: str
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    status: str
    summary: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProposalReviewRequest(BaseModel):
    action: str  # "confirm" or "reject"
    updated_title: str | None = None
    updated_location: str | None = None
    updated_start_at: datetime | None = None
