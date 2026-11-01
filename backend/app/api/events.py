"""Events and Timetable Proposal API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.event import Event
from ..models.user import User
from ..schemas.event import EventResponse, ProposalReviewRequest
from ..security.auth import get_current_user
from ..services.event_service import event_service

router = APIRouter(prefix="/events", tags=["Timetable & Events"])


@router.get("", response_model=list[EventResponse])
def list_events_endpoint(
    status: str | None = Query(None, description="Filter by status (CONFIRMED, PROPOSED, REJECTED)"),
    date: str | None = Query(None, description="Optional target date filter YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve personal timetable events and confirmed schedule items."""
    return event_service.list_events(db=db, user_id=current_user.id, status=status, date_str=date)


@router.get("/proposals", response_model=list[EventResponse])
def get_pending_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve NLP-detected timetable and classroom change proposals awaiting confirmation."""
    return event_service.get_proposals(db=db, user_id=current_user.id)


@router.post("/{id}/confirm", response_model=EventResponse)
def confirm_proposal(
    id: int,
    payload: ProposalReviewRequest = ProposalReviewRequest(action="confirm"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm a proposed timetable change and schedule update."""
    payload.action = "confirm"
    event = event_service.review_proposal(
        db=db,
        user_id=current_user.id,
        event_id=id,
        review=payload,
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposed event not found.",
        )
    return event


@router.post("/{id}/reject", response_model=EventResponse)
def reject_proposal(
    id: int,
    payload: ProposalReviewRequest = ProposalReviewRequest(action="reject"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a proposed timetable change."""
    payload.action = "reject"
    event = event_service.review_proposal(
        db=db,
        user_id=current_user.id,
        event_id=id,
        review=payload,
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposed event not found.",
        )
    return event
