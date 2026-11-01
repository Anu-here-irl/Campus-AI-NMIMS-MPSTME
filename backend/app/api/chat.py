"""Study assistant and note-indexing API endpoints."""

import os
from typing import Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.note import DocumentChunk, Note, Subject
from ..models.user import User
from ..schemas.chat import ChatRequest, ChatResponse, NoteUploadResponse
from ..security.auth import get_current_user
from ..services.chat_service import chat_service
from ..services.notes_indexer import notes_indexer

router = APIRouter(prefix="", tags=["Study Notes & Chatbot"])



@router.post("/chat", response_model=ChatResponse)
def chat_with_campus_ai(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask academic questions grounded in your personal study notes and campus data."""
    return chat_service.answer_query(
        db=db,
        user_id=current_user.id,
        query=payload.message,
        subject_filter=payload.subject_filter,
    )


def _format_note_item(n: Note) -> dict[str, Any]:
    content = ""
    if n.file_ref and os.path.exists(n.file_ref):
        try:
            with open(n.file_ref, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()[:5000]
        except Exception:
            pass
    elif n.chunks:
        content = "\n\n".join(c.text for c in n.chunks[:5])

    return {
        "id": n.id,
        "title": n.title,
        "subject": n.subject.name if n.subject else "General",
        "file_type": n.file_type or "MD",
        "status": n.status or "INDEXED",
        "total_chunks": len(n.chunks),
        "chunks_count": len(n.chunks),
        "created_at": n.created_at.strftime("%Y-%m-%d") if n.created_at else None,
        "content": content,
    }


@router.post("/notes/index-samples")
def index_samples_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed and index built-in Semester 5 subject notes library (CN, OS, DBMS, NLP/ML)."""
    indexed = notes_indexer.index_sample_library(db, current_user.id)
    return {
        "status": "SUCCESS",
        "notes_indexed_count": len(indexed),
        "notes": [_format_note_item(n) for n in indexed],
    }


@router.post("/notes/upload", response_model=NoteUploadResponse)
async def upload_note_file(
    title: str = Form(...),
    subject_name: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload notes (.md, .txt, .pdf, .docx) to extract passages and index them for personal Q&A."""
    save_dir = settings.STORAGE_DIR / f"user_{current_user.id}"
    save_dir.mkdir(parents=True, exist_ok=True)
    filename = file.filename or "notes.txt"
    file_path = save_dir / filename

    content_bytes = await file.read()
    with open(file_path, "wb") as f:
        f.write(content_bytes)

    note = notes_indexer.index_document(
        db=db,
        user_id=current_user.id,
        title=title,
        file_path=file_path,
        subject_name=subject_name,
    )

    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.note_id == note.id).count()
    return NoteUploadResponse(
        id=note.id,
        title=note.title,
        subject=subject_name,
        chunks_indexed=chunk_count,
        status="INDEXED",
    )


@router.get("/notes")
def list_student_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List student's uploaded personal study notes with chunk counts."""
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    return [_format_note_item(n) for n in notes]


@router.delete("/notes/{note_id}")
def delete_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a student note and its indexed chunks."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note.file_ref and os.path.exists(note.file_ref):
        try:
            os.remove(note.file_ref)
        except Exception:
            pass

    db.delete(note)
    db.commit()
    return {"status": "DELETED", "id": note_id}

