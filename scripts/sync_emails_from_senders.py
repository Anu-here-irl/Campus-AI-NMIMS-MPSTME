"""
Sync emails from specific NMIMS senders into CampusAI database.

Senders:
  - ANJALI.UPADHYAY43@nmims.in
  - LAKSH.GUPTA28@nmims.in

Automatically refreshes the stored OAuth token, fetches emails from
those 2 senders via Gmail API, processes them through the NLP pipeline,
and stores results in campusai.db.
"""

import sys
import os
import sqlite3
import base64
import json
import httpx
from datetime import datetime, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "campusai.db"))
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

SENDER_1 = "ANJALI.UPADHYAY43@nmims.in"
SENDER_2 = "LAKSH.GUPTA28@nmims.in"
GMAIL_QUERY = "from:{} OR from:{}".format(SENDER_1, SENDER_2)
MAX_RESULTS = 50


def get_conn():
    return sqlite3.connect(DB_PATH)


def load_credentials():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    client_id = None
    client_secret = None

    # Search in both root and backend/ subdirectory
    search_dirs = [base, os.path.join(base, "backend")]

    for search_dir in search_dirs:
        env_file = os.path.join(search_dir, ".env")
        if os.path.exists(env_file) and not client_id:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GOOGLE_CALENDAR_CLIENT_ID="):
                        client_id = line.split("=", 1)[1].strip().strip('"')
                    elif line.startswith("GOOGLE_CALENDAR_CLIENT_SECRET="):
                        client_secret = line.split("=", 1)[1].strip().strip('"')

    if not client_id:
        for search_dir in search_dirs:
            for fname in ["client_secret.json", "credentials.json", "oauth_credentials.json"]:
                fpath = os.path.join(search_dir, fname)
                if os.path.exists(fpath):
                    with open(fpath, encoding="utf-8") as f:
                        data = json.load(f)
                    cfg = data.get("web") or data.get("installed") or data
                    client_id = cfg.get("client_id")
                    client_secret = cfg.get("client_secret")
                    break
            if client_id:
                break

    return client_id, client_secret


