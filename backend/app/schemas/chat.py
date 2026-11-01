"""Chatbot and Notes Pydantic schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    subject_filter: str | None = None


class ChatSource(BaseModel):
    title: str
    chunk_index: int
    text_snippet: str
    page_number: int | None = None


class ChatResponse(BaseModel):
    answer: str
    grounded: bool
    sources: list[ChatSource] = []
    confidence: float = 0.95


class NoteUploadResponse(BaseModel):
    id: int
    title: str
    subject: str | None = None
    chunks_indexed: int
    status: str
