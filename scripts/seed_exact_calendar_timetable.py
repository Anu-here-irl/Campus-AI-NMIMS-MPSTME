"""
Seed and verify the exact repeating timetable from Google Calendar
Date Range: July 13th, 2026 to November 13th, 2026.
Matches user-provided timetable screenshot exactly.
"""

import os
import sys
from datetime import datetime, date, time, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.event import Event

# Weekly template: weekday -> list of slots
# weekday: 0 = Mon, 1 = Tue, 2 = Wed, 3 = Thu, 4 = Fri, 5 = Sat, 6 = Sun
WEEKLY_SCHEDULE = {
    0: [  # Monday
        {
            "title": "MAD CR 602",
            "subject": "Mobile Application Development",
            "start": (12, 0),
            "end": (13, 0),
            "location": "Classroom 602 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "IS 2 AI Lab",
            "subject": "Intelligence Systems 2",
            "start": (14, 0),
            "end": (16, 0),
            "location": "AI / NLP Lab (Room 205)",
            "event_type": "LAB",
        },
        {
            "title": "Drone Theory CR: 504",
            "subject": "Drone Technology",
            "start": (16, 0),
            "end": (18, 0),
            "location": "Classroom 504 (Floor 5)",
            "event_type": "LECTURE",
        },
    ],
    1: [  # Tuesday
        {
            "title": "DL CR: 101",
            "subject": "Deep Learning",
            "start": (10, 0),
            "end": (11, 0),
            "location": "Classroom 101 (Floor 1)",
            "event_type": "LECTURE",
        },
        {
            "title": "IS 2 CR: 602",
            "subject": "Intelligence Systems 2",
            "start": (11, 0),
            "end": (12, 0),
            "location": "Classroom 602 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "NLP CL: 602",
            "subject": "Natural Language Processing",
            "start": (12, 0),
            "end": (14, 0),
            "location": "Computer Lab 602 (Floor 6)",
            "event_type": "LAB",
        },
        {
            "title": "NLP CR:603",
            "subject": "Natural Language Processing",
            "start": (15, 0),
            "end": (16, 0),
            "location": "Classroom 603 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "Drone Lab TR: 501",
            "subject": "Drone Technology",
            "start": (16, 0),
            "end": (18, 0),
            "location": "Tutorial Room 501 (Floor 5)",
            "event_type": "LAB",
        },
    ],
    2: [  # Wednesday
        {
            "title": "DL CR: 603",
            "subject": "Deep Learning",
            "start": (10, 0),
            "end": (11, 0),
            "location": "Classroom 603 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "CN CL: 602",
            "subject": "Computer Networks",
            "start": (12, 0),
            "end": (14, 0),
            "location": "Computer Lab 602 (Floor 6)",
            "event_type": "LAB",
        },
        {
            "title": "NLP TR: 401",
            "subject": "Natural Language Processing",
            "start": (15, 0),
            "end": (16, 0),
            "location": "Tutorial Room 401 (Floor 4)",
            "event_type": "LECTURE",
        },
        {
            "title": "Drone Theory Advance Comm",
            "subject": "Drone Technology",
            "start": (16, 0),
            "end": (18, 0),
            "location": "Advance Comm Lab (Floor 5)",
            "event_type": "LECTURE",
        },
    ],
    3: [  # Thursday
        {
            "title": "DL CL: 601",
            "subject": "Deep Learning",
            "start": (12, 0),
            "end": (14, 0),
            "location": "Computer Lab 601 (Floor 6)",
            "event_type": "LAB",
        },
        {
            "title": "CN CR: 602",
            "subject": "Computer Networks",
            "start": (15, 0),
            "end": (16, 0),
            "location": "Classroom 602 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "Intro to FC CR: 605",
            "subject": "Intro to Forensic Science",
            "start": (16, 0),
            "end": (18, 0),
            "location": "Classroom 605 (Floor 6)",
            "event_type": "LECTURE",
        },
    ],
    4: [  # Friday
        {
            "title": "IS 2 CR: 603",
            "subject": "Intelligence Systems 2",
            "start": (10, 0),
            "end": (11, 0),
            "location": "Classroom 603 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "CN CR: 603",
            "subject": "Computer Networks",
            "start": (11, 0),
            "end": (12, 0),
            "location": "Classroom 603 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "MAD CR:602",
            "subject": "Mobile Application Development",
            "start": (13, 0),
            "end": (14, 0),
            "location": "Classroom 602 (Floor 6)",
            "event_type": "LECTURE",
        },
        {
            "title": "MAD CL: 601",
            "subject": "Mobile Application Development",
            "start": (14, 0),
            "end": (16, 0),
            "location": "Computer Lab 601 (Floor 6)",
            "event_type": "LAB",
        },
        {
            "title": "Intro to FC CR: 606",
            "subject": "Intro to Forensic Science",
            "start": (16, 0),
            "end": (18, 0),
            "location": "Classroom 606 (Floor 6)",
            "event_type": "LECTURE",
        },
    ],
}

def sync_repeating_timetable():
    print("=" * 65)
    print("  Syncing Exact Timetable from July 13th to November 13th, 2026")
    print("=" * 65)

    db = SessionLocal()

    # Clear existing confirmed calendar events to avoid any mismatches
    del_count = db.query(Event).filter(Event.status == "CONFIRMED", Event.source_email_id.is_(None)).delete()
    db.commit()
    print(f"Cleared {del_count} existing confirmed timetable entries.")

    start_date = date(2026, 7, 13)
    end_date = date(2026, 11, 13)

    cur = start_date
    added_count = 0

    while cur <= end_date:
        weekday = cur.weekday()
        slots = WEEKLY_SCHEDULE.get(weekday, [])

        for slot in slots:
            start_dt = datetime.combine(cur, time(slot["start"][0], slot["start"][1]))
            end_dt = datetime.combine(cur, time(slot["end"][0], slot["end"][1]))

            ev = Event(
                user_id=1,
                source_email_id=None,
                title=slot["title"],
                subject=slot["subject"],
                event_type=slot["event_type"],
                start_at=start_dt,
                end_at=end_dt,
                location=slot["location"],
                status="CONFIRMED",
                summary=f"Google Calendar ({slot['title']})",
            )
            db.add(ev)
            added_count += 1

        cur += timedelta(days=1)

    db.commit()
    print(f"Successfully generated {added_count} confirmed classes matching Google Calendar across {18} weeks!")

    # Verify breakdown
    print("\n--- Daily counts sample ---")
    for d in [date(2026, 7, 13), date(2026, 7, 14), date(2026, 7, 15), date(2026, 7, 16), date(2026, 7, 17), date(2026, 10, 27), date(2026, 11, 13)]:
        cnt = db.query(Event).filter(Event.status == "CONFIRMED", Event.start_at >= datetime.combine(d, time.min), Event.start_at <= datetime.combine(d, time.max)).count()
        print(f"  {d.strftime('%a, %d %b %Y')}: {cnt} classes")

    total_confirmed = db.query(Event).filter(Event.status == "CONFIRMED").count()
    total_proposed = db.query(Event).filter(Event.status == "PROPOSED").count()
    print(f"\nFinal State -> Total Confirmed: {total_confirmed} | Total Proposed Notices: {total_proposed}")

    db.close()

if __name__ == "__main__":
    sync_repeating_timetable()
