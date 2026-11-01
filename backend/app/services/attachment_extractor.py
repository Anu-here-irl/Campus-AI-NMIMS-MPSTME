"""Attachment Extractor to unpack and extract academic email data from attachments."""

import base64
import email
from email import policy
import io
import re
from typing import Any


class AttachmentExtractor:
    """Extracts text, metadata, and forwarded notices from various attachment formats."""

    TARGET_SENDERS = [
        "anjali.upadhyay43@nmims.in",
        "laksh.gupta28@nmims.in",
    ]

    @classmethod
    def is_target_sender(cls, sender_str: str) -> bool:
        """Check if sender matches any of the specified target email IDs."""
        if not sender_str:
            return False
        sender_clean = sender_str.lower().strip()
        return any(target in sender_clean for target in cls.TARGET_SENDERS)

    @classmethod
    def extract_from_eml_bytes(cls, eml_bytes: bytes) -> dict[str, Any]:
        """Parse an attached .eml file (RFC 822) to retrieve inner email content."""
        msg = email.message_from_bytes(eml_bytes, policy=policy.default)
        subject = msg.get("subject", "(No Subject)")
        sender = msg.get("from", "Academic Office")
        date_str = msg.get("date", "")

        # Extract plain text or html body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in disposition:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
                elif content_type == "text/html" and not body and "attachment" not in disposition:
                    html_content = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    body = cls.strip_html(html_content)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="replace")

        return {
            "subject": subject,
            "sender": sender,
            "date": date_str,
            "body": body.strip(),
        }

    @classmethod
    def extract_from_attachment(cls, filename: str, file_bytes: bytes) -> list[dict[str, Any]]:
        """Extract academic notice items from attachment bytes based on file extension."""
        filename_lower = filename.lower()
        items = []

        # 1. Forwarded Email (.eml or .msg)
        if filename_lower.endswith(".eml") or filename_lower.endswith(".msg"):
            extracted = cls.extract_from_eml_bytes(file_bytes)
            items.append({
                "source_file": filename,
                "subject": extracted["subject"],
                "sender": extracted["sender"],
                "body": extracted["body"],
            })

        # 2. Plain text (.txt, .log)
        elif filename_lower.endswith(".txt") or filename_lower.endswith(".log"):
            text = file_bytes.decode("utf-8", errors="replace").strip()
            # Split if multiple emails separated by headers or dividers
            emails = cls._split_multiple_notices_in_text(filename, text)
            items.extend(emails)

        # 3. HTML file (.html, .htm)
        elif filename_lower.endswith(".html") or filename_lower.endswith(".htm"):
            raw_html = file_bytes.decode("utf-8", errors="replace")
            clean_text = cls.strip_html(raw_html)
            items.append({
                "source_file": filename,
                "subject": f"Notice from {filename}",
                "sender": "Academic Faculty",
                "body": clean_text,
            })

        # 4. Word Document (.docx)
        elif filename_lower.endswith(".docx"):
            text = cls._extract_docx(file_bytes)
            items.append({
                "source_file": filename,
                "subject": f"Document: {filename}",
                "sender": "Academic Department",
                "body": text,
            })

        # 5. PDF Document (.pdf)
        elif filename_lower.endswith(".pdf"):
            text = cls._extract_pdf(file_bytes)
            items.append({
                "source_file": filename,
                "subject": f"Circular: {filename}",
                "sender": "Exam Cell",
                "body": text,
            })

        return items

    @classmethod
    def strip_html(cls, html_text: str) -> str:
        """Strip HTML tags and convert entities to plain text."""
        clean = re.sub(r"<style[\s\S]*?</style>", "", html_text, flags=re.IGNORECASE)
        clean = re.sub(r"<script[\s\S]*?</script>", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"<[^>]+>", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def _extract_docx(cls, docx_bytes: bytes) -> str:
        """Extract text from .docx bytes using python-docx or zipfile parsing."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(docx_bytes))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception:
            # Fallback: extract word/document.xml directly from docx zip
            import zipfile
            import xml.etree.ElementTree as ET
            try:
                with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
                    xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    texts = [node.text for node in tree.iter() if node.text]
                    return " ".join(texts)
            except Exception:
                return "Could not decode docx content."

    @classmethod
    def _extract_pdf(cls, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            return "\n".join([page.extract_text() or "" for page in reader.pages]).strip()
        except Exception:
            return "Could not decode PDF binary content."

    @classmethod
    def _split_multiple_notices_in_text(cls, filename: str, text: str) -> list[dict[str, Any]]:
        """If text file contains multiple notices separated by dividers, split them."""
        chunks = re.split(r"(?:\n-{3,}|\n={3,}|\n(?=Subject:|\nFrom:))", text)
        notices = []
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk or len(chunk) < 20:
                continue
            subj_match = re.search(r"Subject:\s*(.+)", chunk, re.IGNORECASE)
            subject = subj_match.group(1).strip() if subj_match else f"{filename} - Notice #{i+1}"
            notices.append({
                "source_file": filename,
                "subject": subject,
                "sender": "Academic Administration",
                "body": chunk,
            })
        if not notices:
            notices.append({
                "source_file": filename,
                "subject": filename,
                "sender": "Academic Administration",
                "body": text,
            })
        return notices


attachment_extractor = AttachmentExtractor()
