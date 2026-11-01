import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import httpx
from backend.app.database import SessionLocal
from backend.app.services.calendar_service import calendar_service

db = SessionLocal()
token = calendar_service.get_valid_access_token(db, 1)
headers = {'Authorization': f'Bearer {token}'}

with httpx.Client() as client:
    # Query from July 2026 onwards
    ev_res = client.get(
        "https://www.googleapis.com/calendar/v3/calendars/anjali.upadhyay2007@gmail.com/events",
        headers=headers,
        params={
            'maxResults': 2500,
            'singleEvents': 'true',
            'orderBy': 'startTime',
            'timeMin': '2026-06-01T00:00:00Z',
            'timeMax': '2026-12-31T23:59:59Z',
        }
    )
    items = ev_res.json().get('items', [])
    print(f"Total events between June 2026 and Dec 2026: {len(items)}")
    for it in items:
        summary = it.get('summary', '')
        start = it.get('start', {})
        st = start.get('dateTime') or start.get('date') or ''
        loc = it.get('location', '')
        print(f"[{st}] {summary} | Location: {loc}")

db.close()
