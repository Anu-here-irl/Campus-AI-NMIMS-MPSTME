"""Campus AI FastAPI Application Entry Point.

Connects NLP intelligence, SQLite / PostgreSQL database,
external integrations, and the Android client API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine, SessionLocal
from .models import *  # Ensure all models are registered with Base.metadata
from .services.campus_service import campus_service

# Routers
from .api.auth import router as auth_router
from .api.emails import router as emails_router
from .api.events import router as events_router
from .api.dashboard import router as dashboard_router
from .api.campus import router as campus_router
from .api.chat import router as chat_router
from .api.notion import router as notion_router
from .api.calendar import router as calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Seed campus floor plan, room graph, and study notes library
    db = SessionLocal()
    try:
        campus_service.seed_campus_data_if_empty(db)
        from .models.note import Note
        from .services.notes_indexer import notes_indexer
        if db.query(Note).filter(Note.user_id == 1).count() == 0:
            notes_indexer.index_sample_library(db, 1)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Campus AI — Intelligent Campus Assistant API",
    description=(
        "NLP-powered backend providing email intelligence, timetable-change detection, "
        "Notion synchronization, indoor campus navigation, and personal study Q&A for Android."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(emails_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(campus_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(notion_router, prefix=settings.API_V1_STR)
app.include_router(calendar_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "nlp_model": "v1.0-tfidf-logreg",
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"}
