"""
Ingest real NMIMS emails and attached .eml notices from the connected Gmail account.

Senders:
  - ANJALI.UPADHYAY43@nmims.in
  - LAKSH.GUPTA28@nmims.in
"""

import os
import sys

# Prevent Windows console cp1252 encoding crashes on emojis in email titles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import base64
import httpx
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.email import Email, EmailPrediction
from backend.app.models.event import Event
from backend.app.schemas.email import EmailIngestRequest
from backend.app.services.calendar_service import calendar_service
from backend.app.services.email_service import email_service
from backend.app.services.attachment_extractor import attachment_extractor
from backend.app.services.email_ingest_service import email_ingest_service

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
SENDER_1 = "ANJALI.UPADHYAY43@nmims.in"
SENDER_2 = "LAKSH.GUPTA28@nmims.in"
QUERY = f"from:{SENDER_1} OR from:{SENDER_2}"

def run_ingest():
    print("=" * 65)
    print("  CampusAI - Real Email Ingestion from NMIMS Senders")
    print("=" * 65)

    db = SessionLocal()
    try:
        token = calendar_service.get_valid_access_token(db, 1)
    except Exception as e:
        print(f"[!] Error getting valid token: {e}")
        db.close()
        return

    headers = {"Authorization": f"Bearer {token}"}

    print(f"[*] Querying Gmail: {QUERY}")
    with httpx.Client(timeout=30.0) as client:
        res = client.get(f"{GMAIL_API_BASE}/messages", headers=headers, params={"q": QUERY})
        if res.status_code != 200:
            print(f"[!] Failed to search messages: {res.status_code} - {res.text}")
            db.close()
            return

        messages = res.json().get("messages", [])
        print(f"[+] Found {len(messages)} matching Gmail messages\n")

        ingested_count = 0
        duplicate_count = 0
        proposals_count = 0

        for i, m in enumerate(messages, 1):
            mid = m["id"]
            det_res = client.get(f"{GMAIL_API_BASE}/messages/{mid}", headers=headers, params={"format": "full"})
            if det_res.status_code != 200:
                continue

            msg_data = det_res.json()
            payload = msg_data.get("payload", {})
            parsed = email_ingest_service._parse_gmail_payload(msg_data)

            print(f"\n--- [{i}/{len(messages)}] Message ID: {mid} ---")
            print(f"Subject: {parsed['subject']}")
            print(f"From: {parsed['sender']}")

            # 1. Ingest main body if present
            if parsed["body"] and len(parsed["body"].strip()) > 15:
                req = EmailIngestRequest(
                    provider_message_id=mid,
                    subject=parsed["subject"],
                    sender=parsed["sender"],
                    sender_role=parsed["sender_role"],
                    body=parsed["body"],
                )
                rec, is_dup = email_service.ingest_email(db, 1, req)
                if is_dup:
                    duplicate_count += 1
                    print("  [DUPLICATE] Main body already ingested")
                else:
                    ingested_count += 1
                    pred = db.query(EmailPrediction).filter(EmailPrediction.email_id == rec.id).first()
                    cat = pred.category if pred else "GENERAL"
                    imp = pred.importance if pred else "LOW"
                    print(f"  [INGESTED] Main email -> Category: {cat}, Importance: {imp}")
                    if db.query(Event).filter(Event.source_email_id == rec.id).first():
                        proposals_count += 1

            # 2. Extract and ingest attachments (.eml notices, pdfs, etc.)
            parts = payload.get("parts", [])
            att_idx = 0

            def process_parts(part_list):
                nonlocal att_idx, ingested_count, duplicate_count, proposals_count
                for part in part_list:
                    filename = part.get("filename")
                    body_dict = part.get("body", {})
                    att_id = body_dict.get("attachmentId")

                    if filename and att_id:
                        att_idx += 1
                        print(f"  -> Found Attachment #{att_idx}: '{filename}'")
                        try:
                            att_url = f"{GMAIL_API_BASE}/messages/{mid}/attachments/{att_id}"
                            att_res = client.get(att_url, headers=headers)
                            if att_res.status_code == 200:
                                raw_b64 = att_res.json().get("data", "")
                                file_bytes = base64.urlsafe_b64decode(raw_b64.encode())
                                extracted = attachment_extractor.extract_from_attachment(filename, file_bytes)
                                print(f"     Extracted {len(extracted)} notice(s) from '{filename}'")

                                for sub_idx, sub_item in enumerate(extracted, 1):
                                    att_req = EmailIngestRequest(
                                        provider_message_id=f"{mid}-att-{att_idx}-{sub_idx}",
                                        subject=sub_item.get("subject") or filename,
                                        sender=sub_item.get("sender") or parsed["sender"],
                                        sender_role="FACULTY" if "nmims" in (sub_item.get("sender") or "").lower() else parsed["sender_role"],
                                        body=sub_item.get("body") or "",
                                    )
                                    att_rec, att_dup = email_service.ingest_email(db, 1, att_req)
                                    if att_dup:
                                        duplicate_count += 1
                                        print(f"     [DUPLICATE] '{att_req.subject[:45]}' already in DB")
                                    else:
                                        ingested_count += 1
                                        pred = db.query(EmailPrediction).filter(EmailPrediction.email_id == att_rec.id).first()
                                        cat = pred.category if pred else "GENERAL"
                                        imp = pred.importance if pred else "LOW"
                                        print(f"     [INGESTED] '{att_req.subject[:45]}' -> {cat} [{imp}]")
                                        if db.query(Event).filter(Event.source_email_id == att_rec.id).first():
                                            proposals_count += 1
                                            print(f"       -> [PROPOSAL CREATED] Event extracted for timetable!")
                        except Exception as ex:
                            print(f"     [!] Failed to extract attachment '{filename}': {ex}")

                    if "parts" in part:
                        process_parts(part["parts"])

            process_parts(parts)

    db.close()

    print("\n" + "=" * 65)
    print(f"  COMPLETED: Ingested: {ingested_count} notices | Duplicates: {duplicate_count} | Proposals: {proposals_count}")
    print("=" * 65)

if __name__ == "__main__":
    run_ingest()
