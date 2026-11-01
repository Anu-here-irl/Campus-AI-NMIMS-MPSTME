# Campus AI — Project Presentation & Viva Defense Guide
## Autonomous Academic Operations & Intelligent Student Study Assistant

**Course:** MBATech AI (Semester 5) — Natural Language Processing  
**Academic Year:** 2026–2027  
**Project Folder:** `CAMPUS AI`  
**Defense Format:** 15-Slide Technical Presentation + Viva Q&A Guide  

---

## Slide 1: Title & Team
- **Project Title:** Campus AI: Machine Learning & Retrieval-Augmented NLP Platform for University Campus Operations
- **Domain:** Natural Language Processing (NLP), Information Extraction, Mobile Computing, Machine Learning
- **Tech Stack:** Python 3.14, FastAPI, Scikit-Learn, SQLite, Android (Java / Material Design), Google Calendar OAuth 2.0, Notion API

---

## Slide 2: The Problem
- **Cognitive Overload:** Students receive 20–50 circulars daily across exams, fee reminders, club events, and timetable shifts.
- **Missed Lectures & Deadlines:** Room changes (e.g., *"Shifted to Room 204"*) buried in paragraphs cause missed classes and attendance debarment.
- **Fragmented Study Resources:** Study materials scattered across cloud drives and PDFs without semantic search or verified citations.
- **Indoor Spatial Navigation:** Large multi-floor university buildings lead to lost time navigating between relocated classes.

---

## Slide 3: Proposed Solution — Campus AI
1. **Automated Circular Ingestion & Classification:** Scans incoming emails, categorizes them into 12 categories, and rates urgency (High/Medium/Low).
2. **Entity Extraction & Proposal Engine:** Extracts dates, times, venues, and classroom relocation shifts; auto-generates timetable change proposals.
3. **Human-in-the-Loop Confirmation:** Students review proposed changes on their Android home screen with a single tap.
4. **Multi-Calendar Sync:** Syncs confirmed updates with Google Calendar and Notion databases, with zero-failure local SQLite fallback.
5. **RAG Study Notes Chatbot:** Answers questions grounded in Semester 5 lecture notes with strict citations (title + page number).
6. **Indoor Campus Pathfinding:** Computes turn-by-turn corridor paths and stair/elevator floor transitions between classrooms.

---

## Slide 4: System Architecture
- **Three-Tier Architecture:**
  - **Client Tier:** Android Native App (Java/XML, Retrofit 2, OkHttp).
  - **Application Gateway:** Python FastAPI backend with JWT Authentication.
  - **Data Tier:** Single-file SQLite database (`campusai.db`) enforcing privacy, simplicity, and zero cloud hosting costs.

```mermaid
flowchart LR
    Android["Android App\n(Java / XML)"] <-->|REST API / JWT| FastAPI["FastAPI Backend\n(Python)"]
    FastAPI <--> SQLite[("SQLite DB\ncampusai.db")]
    FastAPI <--> GoogleCal["Google Calendar OAuth"]
    FastAPI <--> Notion["Notion Timetable API"]
```

---

## Slide 5: NLP Classification Pipeline
- **Preprocessing:** Strip boilerplate, lowercase, alphanumeric filtering.
- **Feature Extraction:** Sublinear TF-IDF vectorizer with $N$-gram range $(1, 2)$, producing 1,500 feature dimensions.
- **Dual Logistic Regression Classifiers:**
  - Classifier 1: 12-Class Categorization (`EXAM`, `ATTENDANCE`, `CLASSROOM / TIMETABLE`, `EVENT`, etc.).
  - Classifier 2: Urgency Rating (`HIGH`, `MEDIUM`, `LOW`).
- **Uncertainty Guardrail:** Confidence scores below $0.45$ flag the email for human verification.
- **Performance:** **99.67% accuracy** on category, **100.00% accuracy** on importance, **4.17ms inference latency**.

---

