"""Google Calendar API and OAuth Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel


class GoogleCalendarAuthUrlResponse(BaseModel):
    auth_url: str
    state: str
    redirect_uri: str


class GoogleCalendarStatusResponse(BaseModel):
    is_connected: bool
    scope: str | None = None
    expires_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GoogleCalendarEventItem(BaseModel):
    id: str
    summary: str
    description: str | None = None
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    html_link: str | None = None


class GoogleCalendarEventsResponse(BaseModel):
    events: list[GoogleCalendarEventItem] = []
    total_count: int
    synced_to_events_count: int = 0
    message: str
