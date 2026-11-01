"""Study Assistant & Retrieval-Augmented Generation (RAG) Chatbot Service.

Provides hybrid retrieval (TF-IDF vector cosine similarity + lexical matching)
over indexed student course notes, timetable & campus knowledge querying,
interactive conversational synthesis, transparent citations, and optional LLM integration.
"""

import os
import re
from datetime import datetime
from typing import Any
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from ..config import settings
from ..models.event import Event
from ..models.note import DocumentChunk, Note, Subject


class ChatService:
    """Conversational study chatbot supporting hybrid RAG, timetable lookup, and campus guidance."""

    SIMILARITY_THRESHOLD = 0.12  # Minimum relevance score to consider a chunk grounded

    @classmethod
    def answer_query(
        cls,
        db: Session,
        user_id: int,
        query: str,
        subject_filter: str | None = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Answer queries grounded in the student's personal notes, calendar timetable, and campus knowledge."""
        query_clean = query.strip()
        if not query_clean:
            return {
                "answer": "Hello! I am Campus AI. Ask me anything about your course notes, timetable, exam schedule, or campus locations.",
                "grounded": False,
                "sources": [],
                "confidence": 0.0,
            }

        query_lower = query_clean.lower()

        # -------------------------------------------------------------
        # 1. Check for Friendly Greetings & Conversational Questions
        # -------------------------------------------------------------
        greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "who are you", "what can you do"}
        if query_lower in greetings or any(query_lower.startswith(g + " ") for g in greetings):
            return {
                "answer": (
                    "Hello! I am **Campus AI**, your academic study assistant and campus guide.\n\n"
                    "I can help you with:\n"
                    "- **Course Q&A & Notes**: Clarifying concepts, summarizing lecture notes, or preparing for exams.\n"
                    "- **Schedule & Timetable**: Checking your upcoming classes, labs, and exam dates.\n"
                    "- **Campus Navigation**: Locating classrooms, research labs, libraries, and amenities across all floors.\n\n"
                    "What would you like to explore or review today?"
                ),
                "grounded": True,
                "sources": [{"title": "Campus AI Assistant", "chunk_index": 0, "page_number": 1, "text_snippet": "Interactive student assistant"}],
                "confidence": 0.95,
            }

        # -------------------------------------------------------------
        # 2. Check for Schedule, Timetable, or Upcoming Class Queries
        # -------------------------------------------------------------
        schedule_keywords = ["when is", "schedule", "timetable", "next class", "upcoming class", "exam date", "classes today", "lecture today"]
        if any(sk in query_lower for sk in schedule_keywords):
            schedule_response = cls._lookup_student_schedule(db, user_id, query_lower)
            if schedule_response:
                return schedule_response

        # -------------------------------------------------------------
        # 3. Check for Room / Facility / Campus Location Queries
        # -------------------------------------------------------------
        location_keywords = ["where is", "how to reach", "location of", "find room", "room ", "lab ", "auditorium", "library", "canteen", "cafeteria"]
        if any(lk in query_lower for lk in location_keywords):
            location_response = cls._lookup_campus_location(query_lower)
            if location_response:
                return location_response

        # -------------------------------------------------------------
        # 4. Hybrid Retrieval over Student's Course Notes (RAG)
        # -------------------------------------------------------------
        chunks_query = (
            db.query(DocumentChunk)
            .join(Note)
            .filter(Note.user_id == user_id)
        )

        if subject_filter:
            chunks_query = (
                chunks_query.outerjoin(Subject)
                .filter(
                    (Subject.name.ilike(f"%{subject_filter}%"))
                    | (Note.title.ilike(f"%{subject_filter}%"))
                )
            )

        candidate_chunks = chunks_query.all()
        matched_chunks = []

        if candidate_chunks:
            chunk_texts = [c.text for c in candidate_chunks]
            try:
                vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    stop_words="english",
                    sublinear_tf=True,
                )
                tfidf_matrix = vectorizer.fit_transform(chunk_texts)
                query_vec = vectorizer.transform([query_clean])
                cosine_sims = cosine_similarity(query_vec, tfidf_matrix).flatten()

                STOP_WORDS = {
                    "what", "when", "where", "which", "how", "why", "who", "whom",
                    "is", "are", "am", "was", "were", "be", "been", "being",
                    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                    "of", "with", "by", "from", "up", "about", "into", "over", "after",
                    "can", "could", "would", "should", "do", "does", "did", "have", "has", "had",
                    "explain", "describe", "tell", "give", "me", "please", "located", "location",
                    "find", "show"
                }
                query_tokens = set(re.findall(r"\w+", query_lower)) - STOP_WORDS

                for idx, chunk in enumerate(candidate_chunks):
                    cos_score = float(cosine_sims[idx])
                    chunk_lower = chunk.text.lower()
                    lex_matches = sum(1 for tok in query_tokens if tok in chunk_lower)
                    lex_score = (lex_matches / max(len(query_tokens), 1)) if query_tokens else 0.0

                    if cos_score > 0.0 or (query_tokens and lex_matches == len(query_tokens)):
                        hybrid_score = (0.70 * cos_score) + (0.30 * lex_score)
                    else:
                        hybrid_score = 0.0

                    if hybrid_score > 0.04:
                        matched_chunks.append((hybrid_score, chunk))

                matched_chunks.sort(key=lambda x: x[0], reverse=True)
            except Exception:
                pass

        # -------------------------------------------------------------
        # 5. Grounded Response from Top Matched Study Notes
        # -------------------------------------------------------------
        if matched_chunks and matched_chunks[0][0] >= cls.SIMILARITY_THRESHOLD:
            top_results = matched_chunks[:top_k]
            sources = []
            context_blocks = []

            for score, chunk in top_results:
                note_title = chunk.note.title if chunk.note else "Course Notes"
                sources.append({
                    "title": note_title,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number or 1,
                    "text_snippet": chunk.text[:220] + ("..." if len(chunk.text) > 220 else ""),
                })
                context_blocks.append(f"[{note_title} - Page {chunk.page_number or 1}]\n{chunk.text}")

            context_str = "\n\n".join(context_blocks)

            # Try fast LLM generation if available
            llm_answer = cls._try_gemini_synthesis(query_clean, context_str)
            if llm_answer:
                answer = llm_answer
            else:
                best_score, best_chunk = top_results[0]
                note_title = best_chunk.note.title if best_chunk.note else "Course Notes"
                answer = (
                    f"**From '{note_title}' (Page {best_chunk.page_number or 1}):**\n\n"
                    f"{best_chunk.text}\n\n"
                    f"💬 *Would you like me to dive deeper into any specific aspect of this, or give you a practice question to test your understanding?*"
                )

            top_conf = min(0.96, 0.70 + (top_results[0][0] * 0.35))
            return {
                "answer": answer,
                "grounded": True,
                "sources": sources,
                "confidence": round(top_conf, 2),
            }

        # -------------------------------------------------------------
        # 6. Fallback Campus Handbook
        # -------------------------------------------------------------
        campus_faqs = {
            "library": "The Central Library is located on the Ground Floor (Room 002), open from 8:30 AM to 8:00 PM on weekdays. Digital repository access remains 24/7.",
            "attendance": "A minimum of 75% attendance is strictly required in each subject as per college academic regulations to avoid debarment.",
            "auditorium": "The Main Auditorium is situated on the Ground Floor (Room 001) near the main campus entrance.",
            "canteen": "The student cafeteria and food court are located on the Lower Ground Floor (LG) with indoor and terrace seating.",
            "cafeteria": "The student cafeteria and food court are located on the Lower Ground Floor (LG) with indoor and terrace seating.",
        }
        for k, v in campus_faqs.items():
            if k in query_lower:
                return {
                    "answer": f"**Campus AI Handbook:** {v}\n\nWould you like directions on the campus map or info on any other facility?",
                    "grounded": True,
                    "sources": [{"title": "Campus AI Handbook", "chunk_index": 0, "page_number": 1, "text_snippet": v}],
                    "confidence": 0.90,
                }

        # -------------------------------------------------------------
        # 7. Hallucination Guardrail / Educational Clarification
        # -------------------------------------------------------------
        return {
            "answer": (
                "I could not find specific notes or schedule entries for that in your indexed study materials.\n\n"
                "As your Campus AI assistant, I can help you with:\n"
                "• Your uploaded course notes (Computer Networks, DBMS, NLP, OS, etc.)\n"
                "• Your timetable, next classes, and upcoming exams\n"
                "• Room locations and facilities across all campus floors\n\n"
                "Could you please rephrase your question, or mention the specific subject you want to review?"
            ),
            "grounded": False,
            "sources": [],
            "confidence": 0.20,
        }

    @classmethod
    def _lookup_student_schedule(cls, db: Session, user_id: int, query_lower: str) -> dict[str, Any] | None:
        """Query user's confirmed timetable events for classes and exam queries."""
        events = (
            db.query(Event)
            .filter(Event.user_id == user_id, Event.status == "CONFIRMED")
            .order_by(Event.start_at.asc())
            .all()
        )
        if not events:
            return None

        # Check for matching subject in query
        matched_event = None
        for ev in events:
            ev_text = f"{ev.title or ''} {ev.subject or ''}".lower()
            tokens = [t for t in re.findall(r"\w+", ev_text) if len(t) >= 3 and t not in {"cr", "cl", "tr", "lecture", "exam"}]
            if any(t in query_lower for t in tokens):
                matched_event = ev
                break

        # If specific event matched
        if matched_event:
            time_str = matched_event.start_at.strftime("%A, %d %b %Y at %I:%M %p") if matched_event.start_at else "Scheduled on your timetable"
            loc_str = matched_event.location or "Room 204"
            ans = (
                f"**[Schedule] {matched_event.title}** ({matched_event.subject or 'Core Course'})\n\n"
                f"- **Date & Time**: {time_str}\n"
                f"- **Location**: {loc_str}\n"
                f"- **Status**: Confirmed in your academic calendar\n\n"
                f"Would you like me to pull up study notes or practice questions for {matched_event.subject or matched_event.title}?"
            )
            return {
                "answer": ans,
                "grounded": True,
                "sources": [{"title": "Academic Calendar & Timetable", "chunk_index": 0, "page_number": 1, "text_snippet": f"{matched_event.title} at {loc_str}"}],
                "confidence": 0.94,
            }

        # Otherwise show upcoming classes
        if any(k in query_lower for k in ["next class", "upcoming", "classes today", "schedule today", "timetable"]):
            upcoming = events[:4]
            lines = ["Here are your upcoming confirmed classes:\n"]
            for ev in upcoming:
                t_str = ev.start_at.strftime("%I:%M %p") if ev.start_at else "Scheduled"
                lines.append(f"- **{ev.title}** ({ev.location or 'Room 204'}) — {t_str}")
            lines.append("\nWould you like details on any specific subject's syllabus or study notes?")
            return {
                "answer": "\n".join(lines),
                "grounded": True,
                "sources": [{"title": "Academic Calendar & Timetable", "chunk_index": 0, "page_number": 1, "text_snippet": "Synchronized personal schedule"}],
                "confidence": 0.92,
            }

        return None

    @classmethod
    def _lookup_campus_location(cls, query_lower: str) -> dict[str, Any] | None:
        """Find room details from the campus floor directory."""
        # Common room codes and names
        campus_directory = [
            ("library", "Central Library", "Ground Floor (Room 002)", "Main college library with reading halls and 24/7 digital repository."),
            ("auditorium", "Main Auditorium", "Ground Floor (Room 001)", "Large acoustic auditorium with main stage for symposiums and conferences."),
            ("cafeteria", "Central Cafeteria", "Lower Ground Floor (LG)", "Main dining hall and student cafeteria with hot meals and snacks."),
            ("canteen", "Central Cafeteria", "Lower Ground Floor (LG)", "Main dining hall and student cafeteria with hot meals and snacks."),
            ("dean", "Dean's Office Area", "Floor 1 (East Wing, Room 120)", "Executive chambers and academic dean's administration secretariat."),
            ("e-yantra", "e-Yantra Robotics Lab", "Ground Floor (Room G12)", "IIT Bombay verified advanced robotics and automation research laboratory."),
            ("robotics", "e-Yantra Robotics Lab", "Ground Floor (Room G12)", "IIT Bombay verified advanced robotics and automation research laboratory."),
            ("204", "Classroom 204 (E CR 204)", "Floor 2 (West Wing)", "Lecture hall equipped with dual HD projection and audio system."),
            ("205", "Classroom 205 (E CR 205)", "Floor 2 (Central Wing)", "Lecture room facing central corridor."),
            ("201", "Classroom 201 (E CR 201)", "Floor 2 (West Wing)", "Smart lecture hall with interactive display."),
            ("101", "Classroom 101 (E CR 101)", "Floor 1 (West Wing)", "First floor lecture hall."),
            ("102", "Classroom 102 (E CR 102)", "Floor 1 (West Wing)", "First floor lecture hall."),
            ("cl 101", "Computer Lab 101", "Floor 1 (East Wing)", "High-performance computing and programming lab."),
            ("cl 102", "Computer Lab 102", "Floor 1 (East Wing)", "AI, database, and cloud computing laboratory."),
            ("hardware lab", "Hardware & Microprocessor Lab", "Floor 1 (Central Wing)", "Embedded systems, IoT, and digital circuitry laboratory."),
        ]

        for trigger, name, location, desc in campus_directory:
            if trigger in query_lower:
                ans = (
                    f"**[Location] {name}**\n\n"
                    f"- **Location**: {location}\n"
                    f"- **Description**: {desc}\n\n"
                    f"Would you like to view this room on the Campus Map, or get step-by-step directions from the main entrance?"
                )
                return {
                    "answer": ans,
                    "grounded": True,
                    "sources": [{"title": "Campus AI Handbook", "chunk_index": 0, "page_number": 1, "text_snippet": f"{name} is located at {location}"}],
                    "confidence": 0.95,
                }

        return None

    _gemini_online: bool | None = None

    @classmethod
    def _try_gemini_synthesis(cls, query: str, context: str) -> str | None:
        """Synthesize a natural language answer using Google Gemini API with fast failure caching."""
        if cls._gemini_online is False:
            return None

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            cls._gemini_online = False
            return None
        api_key = api_key.strip()

        prompt = (
            f"You are Campus AI, an intelligent, articulate academic study assistant for engineering students.\n"
            f"Answer the student's question accurately, concisely, and strictly based on the provided course notes.\n"
            f"Format your answer with clear bullet points where helpful and cite the note title.\n"
            f"End your answer with a brief, helpful follow-up question asking how you can assist further.\n\n"
            f"Course Notes Context:\n{context}\n\n"
            f"Student Question: {query}\n\n"
            f"Answer:"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 450},
        }

        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    cls._gemini_online = True
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    cls._gemini_online = False
        except Exception:
            cls._gemini_online = False

        return None


chat_service = ChatService()
