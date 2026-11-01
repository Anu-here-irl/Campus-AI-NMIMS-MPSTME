"""Event and Timetable Proposal database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_email_id = Column(Integer, ForeignKey("emails.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    event_type = Column(String(50), default="LECTURE")  # EXAM, LECTURE, DEADLINE, EVENT
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), default="PROPOSED")  # PROPOSED, CONFIRMED, REJECTED
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="events")
    source_email = relationship("Email", back_populates="events")
    notion_sync_record = relationship("NotionSyncRecord", back_populates="event", uselist=False, cascade="all, delete-orphan")
