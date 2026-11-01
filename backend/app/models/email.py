"""Email, Prediction, and Entity database models."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class EmailConnection(Base):
    __tablename__ = "email_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), default="GMAIL")
    status = Column(String(50), default="CONNECTED")
    credential_ref = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="email_connections")


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_message_id = Column(String(255), index=True, nullable=True)
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=True)
    sender_role = Column(String(50), default="ADMIN")
    received_at = Column(DateTime, default=datetime.utcnow)
    body_text = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="emails")
    prediction = relationship("EmailPrediction", back_populates="email", uselist=False, cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="email", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="source_email", cascade="all, delete-orphan")


class EmailPrediction(Base):
    __tablename__ = "email_predictions"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    category_confidence = Column(Float, nullable=False)
    importance = Column(String(50), nullable=False)
    importance_confidence = Column(Float, nullable=False)
    uncertain = Column(Boolean, default=False)
    model_version = Column(String(50), default="v1.0-tfidf-logreg")
    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email", back_populates="prediction")


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # DATE, TIME, ROOM, SUBJECT
    value = Column(String(255), nullable=False)
    normalized_value = Column(String(255), nullable=True)
    confidence = Column(Float, default=1.0)

    email = relationship("Email", back_populates="entities")
