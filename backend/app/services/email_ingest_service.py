"""Email Ingestion Service for live Gmail integration, batch imports, and NLP processing."""

import base64
from typing import Any
import httpx
from sqlalchemy.orm import Session

from pathlib import Path
from ..models.email import Email, EmailPrediction
from ..models.event import Event
from ..schemas.email import EmailIngestRequest
from .email_service import email_service
from .attachment_extractor import attachment_extractor



class EmailIngestService:
    """Manages real email ingestion from Gmail API or batch feeds into the NLP pipeline."""

    GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

    @classmethod
    def ingest_from_gmail(
        cls,
        db: Session,
        user_id: int,
        access_token: str,
        max_results: int = 25,
        query: str | None = None,
    ) -> dict[str, Any]:
        """Fetch emails directly from user's Gmail inbox via REST API and process through NLP."""
        headers = {"Authorization": f"Bearer {access_token}"}
        params: dict[str, Any] = {"maxResults": min(max_results, 50)}
        if query:
            params["q"] = query

        ingested_count = 0
        duplicate_count = 0
        proposals_created = 0
        categories_detected: dict[str, int] = {}

        try:
            with httpx.Client(timeout=15.0) as client:
                list_res = client.get(f"{cls.GMAIL_API_BASE}/messages", headers=headers, params=params)
                if list_res.status_code != 200:
                    return {
                        "status": "ERROR",
                        "error": f"Gmail API returned {list_res.status_code}: {list_res.text}",
                        "ingested_count": 0,
                    }

                msg_list = list_res.json().get("messages", [])
                for item in msg_list:
                    msg_id = item.get("id")
                    if not msg_id:
                        continue

                    # Fetch message detail
                    detail_res = client.get(
                        f"{cls.GMAIL_API_BASE}/messages/{msg_id}",
                        headers=headers,
                        params={"format": "full"},
                    )
                    if detail_res.status_code != 200:
                        continue

                    msg_data = detail_res.json()
                    parsed = cls._parse_gmail_payload(msg_data)

                    # Check for attachments in message parts
                    attachment_items = cls._extract_attachments_from_gmail(
                        client=client,
                        headers=headers,
                        msg_id=msg_id,
                        payload=msg_data.get("payload", {}),
                    )

                    # Ingest the main email body if present
                    if parsed["body"] and len(parsed["body"].strip()) > 10:
                        req = EmailIngestRequest(
                            provider_message_id=msg_id,
                            subject=parsed["subject"],
                            sender=parsed["sender"],
                            sender_role=parsed["sender_role"],
                            body=parsed["body"],
                        )
                        email_rec, is_dup = email_service.ingest_email(db, user_id, req)
                        if is_dup:
                            duplicate_count += 1
                        else:
                            ingested_count += 1
                            cls._tally_predictions(db, email_rec.id, categories_detected)
                            if db.query(Event).filter(Event.source_email_id == email_rec.id).first():
                                proposals_created += 1

                    # Ingest each extracted attachment notice as a distinct academic email item
                    for att_idx, att_item in enumerate(attachment_items):
                        att_req = EmailIngestRequest(
                            provider_message_id=f"{msg_id}-att-{att_idx+1}",
                            subject=att_item["subject"],
                            sender=att_item.get("sender") or parsed["sender"],
                            sender_role=parsed["sender_role"],
                            body=att_item["body"],
                        )
                        att_email, att_is_dup = email_service.ingest_email(db, user_id, att_req)
                        if att_is_dup:
                            duplicate_count += 1
                        else:
                            ingested_count += 1
                            cls._tally_predictions(db, att_email.id, categories_detected)
                            if db.query(Event).filter(Event.source_email_id == att_email.id).first():
                                proposals_created += 1


            return {
                "status": "SUCCESS",
                "ingested_count": ingested_count,
                "duplicate_count": duplicate_count,
                "proposals_created": proposals_created,
                "categories_detected": categories_detected,
            }

        except httpx.RequestError as e:
            return {"status": "ERROR", "error": f"Network error during Gmail sync: {str(e)}"}

    @classmethod
    def ingest_batch_items(
        cls,
        db: Session,
        user_id: int,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Ingest a batch of academic emails (e.g. from JSON or test dataset) into the NLP engine."""
        ingested_count = 0
        duplicate_count = 0
        proposals_created = 0
        categories_detected: dict[str, int] = {}

        for item in items:
            req = EmailIngestRequest(
                provider_message_id=item.get("provider_message_id") or item.get("id"),
                subject=item.get("subject", "(No Subject)"),
                sender=item.get("sender", "academic-admin@campus.edu"),
                sender_role=item.get("sender_role", "ADMIN"),
                body=item.get("body", ""),
            )

            email_rec, is_dup = email_service.ingest_email(db, user_id, req)
            if is_dup:
                duplicate_count += 1
            else:
                ingested_count += 1
                pred = (
                    db.query(EmailPrediction)
                    .filter(EmailPrediction.email_id == email_rec.id)
                    .first()
                )
                if pred:
                    cat = pred.category or "GENERAL"
                    categories_detected[cat] = categories_detected.get(cat, 0) + 1

                has_prop = (
                    db.query(Event)
                    .filter(Event.source_email_id == email_rec.id)
                    .first()
                )
                if has_prop:
                    proposals_created += 1

        return {
            "status": "SUCCESS",
            "ingested_count": ingested_count,
            "duplicate_count": duplicate_count,
            "proposals_created": proposals_created,
            "categories_detected": categories_detected,
        }

    @classmethod
    def _parse_gmail_payload(cls, data: dict[str, Any]) -> dict[str, str]:
        """Extract subject, sender, role, and plain text body from Gmail API response."""
        headers = data.get("payload", {}).get("headers", [])
        subject = "(No Subject)"
        sender = "Unknown Sender"

        for h in headers:
            name = h.get("name", "").lower()
            val = h.get("value", "")
            if name == "subject":
                subject = val
            elif name == "from":
                sender = val

        # Infer sender role
        sender_lower = sender.lower()
        if any(w in sender_lower for w in ["prof", "faculty", "instructor", "teacher", "dr."]):
            sender_role = "FACULTY"
        elif any(w in sender_lower for w in ["exam", "registrar", "dean", "office", "admin", "department"]):
            sender_role = "ADMIN"
        elif any(w in sender_lower for w in ["club", "society", "council", "fest"]):
            sender_role = "STUDENT_BODY"
        else:
            sender_role = "EXTERNAL"

        # Body extraction
        body = ""
        payload = data.get("payload", {})

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    raw = part["body"]["data"]
                    body = base64.urlsafe_b64decode(raw.encode()).decode("utf-8", errors="replace")
                    break
        elif "body" in payload and "data" in payload["body"]:
            raw = payload["body"]["data"]
            body = base64.urlsafe_b64decode(raw.encode()).decode("utf-8", errors="replace")

        if not body:
            body = data.get("snippet", "")

        return {
            "subject": subject,
            "sender": sender,
            "sender_role": sender_role,
            "body": body,
        }

    @classmethod
    def _extract_attachments_from_gmail(
        cls,
        client: httpx.Client,
        headers: dict[str, str],
        msg_id: str,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Find and download attachments from Gmail message payload parts."""
        items: list[dict[str, Any]] = []
        parts = payload.get("parts", [])

        for part in parts:
            filename = part.get("filename")
            body_dict = part.get("body", {})
            att_id = body_dict.get("attachmentId")

            if filename and att_id:
                try:
                    att_url = f"{cls.GMAIL_API_BASE}/messages/{msg_id}/attachments/{att_id}"
                    att_res = client.get(att_url, headers=headers)
                    if att_res.status_code == 200:
                        raw_data = att_res.json().get("data", "")
                        file_bytes = base64.urlsafe_b64decode(raw_data.encode())
                        extracted = attachment_extractor.extract_from_attachment(filename, file_bytes)
                        items.extend(extracted)
                except Exception:
                    pass

        return items

    @classmethod
    def _tally_predictions(cls, db: Session, email_id: int, categories_detected: dict[str, int]) -> None:
        """Helper to tally category predictions for summaries."""
        pred = (
            db.query(EmailPrediction)
            .filter(EmailPrediction.email_id == email_id)
            .first()
        )
        if pred:
            cat = pred.category or "GENERAL"
            categories_detected[cat] = categories_detected.get(cat, 0) + 1

    @classmethod
    def ingest_local_attachments_folder(
        cls,
        db: Session,
        user_id: int,
        folder_path: str | Path,
    ) -> dict[str, Any]:
        """Ingest all attachment files (.eml, .txt, .pdf, .docx) from a local directory."""
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {"status": "ERROR", "error": f"Folder {folder} does not exist"}

        ingested_count = 0
        duplicate_count = 0
        proposals_created = 0
        categories_detected: dict[str, int] = {}

        for file_path in folder.iterdir():
            if file_path.is_file():
                try:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    extracted_items = attachment_extractor.extract_from_attachment(file_path.name, file_bytes)
                    for idx, item in enumerate(extracted_items):
                        req = EmailIngestRequest(
                            provider_message_id=f"local-{file_path.stem}-{idx+1}",
                            subject=item.get("subject", file_path.name),
                            sender=item.get("sender", "Academic Office"),
                            sender_role="ADMIN",
                            body=item.get("body", ""),
                        )
                        email_rec, is_dup = email_service.ingest_email(db, user_id, req)
                        if is_dup:
                            duplicate_count += 1
                        else:
                            ingested_count += 1
                            cls._tally_predictions(db, email_rec.id, categories_detected)
                            if db.query(Event).filter(Event.source_email_id == email_rec.id).first():
                                proposals_created += 1
                except Exception:
                    pass

        return {
            "status": "SUCCESS",
            "ingested_count": ingested_count,
            "duplicate_count": duplicate_count,
            "proposals_created": proposals_created,
            "categories_detected": categories_detected,
        }


email_ingest_service = EmailIngestService()

