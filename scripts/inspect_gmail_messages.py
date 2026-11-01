import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
import json
from backend.app.database import SessionLocal
from backend.app.services.calendar_service import calendar_service
from backend.app.services.email_ingest_service import email_ingest_service

db = SessionLocal()
token = calendar_service.get_valid_access_token(db, 1)
db.close()

headers = {"Authorization": f"Bearer {token}"}
query = "from:ANJALI.UPADHYAY43@nmims.in OR from:LAKSH.GUPTA28@nmims.in"
res = httpx.get("https://gmail.googleapis.com/gmail/v1/users/me/messages", headers=headers, params={"q": query})
messages = res.json().get("messages", [])

print(f"Total messages: {len(messages)}")

for m in messages:
    mid = m["id"]
    det = httpx.get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}", headers=headers, params={"format": "full"}).json()
    payload = det.get("payload", {})
    headers_list = payload.get("headers", [])
    hdr_dict = {h["name"].lower(): h["value"] for h in headers_list}
    
    print("\n==============================")
    print("ID:", mid)
    print("Subject:", hdr_dict.get("subject"))
    print("From:", hdr_dict.get("from"))
    print("Date:", hdr_dict.get("date"))
    print("Payload MimeType:", payload.get("mimeType"))
    
    def dump_parts(parts, indent="  "):
        for i, p in enumerate(parts):
            fn = p.get("filename", "")
            mime = p.get("mimeType", "")
            body_dict = p.get("body", {})
            size = body_dict.get("size", 0)
            has_data = "data" in body_dict
            has_att_id = "attachmentId" in body_dict
            print(f"{indent}Part {i}: mime={mime}, filename='{fn}', size={size}, has_data={has_data}, has_att_id={has_att_id}")
            if "parts" in p:
                dump_parts(p["parts"], indent + "    ")
                
    dump_parts(payload.get("parts", []))
