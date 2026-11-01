"""
Database Cleaning and Full Google Calendar Synchronization Script.

1. Removes all synthetic test emails (exam-cell@campus.edu, msg-test-*, msg_e2e_*).
2. Removes all synthetic filler timetable events (DSA, CN Lab, DBMS, NLP exam seeds).
3. Connects to Google Calendar and synchronizes the entire semester timetable (all 400+ classes).
4. Re-evaluates proposals from real NMIMS emails so venue changes and cancellations map to their target dates.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Prevent Windows console encoding issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.email import Email, EmailPrediction, ExtractedEntity
from backend.app.models.event import Event
from backend.app.services.calendar_service import calendar_service
from backend.app.services.event_service import event_service
from backend.app.services.nlp_service import nlp_service

def clean_and_sync():
    print("=" * 70)
    print("  CAMPUS AI - CLEANING SYNTHETIC DATA & SYNCING GOOGLE CALENDAR")
    print("=" * 70)

    db = SessionLocal()

    # ---------------------------------------------------------
    # STEP 1: Purge synthetic emails & their associated records
    # ---------------------------------------------------------
    print("\n[1] Purging synthetic filler emails...")
    synthetic_emails = (
        db.query(Email)
        .filter(
            (Email.sender.ilike("%campus.edu%"))
            | (Email.provider_message_id.ilike("msg-test-%"))
            | (Email.provider_message_id.ilike("msg_e2e_%"))
            | (Email.sender == "Academic Department")
        )
        .all()
    )
    synth_email_ids = [e.id for e in synthetic_emails]
    print(f"    Found {len(synth_email_ids)} synthetic emails to delete: {synth_email_ids}")

    if synth_email_ids:
        # Delete predictions, entities, events linked to these emails
        db.query(EmailPrediction).filter(EmailPrediction.email_id.in_(synth_email_ids)).delete(synchronize_session=False)
        db.query(ExtractedEntity).filter(ExtractedEntity.email_id.in_(synth_email_ids)).delete(synchronize_session=False)
        db.query(Event).filter(Event.source_email_id.in_(synth_email_ids)).delete(synchronize_session=False)
        db.query(Email).filter(Email.id.in_(synth_email_ids)).delete(synchronize_session=False)
        db.commit()
        print("    Successfully deleted synthetic emails and cascaded records.")

    # ---------------------------------------------------------
    # STEP 2: Purge synthetic filler events
    # ---------------------------------------------------------
    print("\n[2] Purging synthetic filler timetable events...")
    # Explicit list of seed filler titles
    filler_titles = [
        "Data Structures & Algorithms",
        "Computer Networks Lab",
        "Database Management Systems",
        "Natural Language Processing Exam",
        "Computer Networks Lecture: Module 4",
        "Natural Language Processing Midterm Exam",
        "NLP Lab Session Shift",
    ]
    # Events with no summary or not from Google Calendar and matching filler titles
    deleted_events = 0
    for title in filler_titles:
        evs = (
            db.query(Event)
            .filter(
                Event.title == title,
                Event.source_email_id.is_(None),
                ~Event.summary.ilike("%Imported from Google Calendar%"),
            )
            .all()
        )
        for ev in evs:
            db.delete(ev)
            deleted_events += 1
    db.commit()
    print(f"    Deleted {deleted_events} synthetic filler timetable events.")

    # ---------------------------------------------------------
    # STEP 3: Sync full Google Calendar semester schedule
    # ---------------------------------------------------------
    print("\n[3] Synchronizing full Google Calendar timetable...")
    try:
        events_list, synced_count = calendar_service.sync_to_campus_events(db, user_id=1)
        print(f"    Fetched {len(events_list)} total calendar events; synced/updated {synced_count} into database!")
    except Exception as ex:
        print(f"    [!] Calendar sync notice: {ex}")

    # ---------------------------------------------------------
    # STEP 4: Re-evaluate proposals for remaining real emails
    # ---------------------------------------------------------
    print("\n[4] Re-evaluating schedule change proposals from genuine NMIMS emails...")
    real_emails = db.query(Email).all()
    print(f"    Total authentic NMIMS emails in DB: {len(real_emails)}")

    # Clean existing proposed events so we rebuild with correct dates & subjects
    db.query(Event).filter(Event.status == "PROPOSED").delete(synchronize_session=False)
    db.commit()

    rebuilt_proposals = 0
    for email in real_emails:
        nlp_res = nlp_service.analyze_email(
            subject=email.subject,
            body=email.body_text,
            sender_role=email.sender_role,
        )
        prop = nlp_res.get("proposed_event")
        if prop:
            start_date = None
            if prop.get("new_date"):
                try:
                    start_date = datetime.strptime(prop["new_date"], "%Y-%m-%d")
                except ValueError:
                    pass
            if not start_date and email.received_at:
                start_date = email.received_at

            ev = Event(
                user_id=email.user_id,
                source_email_id=email.id,
                title=prop.get("title") or "Schedule Change",
                subject=prop.get("subject"),
                event_type=prop.get("event_type", "LECTURE"),
                start_at=start_date,
                location=prop.get("new_location"),
                status="PROPOSED",
                summary=prop.get("summary"),
            )
            # Only keep if relevant to student's calendar subjects
            if event_service.is_event_relevant_to_student(ev):
                db.add(ev)
                rebuilt_proposals += 1

    db.commit()
    print(f"    Rebuilt {rebuilt_proposals} relevant timetable proposals strictly for student's enrolled courses.")

    # ---------------------------------------------------------
    # STEP 5: Final Summary Verification
    # ---------------------------------------------------------
    total_emails = db.query(Email).count()
    total_confirmed = db.query(Event).filter(Event.status == "CONFIRMED").count()
    total_proposed = db.query(Event).filter(Event.status == "PROPOSED").count()

    print("\n" + "=" * 70)
    print(f"  FINAL DATABASE STATE:")
    print(f"  - Total Real Emails: {total_emails}")
    print(f"  - Confirmed Timetable Classes: {total_confirmed} (From Google Calendar)")
    print(f"  - Active Calendar Subject Proposals: {total_proposed} (Date-aligned)")
    print("=" * 70)

    db.close()

if __name__ == "__main__":
    clean_and_sync()
