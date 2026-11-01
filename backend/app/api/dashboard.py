"""Student Dashboard Summary API endpoint."""

from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.email import Email, EmailPrediction
from ..models.event import Event
from ..models.user import User
from ..security.auth import get_current_user
from ..services.event_service import event_service
from .emails import _build_email_response

router = APIRouter(prefix="/dashboard", tags=["Student Dashboard"])


@router.get("")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_time: str | None = None,
) -> dict[str, Any]:
    """Retrieve full dashboard summary for Android home screen."""
    # Determine reference current time (supports client device time or server local time)
    now = datetime.now()
    if client_time:
        try:
            cleaned_time = client_time.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(cleaned_time)
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone().replace(tzinfo=None)
            now = parsed
        except Exception:
            pass

    # 1. Total & unread emails
    total_emails = db.query(Email).filter(Email.user_id == current_user.id).count()
    unread_emails = (
        db.query(Email)
        .filter(Email.user_id == current_user.id, Email.is_read.is_(False))
        .count()
    )

    # 2. High priority emails
    high_priority_emails = (
        db.query(Email)
        .join(EmailPrediction)
        .filter(Email.user_id == current_user.id, EmailPrediction.importance == "HIGH")
        .order_by(Email.received_at.desc())
        .limit(5)
        .all()
    )

    # 3. Pending timetable proposals awaiting student action (filtered to student's calendar subjects)
    pending_proposals = event_service.get_proposals(db=db, user_id=current_user.id)[:5]

    # 4. Confirmed events & Real-time "Next Class" detection
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Today's entire schedule
    raw_today = (
        db.query(Event)
        .filter(
            Event.user_id == current_user.id,
            Event.status == "CONFIRMED",
            Event.start_at >= today_start,
            Event.start_at < today_end,
        )
        .order_by(Event.start_at.asc())
        .all()
    )
    today_events = [ev for ev in raw_today if event_service.is_event_relevant_to_student(ev)]

    # Confirmed classes from today onwards to determine the active/next class in real time
    raw_future = (
        db.query(Event)
        .filter(
            Event.user_id == current_user.id,
            Event.status == "CONFIRMED",
            Event.start_at >= today_start,
        )
        .order_by(Event.start_at.asc())
        .all()
    )
    relevant_future = [ev for ev in raw_future if event_service.is_event_relevant_to_student(ev)]

    # Filter to events that have not yet ended (end_at >= now)
    active_and_future = []
    for ev in relevant_future:
        effective_end = ev.end_at if ev.end_at else (ev.start_at + timedelta(hours=1))
        if effective_end >= now:
            active_and_future.append(ev)

    next_class = active_and_future[0] if active_and_future else None
    is_ongoing = False
    if next_class:
        effective_end = next_class.end_at if next_class.end_at else (next_class.start_at + timedelta(hours=1))
        is_ongoing = next_class.start_at <= now < effective_end

    return {
        "student_name": current_user.full_name or "Student",
        "student_email": current_user.email,
        "unread_email_count": unread_emails,
        "total_email_count": total_emails,
        "pending_proposals_count": len(pending_proposals),
        "high_priority_emails": [_build_email_response(e) for e in high_priority_emails],
        "pending_proposals": [
            {
                "id": p.id,
                "title": p.title,
                "subject": p.subject,
                "event_type": p.event_type,
                "location": p.location,
                "summary": p.summary,
                "start_at": p.start_at.isoformat() if p.start_at else None,
                "end_at": p.end_at.isoformat() if p.end_at else None,
            }
            for p in pending_proposals
        ],
        "next_class": (
            {
                "id": next_class.id,
                "title": next_class.title,
                "subject": next_class.subject,
                "event_type": next_class.event_type,
                "location": next_class.location,
                "start_at": next_class.start_at.isoformat() if next_class.start_at else None,
                "end_at": next_class.end_at.isoformat() if next_class.end_at else None,
                "is_ongoing": is_ongoing,
            }
            if next_class
            else None
        ),
        "upcoming_schedule": [
            {
                "id": ev.id,
                "title": ev.title,
                "subject": ev.subject,
                "event_type": ev.event_type,
                "location": ev.location,
                "start_at": ev.start_at.isoformat() if ev.start_at else None,
                "end_at": ev.end_at.isoformat() if ev.end_at else None,
            }
            for ev in active_and_future[:5]
        ],
        "today_schedule": [
            {
                "id": ev.id,
                "title": ev.title,
                "subject": ev.subject,
                "event_type": ev.event_type,
                "location": ev.location,
                "start_at": ev.start_at.isoformat() if ev.start_at else None,
                "end_at": ev.end_at.isoformat() if ev.end_at else None,
            }
            for ev in today_events
        ],
    }
