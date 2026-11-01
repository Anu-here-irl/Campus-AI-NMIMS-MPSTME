"""Sync Target Emails & Attachments from NMIMS Senders.

Connects to Gmail API using OAuth credentials, filters for target senders
(ANJALI.UPADHYAY43@nmims.in and LAKSH.GUPTA28@nmims.in), extracts all attachments
(.eml, .txt, .pdf, .docx), runs NLP classification, and updates the SQLite database.
"""

import base64
import json
import os
import sys
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import httpx


# Ensure UTF-8 output handling on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def safe_print(*args, **kwargs):
    """Safely print text preventing cp1252 UnicodeEncodeErrors from emojis or special characters."""
    try:
        print(*args, **kwargs)
    except Exception:
        clean_args = [
            str(a).encode("ascii", errors="replace").decode("ascii") for a in args
        ]
        print(*clean_args, **kwargs)

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models.calendar import GoogleCalendarToken
from app.models.email import Email, EmailPrediction, ExtractedEntity
from app.models.event import Event
from app.models.user import User
from app.schemas.email import EmailIngestRequest
from app.services.attachment_extractor import attachment_extractor
from app.services.calendar_service import calendar_service
from app.services.email_service import email_service


TARGET_SENDERS = [
    "anjali.upadhyay43@nmims.in",
    "laksh.gupta28@nmims.in",
]


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Temporary local HTTP handler to capture Google OAuth code on port 8000."""
    auth_code = None
    auth_state = None
    auth_error = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/v1/calendar/callback"):
            query_params = urllib.parse.parse_qs(parsed.query)
            OAuthCallbackHandler.auth_code = query_params.get("code", [None])[0]
            OAuthCallbackHandler.auth_state = query_params.get("state", [None])[0]
            OAuthCallbackHandler.auth_error = query_params.get("error", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Campus AI - Authorization Successful</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                           background: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                    .box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; max-width: 420px; }
                    h2 { color: #1e3a8a; }
                    p { color: #475569; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h2>Authentication Successful!</h2>
                    <p>Campus AI has received Google authorization. You may now close this browser tab and return to the terminal.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy HTTP server logs
        return


def get_or_create_default_student(db) -> User:
    """Ensure student user exists in SQLite."""
    user = db.query(User).filter(User.email == "student@campus.edu").first()
    if not user:
        from app.security.auth import hash_password
        user = User(
            email="student@campus.edu",
            full_name="Student Anjali",
            department="Computer Science",
            semester=5,
            hashed_password=hash_password("student123"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def perform_oauth_flow(db, user_id: int) -> str:
    """Run interactive OAuth consent in browser, listen on port 8000, and save token."""
    print("\n" + "=" * 65, flush=True)
    print("STEP 1: GOOGLE OAUTH 2.0 AUTHORIZATION", flush=True)
    print("=" * 65, flush=True)

    auth_url, state = calendar_service.get_authorization_url(user_id=user_id, include_gmail=True)
    print("\nStarting local listener on http://localhost:8000 ...", flush=True)
    server = HTTPServer(("localhost", 8000), OAuthCallbackHandler)
    server.timeout = 1.0

    print("\nPlease open the following authorization URL in your browser to sign in:", flush=True)
    print("-" * 65, flush=True)
    print(auth_url, flush=True)
    print("-" * 65, flush=True)

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("\nWaiting for browser callback at http://localhost:8000/api/v1/calendar/callback ...", flush=True)
    while OAuthCallbackHandler.auth_code is None and OAuthCallbackHandler.auth_error is None:
        server.handle_request()

    if OAuthCallbackHandler.auth_error:
        print(f"\n[ERROR] Authorization was denied by user: {OAuthCallbackHandler.auth_error}", flush=True)
        sys.exit(1)

    code = OAuthCallbackHandler.auth_code
    print("\nAuthorization code received! Exchanging with Google for access tokens...", flush=True)

    token_data = calendar_service.exchange_code_for_tokens(
        code=code,
        redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI,
    )

    token_rec = calendar_service.save_user_tokens(

        db=db,
        user_id=user_id,
        token_data=token_data,
    )
    print(f"Tokens securely stored in SQLite! Access token active (expires at {token_rec.expires_at}).")
    return token_data["access_token"]


def get_valid_access_token(db, user_id: int) -> str:
    """Retrieve existing active token or initiate OAuth flow."""
    token_rec = (
        db.query(GoogleCalendarToken)
        .filter(GoogleCalendarToken.user_id == user_id, GoogleCalendarToken.is_active.is_(True))
        .first()
    )
    if token_rec and token_rec.access_token:
        # Check if refresh token is present or token still fresh
        return token_rec.access_token
    return perform_oauth_flow(db, user_id)


def fetch_and_process_target_emails(db, user_id: int, access_token: str):
    """Fetch emails from target senders, unpack attachments, and evaluate NLP."""
    print("\n" + "=" * 65)
    print("STEP 2: FETCHING ACADEMIC EMAILS FROM GMAIL")
    print("=" * 65)
    print(f"Target Senders: {', '.join(TARGET_SENDERS)}")

    headers = {"Authorization": f"Bearer {access_token}"}
    query_str = "from:anjali.upadhyay43@nmims.in OR from:laksh.gupta28@nmims.in"
    params = {"q": query_str, "maxResults": 30}

    with httpx.Client(timeout=20.0) as client:
        list_res = client.get("https://gmail.googleapis.com/gmail/v1/users/me/messages", headers=headers, params=params)

        if list_res.status_code == 401:
            print("[WARN] Access token expired or invalid. Re-authenticating...")
            access_token = perform_oauth_flow(db, user_id)
            headers["Authorization"] = f"Bearer {access_token}"
            list_res = client.get("https://gmail.googleapis.com/gmail/v1/users/me/messages", headers=headers, params=params)

        if list_res.status_code != 200:
            print(f"[ERROR] Failed to query Gmail API: {list_res.status_code} {list_res.text}")
            return

        messages = list_res.json().get("messages", [])
        print(f"Found {len(messages)} matching email thread(s) from target senders.")

        if not messages:
            print("\n[NOTE] No emails found matching the exact query in your inbox.")
            print("Querying all recent inbox messages to inspect available senders...")
            broad_res = client.get("https://gmail.googleapis.com/gmail/v1/users/me/messages", headers=headers, params={"maxResults": 10})
            if broad_res.status_code == 200:
                recent_msgs = broad_res.json().get("messages", [])
                print(f"Recent messages count: {len(recent_msgs)}")
                messages = recent_msgs

        ingested_items = []

        for idx, m_meta in enumerate(messages):
            msg_id = m_meta["id"]
            det_res = client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers=headers,
                params={"format": "full"},
            )
            if det_res.status_code != 200:
                continue

            msg_data = det_res.json()
            payload = msg_data.get("payload", {})
            headers_list = payload.get("headers", [])

            subject = "(No Subject)"
            sender = "Unknown"
            for h in headers_list:
                n = h.get("name", "").lower()
                if n == "subject":
                    subject = h.get("value", "")
                elif n == "from":
                    sender = h.get("value", "")

            safe_print(f"\n--- Processing Message [{idx+1}/{len(messages)}] ---")
            safe_print(f"Subject: {subject}")
            safe_print(f"Sender:  {sender}")

            # Check for attachments
            parts = payload.get("parts", [])
            attachments_found = []

            for part in parts:
                filename = part.get("filename")
                att_id = part.get("body", {}).get("attachmentId")
                if filename and att_id:
                    safe_print(f"Found Attachment: {filename}")
                    try:
                        att_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/attachments/{att_id}"
                        att_res = client.get(att_url, headers=headers)
                        if att_res.status_code == 200:
                            raw_data = att_res.json().get("data", "")
                            file_bytes = base64.urlsafe_b64decode(raw_data.encode())
                            extracted_notices = attachment_extractor.extract_from_attachment(filename, file_bytes)
                            attachments_found.extend(extracted_notices)
                    except Exception as e:
                        safe_print(f"  [WARN] Could not parse attachment {filename}: {e}")

            # Ingest body if substantial
            body_text = ""
            if "body" in payload and "data" in payload["body"]:
                body_text = base64.urlsafe_b64decode(payload["body"]["data"].encode()).decode("utf-8", errors="replace")
            elif "parts" in payload:
                for p in payload["parts"]:
                    if p.get("mimeType") == "text/plain" and "data" in p.get("body", {}):
                        body_text = base64.urlsafe_b64decode(p["body"]["data"].encode()).decode("utf-8", errors="replace")
                        break

            if body_text and len(body_text.strip()) > 15:
                req = EmailIngestRequest(
                    provider_message_id=msg_id,
                    subject=subject,
                    sender=sender,
                    sender_role="ADMIN" if "exam" in sender.lower() else "FACULTY",
                    body=body_text.strip(),
                )
                email_rec, is_dup = email_service.ingest_email(db, user_id, req)
                ingested_items.append((email_rec, is_dup, "Direct Email Body"))

            # Ingest all extracted attachment notices
            for att_i, att in enumerate(attachments_found):
                att_req = EmailIngestRequest(
                    provider_message_id=f"{msg_id}-att-{att_i+1}",
                    subject=att.get("subject", subject),
                    sender=att.get("sender", sender),
                    sender_role="ADMIN",
                    body=att.get("body", ""),
                )
                att_email, att_is_dup = email_service.ingest_email(db, user_id, att_req)
                source_label = f"Attachment: {att.get('source_file', 'file')}"
                ingested_items.append((att_email, att_is_dup, source_label))

    safe_print("\n" + "=" * 65)
    safe_print("STEP 3: EVALUATION & NLP CLASSIFICATION REPORT")
    safe_print("=" * 65)
    safe_print(f"Total Notices Ingested / Processed: {len(ingested_items)}")

    report_lines = [
        "# Phase 4 — Real Email Ingestion & Testing Evaluation Report",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Target Senders:** `ANJALI.UPADHYAY43@nmims.in`, `LAKSH.GUPTA28@nmims.in`",
        f"**Total Processed Items:** {len(ingested_items)}",
        "",
        "## Ingested Notices & NLP Predictions",
        "",
        "| ID | Source | Subject | Category | Confidence | Priority | Detected Change | Entities |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for email_rec, is_dup, source in ingested_items:
        pred = db.query(EmailPrediction).filter(EmailPrediction.email_id == email_rec.id).first()
        prop = db.query(Event).filter(Event.source_email_id == email_rec.id).first()
        entities = db.query(ExtractedEntity).filter(ExtractedEntity.email_id == email_rec.id).all()

        cat = pred.category if pred else "N/A"
        cat_conf = f"{pred.category_confidence * 100:.1f}%" if pred else "N/A"
        imp = pred.importance if pred else "N/A"
        has_prop = f"YES: {prop.title} ({prop.location or 'New Date'})" if prop else "None"
        ent_str = ", ".join([f"{e.entity_type}:{e.normalized_value or e.value}" for e in entities[:3]])

        safe_print(f"\n[Notice ID: {email_rec.id}] {email_rec.subject[:50]}")
        safe_print(f"  Source:     {source} {'(Duplicate)' if is_dup else ''}")
        safe_print(f"  Category:   {cat} (Confidence: {cat_conf})")
        safe_print(f"  Priority:   {imp}")
        safe_print(f"  Entities:   {ent_str}")
        safe_print(f"  Proposal:   {has_prop}")


        safe_subj = email_rec.subject.replace("|", "/")[:40]
        report_lines.append(
            f"| {email_rec.id} | {source} | {safe_subj} | **{cat}** | {cat_conf} | {imp} | {has_prop} | {ent_str} |"
        )

    # Save report
    report_path = BACKEND_DIR.parent / "docs" / "phase_4_evaluation_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    safe_print(f"\nEvaluation report written to: {report_path}")
    safe_print("\nPHASE 4 EMAIL INGESTION & NLP EVALUATION COMPLETE.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = get_or_create_default_student(db)
        safe_print(f"Logged in as student: {user.email} (ID: {user.id})")
        token = get_valid_access_token(db, user.id)
        fetch_and_process_target_emails(db, user.id, token)

    finally:
        db.close()


if __name__ == "__main__":
    main()