## Slide 6: Information Extraction (IE) Engine
- **Regex + Boundary-Aware Context Windows:**
  - **Date Parser:** Handles day-first (`30 October 2026`, `30th Oct`) and month-first (`October 30, 2026`), normalized to ISO `YYYY-MM-DD`.
  - **Time Parser:** 12-hour AM/PM formats (`11:30 AM`, `10 AM`) normalized to `HH:MM AM/PM`.
  - **Venue Parser:** Structured regex matching `Room 204`, `Classroom 204`, `Computer Lab 2`, `Seminar Hall`, `Auditorium`.
  - **Relocation Shifts:** Detects phrases like `moved from Classroom 101 to Classroom 204` to populate `old_location` and `new_location`.

---

## Slide 7: Real Student Data Testing (Phase 4)
- **Real NMIMS University Data Deployment:**
  - Attached circulars sent by `ANJALI.UPADHYAY43@nmims.in` and `LAKSH.GUPTA28@nmims.in`.
  - Extracted and decoded **344 forwarded `.eml` circular attachments**.
  - Successfully classified **347 real notices** into SQLite:
    - 81 Exams, 75 General, 65 Events, 43 Attendance Warnings, 37 Academic, 20 Timetable Shifts, 8 Assignments, 7 Fees, 4 Registrations.
  - Extracted **441 times, 282 dates, and 171 rooms**.
  - Automatically generated **115 timetable proposals**.

---

## Slide 8: Timetable Proposals & Human-in-the-Loop
- **Why Human-in-the-Loop?** In academic environments, AI should never silently alter a student's schedule without verification.
- **Lifecycle:**
  - Email Ingested $\to$ Relocation Detected $\to$ Proposal Created (`status="PROPOSED"`).
  - Student notified on Android Dashboard.
  - Student confirms with one tap $\to$ Status becomes `CONFIRMED`.
  - Schedule is updated in SQLite, Google Calendar, and Notion.

---

## Slide 9: Google Calendar & Notion Integration
- **Google Cloud OAuth 2.0 Web Application Client:**
  - Client ID configured with redirect URI: `http://localhost:8000/api/v1/calendar/callback`.
  - Scopes: `calendar.readonly` and `gmail.readonly`.
  - Token refresh and CSRF validation handled securely on backend.
- **Notion Timetable Synchronization:**
  - `POST /api/v1/notion/sync` synchronizes confirmed timetable events to Notion pages.
  - If no Notion account is configured, the system uses a **Zero-Failure Local Fallback** (`FALLBACK_LOCAL`), keeping student data intact in SQLite.

---

## Slide 10: RAG Study Assistant & Notes Indexer
- **Semester 5 Curriculum Library:**
  - Computer Networks (CS-501)
  - Operating Systems (CS-502)
  - Database Management Systems (CS-503)
  - Natural Language Processing & Machine Learning (CS-504)
- **Sliding-Window Chunking:** ~450 characters per chunk with 60-character boundary overlap, preserving source page numbers.
- **Custom Uploads:** Students can upload their own notes (`.md`, `.txt`, `.pdf`, `.docx`) via mobile or REST API.

---

## Slide 11: Hybrid Retrieval & Hallucination Guardrails
- **Hybrid Retrieval Formula:**
  $$\text{Score} = 0.70 \times \text{TF-IDF Cosine Similarity} + 0.30 \times \text{Stopword-Filtered Lexical Overlap}$$
- **Relevance Thresholding:** $\text{Score} \ge 0.15$ required for grounded context assembly.
- **Zero Hallucination Guarantee:** Out-of-domain nonsense is rejected explicitly (`grounded=False`, `confidence=0.20`).
- **Campus FAQ Fallback:** Practical inquiries (library hours, lab locations, attendance rules) are answered instantly from the handbook.

---

## Slide 12: Indoor Campus Navigation Engine
- **Multi-Floor Building Model:**
  - 4 Floors: Ground Floor (0), First Floor (1), Second Floor (2), Third Floor (3).
  - 15 facilities mapped with normalized coordinates.
