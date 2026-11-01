"""Google Calendar OAuth & Synchronization Service.

Handles OAuth 2.0 authorization URL generation, cryptographic state validation,
token exchange, secure token persistence in SQLite, automatic token refresh,
and Google Calendar API (read-only) integration.
"""

import base64
import hashlib
import hmac
import json
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import settings
from ..models.calendar import GoogleCalendarToken
from ..models.event import Event


class GoogleCalendarService:
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    CALENDAR_EVENTS_ENDPOINT = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    STATE_VALIDITY_SECONDS = 900  # 15 minutes

    @classmethod
    def generate_oauth_state(cls, user_id: int) -> str:
        """Generate a cryptographically signed, timestamped OAuth state string."""
        payload = {
            "sub": user_id,
            "ts": time.time(),
            "nonce": hashlib.sha256(f"{user_id}:{time.time()}:{settings.SECRET_KEY}".encode()).hexdigest()[:16],
        }
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")

        sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")

        return f"{payload_b64}.{sig_b64}"

    @classmethod
    def validate_oauth_state(cls, state: str) -> int:
        """Validate OAuth state signature and freshness, returning the authenticated user_id."""
        try:
            parts = state.split(".")
            if len(parts) != 2:
                raise ValueError("Malformed state")
            payload_b64, sig_b64 = parts

            expected_sig = hmac.new(
                settings.SECRET_KEY.encode("utf-8"),
                payload_b64.encode("utf-8"),
                hashlib.sha256,
            ).digest()
            expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

            if not hmac.compare_digest(sig_b64, expected_sig_b64):
                raise ValueError("State signature verification failed")

            # Pad base64
            rem = len(payload_b64) % 4
            if rem > 0:
                payload_b64 += "=" * (4 - rem)
            data = json.loads(base64.urlsafe_b64decode(payload_b64).decode())

            # Check expiration
            if time.time() - data.get("ts", 0) > cls.STATE_VALIDITY_SECONDS:
                raise ValueError("OAuth state expired (older than 15 minutes)")

            user_id = data.get("sub")
            if not user_id:
                raise ValueError("Missing user_id in state")

            return int(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or expired OAuth state parameter: {str(e)}",
            )

    @classmethod
    def get_authorization_url(cls, user_id: int, include_gmail: bool = True) -> tuple[str, str]:
        """Construct the Google OAuth authorization URL for calendar and gmail read scopes."""
        if not settings.GOOGLE_CALENDAR_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_CALENDAR_CLIENT_ID is not configured in backend environment.",
            )

        state = cls.generate_oauth_state(user_id)
        scope = settings.GOOGLE_COMBINED_SCOPE if include_gmail else settings.GOOGLE_CALENDAR_SCOPE
        params = {
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_CALENDAR_REDIRECT_URI,
            "response_type": "code",
            "scope": scope,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        auth_url = f"{cls.AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
        return auth_url, state

    @classmethod
    def exchange_code_for_tokens(cls, code: str, redirect_uri: str | None = None) -> dict[str, Any]:
        """Exchange authorization code for OAuth tokens with Google."""
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri or settings.GOOGLE_CALENDAR_REDIRECT_URI,
        }
        if settings.GOOGLE_CALENDAR_CLIENT_SECRET:
            payload["client_secret"] = settings.GOOGLE_CALENDAR_CLIENT_SECRET

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(cls.TOKEN_ENDPOINT, data=payload)
                if res.status_code != 200:
                    error_detail = res.text
                    try:
                        err_json = res.json()
                        error_detail = err_json.get("error_description") or err_json.get("error") or res.text
                    except Exception:
                        pass
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Google token exchange failed: {error_detail}",
                    )
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error communicating with Google OAuth endpoint: {str(e)}",
            )

    @classmethod
    def save_user_tokens(cls, db: Session, user_id: int, token_data: dict[str, Any]) -> GoogleCalendarToken:
        """Persist or update user OAuth tokens securely in SQLite."""
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        scope = token_data.get("scope", settings.GOOGLE_CALENDAR_SCOPE)

        token_record = (
            db.query(GoogleCalendarToken)
            .filter(GoogleCalendarToken.user_id == user_id)
            .first()
        )

        if not token_record:
            token_record = GoogleCalendarToken(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=expires_at,
                scope=scope,
                is_active=True,
            )
            db.add(token_record)
        else:
            token_record.access_token = access_token
            if refresh_token:
                token_record.refresh_token = refresh_token
            token_record.expires_at = expires_at
            token_record.scope = scope
            token_record.is_active = True
            token_record.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(token_record)
        return token_record

    @classmethod
    def get_valid_access_token(cls, db: Session, user_id: int) -> str:
        """Retrieve valid access token, automatically refreshing via refresh_token if needed."""
        token_record = (
            db.query(GoogleCalendarToken)
            .filter(GoogleCalendarToken.user_id == user_id, GoogleCalendarToken.is_active.is_(True))
            .first()
        )
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Google Calendar account connected for this user.",
            )

        # Check if expired or about to expire in next 2 minutes
        now = datetime.utcnow()
        if token_record.expires_at and token_record.expires_at <= now + timedelta(minutes=2):
            if not token_record.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Calendar access token expired and no refresh token is stored. Please reconnect.",
                )

            # Refresh token
            refresh_payload = {
                "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": token_record.refresh_token,
            }
            if settings.GOOGLE_CALENDAR_CLIENT_SECRET:
                refresh_payload["client_secret"] = settings.GOOGLE_CALENDAR_CLIENT_SECRET

            with httpx.Client(timeout=15.0) as client:
                res = client.post(cls.TOKEN_ENDPOINT, data=refresh_payload)
                if res.status_code != 200:
                    token_record.is_active = False
                    db.commit()
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to refresh Google Calendar token. Please reconnect.",
                    )
                new_data = res.json()
                token_record.access_token = new_data["access_token"]
                expires_in = new_data.get("expires_in", 3600)
                token_record.expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
                token_record.updated_at = datetime.utcnow()
                db.commit()

        return token_record.access_token

    @staticmethod
    def extract_location_from_title(title: str) -> str:
        """Extract and format readable room/lab from calendar title (e.g. 'NLP CL: 602' -> 'Computer Lab 602')."""
        t = (title or "").upper()
        if "CL:" in t or "CL " in t:
            m = re.search(r"CL:?\s*(\d+)", t)
            if m:
                return f"Computer Lab {m.group(1)} (Floor {m.group(1)[0]})"
        if "CR:" in t or "CR " in t:
            m = re.search(r"CR:?\s*(\d+)", t)
            if m:
                return f"Classroom {m.group(1)} (Floor {m.group(1)[0]})"
        if "TR:" in t or "TR " in t:
            m = re.search(r"TR:?\s*(\d+)", t)
            if m:
                return f"Tutorial Room {m.group(1)} (Floor {m.group(1)[0]})"
        if "AI LAB" in t:
            return "AI / NLP Lab (Room 205)"
        if "ADVANCE COMM" in t or "B.COMM" in t:
            return "Communication Lab (5th Floor)"
        return "Classroom 602"

    @staticmethod
    def extract_subject_from_title(title: str) -> str:
        """Map calendar event titles to student's enrolled courses."""
        t = (title or "").upper()
        if "NLP" in t:
            return "Natural Language Processing"
        if "CN" in t or "COMPUTER NETWORKS" in t:
            return "Computer Networks"
        if "DBMS" in t or "DATABASE" in t:
            return "Database Management Systems"
        if "DL" in t or "DEEP LEARNING" in t:
            return "Deep Learning"
        if "MAD" in t or "MOBILE APP" in t:
            return "Mobile Application Development"
        if "IS 2" in t or "IS-II" in t or "IS - II" in t or "IS -II" in t:
            return "Intelligence Systems 2"
        if "IS 1" in t or "IS-I" in t or "IS - I" in t or "IS -I" in t:
            return "Intelligence Systems 1"
        if "DRONE" in t:
            return "Drone Technology"
        if "FC" in t or "FORENSIC" in t or "IFS" in t:
            return "Intro to Forensic Science"
        if "DAA" in t or "DSA" in t or "DATA STRUCTURE" in t:
            return "Data Structures & Algorithms"
        if "ML" in t or "MACHINE LEARNING" in t:
            return "Machine Learning"
        if "COA" in t or "COMPUTER ARCHITECTURE" in t:
            return "Computer Architecture"
        if "OS" in t or "OPERATING SYSTEM" in t:
            return "Operating System"
        if "SIP" in t or "SIGNAL" in t:
            return "Signal and Image Processing"
        if "AI" in t or "ARTIFICIAL" in t:
            return "Artificial Intelligence"
        return title.split(":")[0].strip() if ":" in title else title.strip()

    @classmethod
    def fetch_calendar_events(cls, db: Session, user_id: int, max_results: int = 2500) -> list[dict[str, Any]]:
        """Fetch full semester academic timetable events from Google Calendar API (calendar.readonly scope)."""
        access_token = cls.get_valid_access_token(db, user_id)
        
        # Include current semester (June 2026 to January 2027)
        time_min = "2026-06-01T00:00:00Z"
        time_max = "2027-01-31T23:59:59Z"

        params = {
            "maxResults": max_results,
            "orderBy": "startTime",
            "singleEvents": "true",
            "timeMin": time_min,
            "timeMax": time_max,
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        with httpx.Client(timeout=30.0) as client:
            # 1. Discover all calendars accessible to the user
            cal_res = client.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)
            cal_ids = ["primary"]
            if cal_res.status_code == 200:
                cals = cal_res.json().get("items", [])
                for c in cals:
                    cid = c.get("id")
                    if cid and cid not in cal_ids:
                        cal_ids.append(cid)

            # 2. Gather events across user's calendars
            items = []
            seen_event_ids = set()
            for cid in cal_ids:
                try:
                    res = client.get(
                        f"https://www.googleapis.com/calendar/v3/calendars/{cid}/events",
                        params=params,
                        headers=headers,
                    )
                    if res.status_code == 200:
                        cal_items = res.json().get("items", [])
                        for item in cal_items:
                            iid = item.get("id")
                            if iid not in seen_event_ids:
                                seen_event_ids.add(iid)
                                items.append(item)
                except Exception:
                    pass

        events = []
        for item in items:
            start = item.get("start", {})
            end = item.get("end", {})
            start_str = start.get("dateTime") or start.get("date")
            end_str = end.get("dateTime") or end.get("date")

            events.append({
                "id": item.get("id", ""),
                "summary": item.get("summary", "Untitled College Event"),
                "description": item.get("description"),
                "location": item.get("location"),
                "start_time": start_str,
                "end_time": end_str,
                "html_link": item.get("htmlLink"),
            })
        return events

    @classmethod
    def sync_to_campus_events(cls, db: Session, user_id: int) -> tuple[list[dict[str, Any]], int]:
        """Fetch Google Calendar events and synchronize them into student's Campus AI Event records."""
        events_list = cls.fetch_calendar_events(db, user_id)
        synced_count = 0

        for item in events_list:
            summary = item.get("summary") or "College Event"
            start_time_str = item.get("start_time")
            parsed_date = None
            if start_time_str:
                try:
                    # ISO string parse (e.g. 2026-11-15T10:00:00+05:30 or 2026-11-15)
                    clean_iso = start_time_str.replace("Z", "+00:00")
                    parsed_date = datetime.fromisoformat(clean_iso).replace(tzinfo=None)
                except Exception:
                    pass

            if not parsed_date:
                continue

            # Detect event type
            event_type = "EXAM" if "exam" in summary.lower() else ("LAB" if "lab" in summary.lower() or "cl" in summary.lower() else "LECTURE")
            
            # Format room
            loc = item.get("location")
            if not loc:
                loc = cls.extract_location_from_title(summary)
            subj = cls.extract_subject_from_title(summary)

            # Check if event with title, user and start_at already exists
            existing = (
                db.query(Event)
                .filter(
                    Event.user_id == user_id,
                    Event.title == summary,
                    Event.start_at == parsed_date,
                )
                .first()
            )
            if not existing:
                new_event = Event(
                    user_id=user_id,
                    title=summary,
                    subject=subj,
                    event_type=event_type,
                    start_at=parsed_date,
                    location=loc,
                    status="CONFIRMED",
                    summary=item.get("description") or f"Imported from Google Calendar ({summary})",
                )
                db.add(new_event)
                synced_count += 1
            else:
                if loc and not existing.location:
                    existing.location = loc
                if subj and not existing.subject:
                    existing.subject = subj
                synced_count += 1

        db.commit()
        return events_list, synced_count

    @classmethod
    def disconnect_calendar(cls, db: Session, user_id: int) -> bool:
        """Remove stored OAuth tokens for the student."""
        token_record = (
            db.query(GoogleCalendarToken)
            .filter(GoogleCalendarToken.user_id == user_id)
            .first()
        )
        if token_record:
            db.delete(token_record)
            db.commit()
            return True
        return False


calendar_service = GoogleCalendarService()
