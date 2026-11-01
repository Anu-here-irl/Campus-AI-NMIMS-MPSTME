"""Notes Management & Upload API Endpoints for RAG Study Assistant."""

import shutil
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.note import DocumentChunk, Note, Subject
from ..models.user import User
from ..security.auth import get_current_user
from ..services.notes_indexer import notes_indexer

router = APIRouter(prefix="/notes", tags=["Study Notes & RAG"])


class NoteItemResponse(BaseModel):
    id: int
    title: str
    subject: str | None
    file_type: str
    status: str
    total_chunks: int
    created_at: str


@router.get("", response_model=list[NoteItemResponse])
def list_notes_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all indexed study notes and documents for current student."""
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    results = []
    for n in notes:
        subj_name = n.subject.name if n.subject else None
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.note_id == n.id).count()
        results.append(
            NoteItemResponse(
                id=n.id,
                title=n.title,
                subject=subj_name,
                file_type=n.file_type or "MD",
                status=n.status or "INDEXED",
                total_chunks=chunk_count,
                created_at=n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else "",
            )
        )
    return results


@router.post("/index-samples", response_model=list[NoteItemResponse])
def index_samples_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed and index built-in Semester 5 subject notes library (CN, OS, DBMS, NLP/ML)."""
    notes_indexer.index_sample_library(db, current_user.id)
    return list_notes_endpoint(db, current_user)


@router.post("/upload", response_model=NoteItemResponse)
async def upload_note_endpoint(
    title: str = Form(...),
    subject: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a new study note file (.md, .txt, .pdf, .docx), chunk it, and index for RAG Q&A."""
    save_dir = settings.STORAGE_DIR / f"user_{current_user.id}"
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    note = notes_indexer.index_document(
        db=db,
        user_id=current_user.id,
        title=title,
        file_path=file_path,
        subject_name=subject,
    )

    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.note_id == note.id).count()
    return NoteItemResponse(
        id=note.id,
        title=note.title,
        subject=subject,
        file_type=note.file_type,
        status=note.status,
        total_chunks=chunk_count,
        created_at=note.created_at.strftime("%Y-%m-%d %H:%M:%S") if note.created_at else "",
    )


@router.delete("/{note_id}")
def delete_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a note and its indexed chunks."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    db.delete(note)
    db.commit()
    return {"status": "SUCCESS", "message": f"Deleted note {note_id} and associated chunks."}
