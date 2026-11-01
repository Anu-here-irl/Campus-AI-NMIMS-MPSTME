"""Email Service managing ingestion, deduplication, persistence, and event synthesis."""

from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from ..models.email import Email, EmailPrediction, ExtractedEntity
from ..models.event import Event
from ..schemas.email import EmailIngestRequest
from .nlp_service import nlp_service


class EmailService:
    @staticmethod
    def ingest_email(
        db: Session,
        user_id: int,
        payload: EmailIngestRequest,
    ) -> tuple[Email, bool]:
        """Ingest, deduplicate, classify, and persist email with its predictions and proposals.

        Returns (email, is_duplicate).
        """
        # Deduplication check
        if payload.provider_message_id:
            existing = (
                db.query(Email)
                .filter(
                    Email.user_id == user_id,
                    Email.provider_message_id == payload.provider_message_id,
                )
                .first()
            )
            if existing:
                return existing, True

        # Run NLP Pipeline
        nlp_res = nlp_service.analyze_email(
            subject=payload.subject,
            body=payload.body,
            sender_role=payload.sender_role,
        )

        # Create Email Record
        email = Email(
            user_id=user_id,
            provider_message_id=payload.provider_message_id,
            subject=payload.subject,
            sender=payload.sender,
            sender_role=payload.sender_role or "ADMIN",
            received_at=datetime.utcnow(),
            body_text=payload.body,
            is_read=False,
        )
        db.add(email)
        db.flush()

        # Upsert Prediction Record (guard against orphaned records)
        prediction = db.query(EmailPrediction).filter(EmailPrediction.email_id == email.id).first()
        if not prediction:
            prediction = EmailPrediction(
                email_id=email.id,
                category=nlp_res["category"],
                category_confidence=nlp_res["category_confidence"],
                importance=nlp_res["importance"],
                importance_confidence=nlp_res["importance_confidence"],
                uncertain=nlp_res["uncertain"],
                model_version=nlp_res.get("model_version", "v1.0-tfidf-logreg"),
            )
            db.add(prediction)
        else:
            prediction.category = nlp_res["category"]
            prediction.category_confidence = nlp_res["category_confidence"]
            prediction.importance = nlp_res["importance"]
            prediction.importance_confidence = nlp_res["importance_confidence"]
            prediction.uncertain = nlp_res["uncertain"]
            prediction.model_version = nlp_res.get("model_version", "v1.0-tfidf-logreg")

        # Create Extracted Entities (clean existing if any)
        db.query(ExtractedEntity).filter(ExtractedEntity.email_id == email.id).delete()
        for ent in nlp_res.get("entities", []):
            entity_rec = ExtractedEntity(
                email_id=email.id,
                entity_type=ent["entity_type"],
                value=ent["value"],
                normalized_value=ent.get("normalized_value"),
                confidence=ent.get("confidence", 1.0),
            )
            db.add(entity_rec)

        # Automatically create proposed event if a change is detected
        prop = nlp_res.get("proposed_event")
        if prop:
            start_date = None
            if prop.get("new_date"):
                try:
                    start_date = datetime.strptime(prop["new_date"], "%Y-%m-%d")
                except ValueError:
                    pass
            # If no explicit future rescheduled date was found, anchor to email received_at date
            if not start_date and email.received_at:
                start_date = email.received_at

            event = Event(
                user_id=user_id,
                source_email_id=email.id,
                title=prop.get("title") or "Proposed Timetable Change",
                subject=prop.get("subject"),
                event_type=prop.get("event_type", "LECTURE"),
                start_at=start_date,
                location=prop.get("new_location"),
                status="PROPOSED",
                summary=prop.get("summary"),
            )
            db.add(event)

        db.commit()
        db.refresh(email)
        return email, False

    @staticmethod
    def list_emails(
        db: Session,
        user_id: int,
        category: str | None = None,
        importance: str | None = None,
        unread_only: bool = False,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Email]:
        """Query emails with filters."""
        query = db.query(Email).filter(Email.user_id == user_id)

        if unread_only:
            query = query.filter(Email.is_read.is_(False))

        if category or importance:
            query = query.join(EmailPrediction)
            if category:
                cat_upper = category.upper().strip()
                if "TIMETABLE" in cat_upper:
                    query = query.filter(
                        (EmailPrediction.category.ilike("%TIMETABLE%"))
                        | (EmailPrediction.category.ilike("%CLASSROOM%"))
                    )
                elif "NOTICE" in cat_upper:
                    query = query.filter(
                        EmailPrediction.category.in_(["ACADEMIC", "ADMINISTRATIVE", "GENERAL", "NOTICE", "FEES", "ATTENDANCE"])
                    )
                else:
                    query = query.filter(EmailPrediction.category.ilike(f"%{category}%"))
            if importance:
                query = query.filter(EmailPrediction.importance == importance)

        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                (Email.subject.ilike(search_fmt)) | (Email.body_text.ilike(search_fmt))
            )

        return query.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()


email_service = EmailService()