- **Hierarchical Pathfinding:**
  - Same Floor: Horizontal corridor walking with wing direction guidance (East Wing vs West Wing).
  - Cross-Floor: Calculates vertical distance via Central Stairs / Elevator ($|\Delta \text{floor}| \times 15\text{m}$) and generates directional steps (e.g. *"Ascend 2 floors to 2nd Floor"*).
  - Waypoints: Returns coordinates for rendering path lines on the mobile canvas.

---

## Slide 13: Android Mobile Client Implementation
- **Native Android App (Java & Material Design):**
  - `DashboardFragment`: Unread count, high-priority notices, upcoming classes, quick actions.
  - `EmailsFragment`: Searchable, category-filtered list with colored importance tags.
  - `TimetableFragment`: Upcoming classes and interactive proposal review cards (Confirm / Reject).
  - `ChatFragment`: RAG study notes chat with confidence score and document citations.
  - `CampusMapFragment`: Floor selector chips, room search, and turn-by-turn route directions.

---

## Slide 14: Comprehensive Test & Benchmark Results
- **100% Automated Test Pass Rate Across 51 Tests:**
  - `test_nlp.py`: 16/16 Passed (Classification, NER, evaluation).
  - `test_api_backend.py`: 8/8 Passed (Auth, Ingest, Classify, Proposals, Confirm, Dashboard).
  - `test_api_calendar.py`: 7/7 Passed (OAuth flow, CSRF, Calendar event ingestion).
  - `test_api_campus.py`: 8/8 Passed (Floors, Rooms, Search, Same-Floor, Inter-Floor, 404s).
  - `test_api_chat.py`: 7/7 Passed (RAG indexing, retrieval, citations, guardrails, custom uploads).
  - `test_api_notion.py`: 4/4 Passed (Notion sync and local fallback).
  - `test_e2e_integration.py`: 1/1 Passed (Full student journey end-to-end).
- **Execution Speed:** Complete regression suite executes in under **6 seconds**.

---

## Slide 15: Conclusion & Future Scope
- **Conclusion:** Campus AI delivers a complete, production-tested, low-latency university operations assistant that eliminates notice blindness, automates schedule management, grounds study Q&A, and navigates campus buildings.
- **Future Enhancements:**
  1. On-device mobile NLP inference using TensorFlow Lite.
  2. BLE Bluetooth beacon integration for sub-meter real-time indoor positioning.
  3. Voice assistant interface with Whisper speech-to-text.

---

## Viva Defense Q&A Guide (Anticipated Faculty Questions)

### Q1: Why use TF-IDF and Logistic Regression instead of a heavy transformer like BERT?
**Answer:** Academic circulars have concise, predictable lexicons. TF-IDF with Logistic Regression achieves **99.67% accuracy** while running inference in **4.17 milliseconds** on commodity CPU hardware without GPU requirements or cloud inference fees. This guarantees sub-second responsiveness on student devices.

### Q2: How does Campus AI prevent hallucination in the study chatbot?
**Answer:** We enforce a three-layer guardrail: (1) Hybrid scoring requiring $\text{Score} \ge 0.15$, (2) Stopword filtering to prevent spurious single-word overlap, and (3) Explicit out-of-domain rejection where the system states information was not found rather than fabricating facts. Every grounded answer includes the source document title and original page number.

### Q3: Why is human confirmation required for timetable changes?
**Answer:** Silent calendar overwrites can cause severe academic consequences (e.g., missing an exam because an email was slightly misread). By adopting a Human-in-the-Loop paradigm (`status="PROPOSED"` $\to$ Student reviews $\to$ `CONFIRMED`), the student maintains 100% control over their schedule.

### Q4: Why use SQLite instead of PostgreSQL or MySQL?
**Answer:** SQLite is serverless, zero-configuration, ACID-compliant, and self-contained in a single portable file (`campusai.db`). It eliminates database server crashes, network latency, and infrastructure maintenance costs, perfectly aligning with single-institution or personal student deployment.
