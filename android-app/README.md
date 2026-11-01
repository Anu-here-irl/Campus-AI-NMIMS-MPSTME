# Campus AI — Android Mobile Client

The **Campus AI** Android client is an academic assistant mobile application written in **Java** using modern **Android Material Components**, **Retrofit 2**, **OkHttp3**, and **Gson**.

---

## 📱 Features & Screen Overview

1. **Authentication (`LoginActivity`):**
   - Direct JWT-based authentication against FastAPI backend.
   - User registration and account switching.
   - Dynamic backend URL configurator (`http://10.0.2.2:8000` for Android Emulator, or local Wi-Fi IP for physical phones).

2. **Dashboard (`DashboardFragment`):**
   - Real-time statistics cards: Unread Notices, Pending Schedule Changes, Today's Classes.
   - Actionable schedule change proposals detected by the NLP engine.
   - High-priority urgent notices feed.
   - Quick one-tap Google Calendar synchronization.

3. **Email & Academic Notices (`EmailsFragment` & `EmailDetailActivity`):**
   - Category filter chips: **All**, **Exams**, **Assignments**, **Class Changes**, **General**.
   - Importance filter: High priority toggle.
   - Real-time notice search across subjects, senders, and content.
   - **Detailed NLP breakdown:**
     - Category confidence percentage (e.g. `EXAM (84.2%)`).
     - Priority level confidence percentage (e.g. `HIGH PRIORITY (88.1%)`).
     - Uncertainty indicator banner alerting students when model confidence is low.
     - Extracted entity chips: Dates, Locations, Course Codes, Deadlines.
     - Interactive Proposal confirmation/rejection card.

4. **Timetable & Google Calendar (`TimetableFragment`):**
   - Daily and upcoming class schedule view.
   - Google Calendar OAuth 2.0 status check (`calendar.readonly`).
   - Secure browser-based authentication flow protecting Google Cloud credentials.
   - One-tap calendar event ingestion directly into personal academic timetable.

5. **Study AI Assistant (`ChatFragment`):**
   - Retrieval-grounded question & answering over course notes and syllabus documents.
   - Transparent source citations with chunk titles and page references.

6. **Campus Navigation & Map (`CampusMapFragment`):**
   - Searchable room, laboratory, and campus facility directory.
   - Floor selector (Ground/Floor 0, Floor 1, Floor 2, Floor 3).
   - Turn-by-turn pathfinding and walking directions between any two rooms on campus.

---

## 🛠️ Building & Running in Android Studio

1. Open **Android Studio** (Electric Eel, Hedgehog, Iguana, or later).
2. Select **Open** and choose the directory:
   ```
   CAMPUS AI/android-app
   ```
3. Allow Gradle to sync dependencies automatically.
4. Select an Android Virtual Device (AVD running API 26 or higher) or connect a physical Android device via USB debugging.
5. Click **Run 'app'** (`Shift + F10`).

---

## 🌐 Connecting to FastAPI Backend

- **Android Emulator:** The host computer is accessible via `http://10.0.2.2:8000`. This is set as the default URL.
- **Physical Device:** Ensure the phone and PC are connected to the same Wi-Fi network. Find your PC's IPv4 address (e.g., `192.168.1.15`), start the FastAPI backend with:
  ```powershell
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
  and enter `http://192.168.1.15:8000` in the server URL field on the login screen.
