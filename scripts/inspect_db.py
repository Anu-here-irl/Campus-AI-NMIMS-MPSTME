import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "campusai.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in campusai.db:")
for t in sorted(tables):
    try:
        cnt = cur.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        print(f"  {t:30s}: {cnt} rows")
    except Exception as e:
        print(f"  {t:30s}: error {e}")

# Check google calendar tokens specifically
print("\nGoogle Calendar Tokens:")
for row in cur.execute("SELECT id, user_id, scope, expires_at, is_active FROM google_calendar_tokens").fetchall():
    print(" ", row)

# Check users
print("\nUsers:")
for row in cur.execute("SELECT id, email, full_name, role FROM users").fetchall():
    print(" ", row)

# Check emails
print("\nEmails Sample (up to 5):")
for row in cur.execute("SELECT id, user_id, subject, sender, received_at FROM emails LIMIT 5").fetchall():
    print(" ", row)

# Check events
print("\nEvents Sample (up to 5):")
for row in cur.execute("SELECT id, title, start_time, room, status FROM events LIMIT 5").fetchall():
    print(" ", row)

conn.close()
