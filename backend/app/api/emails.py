"""Email and NLP Classification API endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.email import Email, EmailPrediction, ExtractedEntity
from ..models.user import User
from ..schemas.email import (
    EmailIngestRequest,
    EmailListResponse,
    EmailResponse,
    EntityItem,
    NLPPredictionResponse,
    ProposedEventItem,
)
from ..security.auth import get_current_user
from ..services.email_service import email_service
from ..services.email_ingest_service import email_ingest_service
from ..services.nlp_service import nlp_service

router = APIRouter(prefix="", tags=["Emails & NLP"])


@router.post("/nlp/predict", response_model=NLPPredictionResponse)
def predict_nlp(
    payload: EmailIngestRequest,
    current_user: User = Depends(get_current_user),
):
    """Run NLP classification, importance rating, and entity extraction directly on email text."""
    res = nlp_service.analyze_email(
        subject=payload.subject,
        body=payload.body,
        sender_role=payload.sender_role,
    )
    return res


@router.post("/emails/sync", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
def ingest_email_endpoint(
    payload: EmailIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest a new college email (synthetic or forwarded), classify via NLP, and store."""
    email, is_dup = email_service.ingest_email(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )
    return _build_email_response(email)


@router.post("/emails/ingest-batch")
def ingest_batch_endpoint(
    items: list[dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest a batch of academic emails into the database and run NLP analysis."""
    return email_ingest_service.ingest_batch_items(
        db=db,
        user_id=current_user.id,
        items=items,
    )


@router.post("/emails/sync-gmail")
def sync_gmail_endpoint(
    access_token: str | None = None,
    max_results: int = 25,
    query: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync real emails from user's connected Gmail inbox."""
    if not access_token:
        # Retrieve valid (auto-refreshed) access token from stored Google Calendar & Gmail credentials
        from ..services.calendar_service import calendar_service
        try:
            access_token = calendar_service.get_valid_access_token(db, current_user.id)
        except HTTPException:
            access_token = None

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active Google access token available. Please provide access_token parameter or connect your Google account.",
        )

    return email_ingest_service.ingest_from_gmail(
        db=db,
        user_id=current_user.id,
        access_token=access_token,
        max_results=max_results,
        query=query,
    )



@router.get("/emails", response_model=EmailListResponse)
def list_emails_endpoint(
    category: str | None = Query(None, description="Filter by category (e.g. EXAM, ASSIGNMENT, CLASSROOM / TIMETABLE)"),
    importance: str | None = Query(None, description="Filter by importance (HIGH, MEDIUM, LOW)"),
    unread_only: bool = Query(False, description="Filter unread emails only"),
    search: str | None = Query(None, description="Search term in subject or body"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve categorized emails with search, filtering, and importance indicators."""
    items = email_service.list_emails(
        db=db,
        user_id=current_user.id,
        category=category,
        importance=importance,
        unread_only=unread_only,
        search=search,
        limit=limit,
        offset=offset,
    )
    total = db.query(Email).filter(Email.user_id == current_user.id).count()
    unread_count = (
        db.query(Email)
        .filter(Email.user_id == current_user.id, Email.is_read.is_(False))
        .count()
    )
    return EmailListResponse(
        total=total,
        unread_count=unread_count,
        items=[_build_email_response(e) for e in items],
    )


@router.get("/emails/{id}", response_model=EmailResponse)
def get_email_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single email with full predictions and extracted entities."""
    email = (
        db.query(Email)
        .filter(Email.id == id, Email.user_id == current_user.id)
        .first()
    )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found.",
        )
    # Mark as read
    if not email.is_read:
        email.is_read = True
        db.commit()

    return _build_email_response(email)


def _build_email_response(email: Email) -> EmailResponse:
    pred = email.prediction
    entities = [
        EntityItem(
            entity_type=e.entity_type,
            value=e.value,
            normalized_value=e.normalized_value,
            confidence=e.confidence,
        )
        for e in email.entities
    ]

    proposed = None
    if email.events:
        ev = email.events[0]
        proposed = ProposedEventItem(
            title=ev.title,
            subject=ev.subject,
            event_type=ev.event_type,
            new_date=ev.start_at.strftime("%Y-%m-%d") if ev.start_at else None,
            new_location=ev.location,
            summary=ev.summary,
        )

    return EmailResponse(
        id=email.id,
        user_id=email.user_id,
        provider_message_id=email.provider_message_id,
        subject=email.subject,
        sender=email.sender,
        sender_role=email.sender_role,
        received_at=email.received_at,
        body_text=email.body_text,
        is_read=email.is_read,
        category=pred.category if pred else None,
        category_confidence=pred.category_confidence if pred else None,
        importance=pred.importance if pred else None,
        importance_confidence=pred.importance_confidence if pred else None,
        uncertain=pred.uncertain if pred else False,
        review_recommended=pred.uncertain if pred else False,
        entities=entities,
        proposed_event=proposed,
    )
