"""Google Calendar OAuth & Synchronization API Endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.calendar import GoogleCalendarToken
from ..models.user import User
from ..schemas.calendar import (
    GoogleCalendarAuthUrlResponse,
    GoogleCalendarEventItem,
    GoogleCalendarEventsResponse,
    GoogleCalendarStatusResponse,
)
from ..security.auth import get_current_user
from ..services.calendar_service import calendar_service

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])


@router.get("/auth-url", response_model=GoogleCalendarAuthUrlResponse)
def get_calendar_auth_url(current_user: User = Depends(get_current_user)):
    """Generate the Google OAuth 2.0 authorization URL with state validation for calendar.readonly scope."""
    auth_url, state = calendar_service.get_authorization_url(current_user.id)
    return GoogleCalendarAuthUrlResponse(
        auth_url=auth_url,
        state=state,
        redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI,
    )


@router.get("/callback")
def google_calendar_oauth_callback(
    request: Request,
    code: str | None = Query(None, description="Authorization code from Google"),
    state: str | None = Query(None, description="OAuth state parameter"),
    error: str | None = Query(None, description="OAuth error if authorization was denied"),
    db: Session = Depends(get_db),
):
    """Matching FastAPI OAuth callback for Google Calendar OAuth 2.0.

    Validates state parameter, exchanges code for access & refresh tokens,
    and stores them securely in the SQLite database associated with the user.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth authorization denied: {error}",
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OAuth query parameters: 'code' and 'state' are required.",
        )

    # 1. Cryptographically validate state to prevent CSRF attacks and extract user_id
    user_id = calendar_service.validate_oauth_state(state)

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with OAuth session not found.",
        )

    # 2. Exchange authorization code for tokens
    token_data = calendar_service.exchange_code_for_tokens(
        code=code,
        redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI,
    )

    # 3. Securely persist user tokens in SQLite
    calendar_service.save_user_tokens(
        db=db,
        user_id=user_id,
        token_data=token_data,
    )

    # If request accepts HTML (e.g. from browser or webview popup), return friendly landing page
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Campus AI — Calendar Connected</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background: #f8fafc;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }}
                .card {{
                    background: white;
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                    text-align: center;
                    max-width: 420px;
                }}
                .badge {{
                    background: #10b981;
                    color: white;
                    width: 60px;
                    height: 60px;
                    line-height: 60px;
                    border-radius: 50%;
                    font-size: 28px;
                    margin: 0 auto 20px;
                }}
                h1 {{ font-size: 22px; color: #1e293b; margin: 0 0 10px; }}
                p {{ font-size: 14px; color: #64748b; line-height: 1.5; margin: 0 0 24px; }}
                .btn {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    padding: 10px 24px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">&#10003;</div>
                <h1>Google Calendar Connected!</h1>
                <p>Campus AI has successfully connected to your Google Calendar with read-only access. You can now close this tab and return to the application.</p>
                <a class="btn" href="javascript:window.close();">Close Window</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)

    return {
        "status": "CONNECTED",
        "message": "Google Calendar OAuth authorization successful. Tokens securely stored.",
        "user_email": user.email,
        "scope": settings.GOOGLE_CALENDAR_SCOPE,
    }


@router.get("/status", response_model=GoogleCalendarStatusResponse)
def get_calendar_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check whether the student has connected their Google Calendar account."""
    token_record = (
        db.query(GoogleCalendarToken)
        .filter(GoogleCalendarToken.user_id == current_user.id, GoogleCalendarToken.is_active.is_(True))
        .first()
    )
    if not token_record:
        return GoogleCalendarStatusResponse(is_connected=False)

    return GoogleCalendarStatusResponse(
        is_connected=True,
        scope=token_record.scope,
        expires_at=token_record.expires_at,
        created_at=token_record.created_at,
        updated_at=token_record.updated_at,
    )


@router.get("/events", response_model=GoogleCalendarEventsResponse)
def list_calendar_events(
    max_results: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve upcoming events from connected Google Calendar account."""
    events = calendar_service.fetch_calendar_events(db, current_user.id, max_results=max_results)
    return GoogleCalendarEventsResponse(
        events=[GoogleCalendarEventItem(**item) for item in events],
        total_count=len(events),
        message=f"Fetched {len(events)} upcoming events from Google Calendar.",
    )


@router.post("/sync", response_model=GoogleCalendarEventsResponse)
def sync_calendar_events_to_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Synchronize Google Calendar events into Campus AI personal timetable."""
    events, synced_count = calendar_service.sync_to_campus_events(db, current_user.id)
    return GoogleCalendarEventsResponse(
        events=[GoogleCalendarEventItem(**item) for item in events],
        total_count=len(events),
        synced_to_events_count=synced_count,
        message=f"Synchronized {synced_count} Google Calendar entries to student timetable.",
    )


@router.delete("/disconnect")
def disconnect_calendar_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Disconnect Google Calendar account and securely delete stored OAuth tokens."""
    removed = calendar_service.disconnect_calendar(db, current_user.id)
    return {
        "status": "DISCONNECTED",
        "message": "Google Calendar disconnected and stored tokens deleted." if removed else "No active connection found.",
    }