def refresh_token(refresh_tok, client_id, client_secret):
    print("[*] Refreshing Google access token...")
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok,
    }
    with httpx.Client(timeout=15.0) as client:
        res = client.post(TOKEN_ENDPOINT, data=payload)
        if res.status_code != 200:
            print("[!] Token refresh failed: {} - {}".format(res.status_code, res.text))
            sys.exit(1)
        data = res.json()

    new_access = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    new_expiry = (datetime.utcnow() + timedelta(seconds=int(expires_in))).isoformat()

    conn = get_conn()
    conn.execute(
        "UPDATE google_calendar_tokens SET access_token=?, expires_at=?, updated_at=? WHERE is_active=1",
        (new_access, new_expiry, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    print("[+] Token refreshed. Valid until: {} UTC".format(new_expiry))
    return new_access


def fetch_messages(access_token):
    headers = {"Authorization": "Bearer {}".format(access_token)}
    params = {"q": GMAIL_QUERY, "maxResults": MAX_RESULTS}
    print("\n[*] Querying Gmail: {}".format(GMAIL_QUERY))

    with httpx.Client(timeout=20.0) as client:
        res = client.get("{}/messages".format(GMAIL_API_BASE), headers=headers, params=params)
        if res.status_code == 401:
            print("[!] Gmail 401 - token may not have gmail.readonly scope. Response: {}".format(res.text[:300]))
            sys.exit(1)
        if res.status_code != 200:
            print("[!] Gmail API error {}: {}".format(res.status_code, res.text[:300]))
            sys.exit(1)
        messages = res.json().get("messages", [])
        print("[+] Found {} messages".format(len(messages)))
        return messages


def decode_b64(data):
    try:
        padded = data + "=" * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")
    except Exception:
        return ""


def extract_body(payload):
    parts = payload.get("parts", [])
    if parts:
        for part in parts:
            mime = part.get("mimeType", "")
            if mime == "text/plain":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    return decode_b64(body_data)
        for part in parts:
            mime = part.get("mimeType", "")
            if mime == "text/html":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    return decode_b64(body_data)
    else:
        body_data = payload.get("body", {}).get("data", "")
        if body_data:
            return decode_b64(body_data)
    return ""


def parse_msg(msg_data):
    payload = msg_data.get("payload", {})
    hdrs = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
    subject = hdrs.get("subject", "(No Subject)")
    sender = hdrs.get("from", "unknown@nmims.in")
    body = extract_body(payload).strip()
    return {"subject": subject, "sender": sender, "body": body}


def store_email(user_id, msg_id, parsed):
    """Insert into DB and run NLP. Returns True if new, False if duplicate."""
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM emails WHERE provider_message_id=?", (msg_id,)
    ).fetchone()
    if existing:
        conn.close()
        return False

    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        """INSERT INTO emails (user_id, provider_message_id, subject, sender, sender_role,
           body_text, is_read, created_at, received_at)
           VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
        (
            user_id,
            msg_id,
            parsed["subject"][:500],
            parsed["sender"][:255],
            "FACULTY",
            parsed["body"],
            now,
            now,
        ),
    )
    email_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Run NLP
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from backend.app.services.nlp_service import nlp_service
        result = nlp_service.analyze_email(
            subject=parsed["subject"],
            body=parsed["body"],
            sender_role="FACULTY",
        )
        conn2 = get_conn()
        conn2.execute(
            """INSERT OR IGNORE INTO email_predictions
               (email_id, category, category_confidence, importance, importance_confidence,
                uncertain, model_version, created_at)
               VALUES (?, ?, ?, ?, ?, 0, '1.0.0', ?)""",
            (
                email_id,
                result.category,
                result.category_confidence,
                result.importance,
                result.importance_confidence,
                now,
            ),
        )
        conn2.commit()
        conn2.close()
    except Exception as e:
        print("   [!] NLP failed for email {}: {}".format(email_id, e))

    return True


def main():
    print("=" * 60)
    print("  CampusAI - Gmail Sync from NMIMS Senders")
    print("=" * 60)

    client_id, client_secret = load_credentials()
    if not client_id or not client_secret:
        print("[!] Could not find GOOGLE_CALENDAR_CLIENT_ID/SECRET in .env or client_secret.json")
        sys.exit(1)
    print("[+] Credentials loaded (client_id: {}...)".format(client_id[:20]))

    conn = get_conn()
    row = conn.execute(
        "SELECT user_id, refresh_token, access_token, expires_at FROM google_calendar_tokens WHERE is_active=1"
    ).fetchone()
    conn.close()

    if not row:
        print("[!] No active Google token in DB. Connect Google account first.")
        sys.exit(1)

    user_id, refresh_tok, access_token, expires_at = row
    print("[+] Found token for user_id={}".format(user_id))

    # Refresh if expired
    try:
        expiry = datetime.fromisoformat(str(expires_at))
        if expiry <= datetime.utcnow() + timedelta(minutes=2):
            access_token = refresh_token(refresh_tok, client_id, client_secret)
        else:
            print("[+] Token still valid until {} UTC".format(expiry.strftime("%H:%M:%S")))
    except Exception:
        access_token = refresh_token(refresh_tok, client_id, client_secret)

    messages = fetch_messages(access_token)
    if not messages:
        print("\n[!] No emails found from those 2 senders in this Gmail inbox.")
        print("    Make sure the connected Gmail account has emails FROM:")
        print("    - {}".format(SENDER_1))
        print("    - {}".format(SENDER_2))
        return

    ingested = 0
    duplicates = 0
    print("\n[*] Processing {} emails through NLP...\n".format(len(messages)))

    with httpx.Client(timeout=20.0) as client:
        for i, msg in enumerate(messages, 1):
            msg_id = msg.get("id")
            if not msg_id:
                continue
            detail_res = client.get(
                "{}/messages/{}".format(GMAIL_API_BASE, msg_id),
                headers={"Authorization": "Bearer {}".format(access_token)},
                params={"format": "full"},
            )
            if detail_res.status_code != 200:
                continue

            parsed = parse_msg(detail_res.json())
            if len(parsed["body"]) < 5:
                continue

            is_new = store_email(user_id, msg_id, parsed)
            status = "NEW      " if is_new else "DUPLICATE"
            print("  [{:02d}] [{}] {}".format(i, status, parsed["subject"][:55]))
            print("         From: {}".format(parsed["sender"]))

            if is_new:
                ingested += 1
            else:
                duplicates += 1

    print("\n" + "=" * 60)
    total = get_conn().execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    print("  DONE - Ingested: {}  |  Duplicates: {}  |  Total in DB: {}".format(ingested, duplicates, total))
    print("=" * 60)
    print("\n>> Pull-to-refresh the Emails screen in the app to see them!")


if __name__ == "__main__":
    main()
