"""Notion integration database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class NotionConnection(Base):
    __tablename__ = "notion_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    database_id = Column(String(255), nullable=True)
    token_ref = Column(String(500), nullable=True)
    status = Column(String(50), default="CONNECTED")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notion_connection")


class NotionSyncRecord(Base):
    __tablename__ = "notion_sync_records"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), unique=True, nullable=False)
    notion_page_id = Column(String(255), nullable=True)
    sync_status = Column(String(50), default="PENDING")  # PENDING, SYNCED, FAILED
    last_synced_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="notion_sync_record")
