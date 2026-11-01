import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "..", "campusai.db")
c = sqlite3.connect(db_path)
print('=== Status counts in events ===')
for r in c.execute('SELECT status, COUNT(*) FROM events GROUP BY status'):
    print(' ', r)

print('\n=== Confirmed (Timetable / Calendar) Events ===')
for r in c.execute("SELECT id, title, subject, start_at, location, source_email_id FROM events WHERE status='CONFIRMED'"):
    print(' ', r)

print('\n=== Proposed Events ===')
for r in c.execute("SELECT id, title, subject, start_at, location, source_email_id FROM events WHERE status='PROPOSED' LIMIT 20"):
    print(' ', r)

c.close()
