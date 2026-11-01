"""Event service managing timetable events, proposed changes, and confirmation."""

import re
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.event import Event
from ..models.note import Subject
from ..schemas.event import ProposalReviewRequest


class EventService:
    # Explicit regex patterns for student's enrolled courses and acronyms
    STUDENT_COURSE_PATTERNS = [
        re.compile(r"\bcomputer\s+networks?\b", re.IGNORECASE),
        re.compile(r"\bcn\b", re.IGNORECASE),
        re.compile(r"\bnatural\s+language\s+processing\b", re.IGNORECASE),
        re.compile(r"\bnlp\b", re.IGNORECASE),
        re.compile(r"\bdatabase\s+management\b", re.IGNORECASE),
        re.compile(r"\bdbms\b", re.IGNORECASE),
        re.compile(r"\bdeep\s+learning\b", re.IGNORECASE),
        re.compile(r"\bdl\b", re.IGNORECASE),
        re.compile(r"\bmobile\s+app(?:lication)?(?:\s+dev)?\b", re.IGNORECASE),
        re.compile(r"\bmad\b", re.IGNORECASE),
        re.compile(r"\bintelligence\s+systems?\s*2\b", re.IGNORECASE),
        re.compile(r"\bis\s*2\b", re.IGNORECASE),
        re.compile(r"\bintelligence\s+systems?\s*1\b", re.IGNORECASE),
        re.compile(r"\bis\s*1\b", re.IGNORECASE),
        re.compile(r"\bdrone\b", re.IGNORECASE),
        re.compile(r"\bforensic(?:\s+science)?\b", re.IGNORECASE),
        re.compile(r"\bintro\s+(?:to|for)\s+fc\b", re.IGNORECASE),
        re.compile(r"\bdata\s+structures?\b", re.IGNORECASE),
        re.compile(r"\bdaa\b", re.IGNORECASE),
        re.compile(r"\bdsa\b", re.IGNORECASE),
        re.compile(r"\bmachine\s+learning\b", re.IGNORECASE),
        re.compile(r"\bml\b", re.IGNORECASE),
        re.compile(r"\bcomputer\s+architecture\b", re.IGNORECASE),
        re.compile(r"\bcoa\b", re.IGNORECASE),
        re.compile(r"\boperating\s+systems?\b", re.IGNORECASE),
        re.compile(r"\bos\b", re.IGNORECASE),
        re.compile(r"\bsignal\s+(?:and|&)\s+image\s+processing\b", re.IGNORECASE),
        re.compile(r"\bsip\b", re.IGNORECASE),
        re.compile(r"\bartificial\s+intelligence\b", re.IGNORECASE),
    ]

    @classmethod
    def is_event_relevant_to_student(cls, event: Event) -> bool:
        """Check if a timetable event or change proposal strictly pertains to subjects in student's Google Calendar."""
        if not event:
            return False

        text_to_check = f"{event.title or ''} {event.subject or ''} {event.summary or ''}".lower()

        for pattern in cls.STUDENT_COURSE_PATTERNS:
            if pattern.search(text_to_check):
                return True

        return False

    @classmethod
    def list_events(
        cls,
        db: Session,
        user_id: int,
        status: str | None = None,
        date_str: str | None = None,
        limit: int = 2500,
    ) -> list[Event]:
        query = db.query(Event).filter(Event.user_id == user_id)
        if status:
            query = query.filter(Event.status == status)

        if date_str:
            # Format: YYYY-MM-DD
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                day_start = datetime.combine(target_date, datetime.min.time())
                day_end = datetime.combine(target_date, datetime.max.time())
                query = query.filter(Event.start_at >= day_start, Event.start_at <= day_end)
            except ValueError:
                pass

        all_events = query.order_by(Event.start_at.asc()).limit(limit).all()

        # Filter strictly to the student's enrolled courses:
        # Both Google Calendar confirmed classes and faculty email proposals must match calendar subjects
        filtered = [e for e in all_events if cls.is_event_relevant_to_student(e)]
        return filtered

    @classmethod
    def get_proposals(cls, db: Session, user_id: int) -> list[Event]:
        """Return pending timetable change proposals filtered strictly to student's calendar subjects."""
        all_proposals = (
            db.query(Event)
            .filter(Event.user_id == user_id, Event.status == "PROPOSED")
            .order_by(Event.created_at.desc())
            .all()
        )
        return [p for p in all_proposals if cls.is_event_relevant_to_student(p)]

    @classmethod
    def review_proposal(
        cls,
        db: Session,
        user_id: int,
        event_id: int,
        review: ProposalReviewRequest,
    ) -> Event | None:
        event = (
            db.query(Event)
            .filter(Event.id == event_id, Event.user_id == user_id)
            .first()
        )
        if not event:
            return None

        if review.action.lower() == "confirm":
            event.status = "CONFIRMED"
            if review.updated_title:
                event.title = review.updated_title
            if review.updated_location:
                event.location = review.updated_location
            if review.updated_start_at:
                event.start_at = review.updated_start_at
        else:
            event.status = "REJECTED"

        db.commit()
        db.refresh(event)
        return event


event_service = EventService()
