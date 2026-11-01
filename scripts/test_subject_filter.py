import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.database import SessionLocal
from backend.app.models.event import Event
from backend.app.models.note import Subject

db = SessionLocal()
confirmed = db.query(Event).filter(Event.user_id == 1, Event.status == 'CONFIRMED').all()
enrolled_subjects = db.query(Subject).filter(Subject.user_id == 1).all()

calendar_subject_names = set()
for e in confirmed:
    if e.subject:
        calendar_subject_names.add(e.subject.strip())
for s in enrolled_subjects:
    if s.name:
        calendar_subject_names.add(s.name.strip())
    if s.code:
        calendar_subject_names.add(s.code.strip())

print("Calendar/Enrolled subjects:", calendar_subject_names)

# Build matching subject keys
# Tokenize and extract key stems / abbreviations:
# e.g., 'nlp', 'cn', 'dbms', 'dl', 'mad', 'is 2', 'network', 'database', 'deep learning', 'mobile application', 'drone', 'security', 'operating systems', 'os', 'data structures'
stopwords = {'and', 'the', 'of', 'for', 'in', 'on', 'at', 'to', 'a', 'an', 'cr', 'cl', 'tr', 'lab', 'room', 'lecture', 'exam', 'class', 'batch', 'sem', 'v', 'div', 'schedule', 'change'}

subject_tokens = set()
for name in calendar_subject_names:
    tokens = re.findall(r'[a-zA-Z0-9]+', name.lower())
    for t in tokens:
        if t not in stopwords and len(t) >= 2:
            subject_tokens.add(t)

print("\nRecognized subject tokens:", sorted(list(subject_tokens)))

proposed = db.query(Event).filter(Event.user_id == 1, Event.status == 'PROPOSED').all()
print(f"\nTotal proposed events in DB: {len(proposed)}")

relevant_proposals = []
filtered_out = []

for p in proposed:
    full_text = f"{p.title} {p.subject or ''} {p.summary or ''}".lower()
    p_tokens = set(re.findall(r'[a-zA-Z0-9]+', full_text))
    
    # Check if any subject token is in proposed event text
    if any(st in p_tokens for st in subject_tokens):
        relevant_proposals.append(p)
    else:
        filtered_out.append(p)

print(f"\n=== RELEVANT TO CALENDAR: {len(relevant_proposals)} ===")
for p in relevant_proposals:
    print(f"  [+] ID {p.id}: {p.title} | Subj: {p.subject} | Date: {p.start_at}")

print(f"\n=== FILTERED OUT (Not in student's calendar): {len(filtered_out)} ===")
for p in filtered_out[:8]:
    print(f"  [-] ID {p.id}: {p.title} | Subj: {p.subject}")

db.close()
