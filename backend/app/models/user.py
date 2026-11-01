"""User database model."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    emails = relationship("Email", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    email_connections = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan")
    notion_connection = relationship("NotionConnection", back_populates="user", uselist=False, cascade="all, delete-orphan")
    google_calendar_token = relationship("GoogleCalendarToken", back_populates="user", uselist=False, cascade="all, delete-orphan")
