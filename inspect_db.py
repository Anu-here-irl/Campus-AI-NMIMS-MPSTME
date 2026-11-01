import sqlite3

conn = sqlite3.connect('campusai.db')
c = conn.cursor()

print("--- PROPOSED EVENTS FROM REAL EMAILS (61-110) ---")
for r in c.execute("SELECT e.id, e.title, e.subject, e.start_at, e.location, e.status, e.source_email_id, em.subject, em.sender FROM events e JOIN emails em ON e.source_email_id = em.id WHERE e.status='PROPOSED'").fetchall():
    print(r)
