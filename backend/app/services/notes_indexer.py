"""Document Indexer & Semantic Chunking service for academic study notes."""

import io
import re
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from ..models.note import DocumentChunk, Note, Subject


class NotesIndexer:
    """Handles text extraction, semantic chunking, and database indexing of study notes."""

    DEFAULT_CHUNK_SIZE = 500  # characters
    DEFAULT_CHUNK_OVERLAP = 80  # characters

    @classmethod
    def extract_text_from_file(cls, file_path: Path) -> list[tuple[int, str]]:
        """Extract text chunks paired with their page numbers from file.

        Returns list of (page_number, text).
        """
        suffix = file_path.suffix.lower()

        # 1. Markdown or Text
        if suffix in (".md", ".txt", ".markdown"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            # Split roughly by chapters / headings if present
            sections = re.split(r"(?=\n##\s+)", content)
            pages = []
            for idx, sec in enumerate(sections):
                sec = sec.strip()
                if sec:
                    pages.append((idx + 1, sec))
            return pages if pages else [(1, content)]

        # 2. PDF Document
        elif suffix == ".pdf":
            pages = []
            try:
                import pypdf
                with open(file_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    for p_num, page in enumerate(reader.pages):
                        txt = page.extract_text() or ""
                        if txt.strip():
                            pages.append((p_num + 1, txt.strip()))
            except Exception:
                pass
            return pages if pages else [(1, "PDF content extraction failed or empty.")]

        # 3. Word Document (.docx)
        elif suffix == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                return [(1, full_text)]
            except Exception:
                # Fallback xml parsing
                import zipfile
                import xml.etree.ElementTree as ET
                try:
                    with zipfile.ZipFile(file_path) as z:
                        xml_content = z.read("word/document.xml")
                        tree = ET.fromstring(xml_content)
                        texts = [node.text for node in tree.iter() if node.text]
                        return [(1, " ".join(texts))]
                except Exception:
                    return [(1, "DOCX extraction failed.")]

        return [(1, "Unsupported document format.")]

    @classmethod
    def chunk_text(
        cls,
        text: str,
        page_number: int,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[dict[str, Any]]:
        """Apply sliding-window chunking to text preserving sentence boundaries when possible."""
        text = text.strip()
        if len(text) <= chunk_size:
            return [{"text": text, "page_number": page_number}]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end < len(text):
                # Look for sentence boundary near end
                boundary = text.rfind(". ", start, end)
                if boundary != -1 and boundary > start + (chunk_size // 2):
                    end = boundary + 1

            chunk_content = text[start:end].strip()
            if len(chunk_content) > 30:
                chunks.append({"text": chunk_content, "page_number": page_number})

            start = end - overlap
            if start >= len(text) - overlap:
                break

        return chunks

    @classmethod
    def index_document(
        cls,
        db: Session,
        user_id: int,
        title: str,
        file_path: Path,
        subject_name: str | None = None,
        subject_code: str | None = None,
    ) -> Note:
        """Parse, chunk, and index an academic note into SQLite."""
        # Find or create subject
        subject_id = None
        if subject_name:
            subj = (
                db.query(Subject)
                .filter(Subject.user_id == user_id, Subject.name.ilike(subject_name))
                .first()
            )
            if not subj:
                subj = Subject(user_id=user_id, name=subject_name, code=subject_code)
                db.add(subj)
                db.flush()
            subject_id = subj.id

        # Create Note record
        note = Note(
            user_id=user_id,
            subject_id=subject_id,
            title=title,
            file_ref=str(file_path),
            file_type=file_path.suffix.upper().lstrip("."),
            status="INDEXED",
        )
        db.add(note)
        db.flush()

        # Extract text pages and chunk
        pages = cls.extract_text_from_file(file_path)
        all_chunks = []
        for p_num, p_text in pages:
            chunks = cls.chunk_text(p_text, page_number=p_num)
            all_chunks.extend(chunks)

        for idx, ch in enumerate(all_chunks):
            chunk_rec = DocumentChunk(
                note_id=note.id,
                chunk_index=idx,
                text=ch["text"],
                page_number=ch["page_number"],
            )
            db.add(chunk_rec)

        db.commit()
        db.refresh(note)
        return note

    @classmethod
    def index_sample_library(cls, db: Session, user_id: int) -> list[Note]:
        # Support sample_notes located under CAMPUS AI/storage or backend/storage
        candidates = [
            Path(__file__).resolve().parents[3] / "storage" / "sample_notes",
            Path(__file__).resolve().parents[2] / "storage" / "sample_notes",
            Path(__file__).resolve().parents[1] / "storage" / "sample_notes",
        ]
        sample_dir = next((p for p in candidates if p.exists()), candidates[0])
        indexed_notes = []

        manifest = [
            ("computer_networks_notes.md", "Computer Networks", "CS-501"),
            ("operating_systems_notes.md", "Operating Systems", "CS-502"),
            ("database_management_notes.md", "Database Management Systems", "CS-503"),
            ("nlp_machine_learning_notes.md", "Natural Language Processing & ML", "CS-504"),
        ]

        for fname, subj_name, code in manifest:
            fpath = sample_dir / fname
            if not fpath.exists():
                continue

            existing = (
                db.query(Note)
                .filter(Note.user_id == user_id, Note.title == subj_name)
                .first()
            )
            if existing:
                indexed_notes.append(existing)
                continue

            note = cls.index_document(
                db=db,
                user_id=user_id,
                title=subj_name,
                file_path=fpath,
                subject_name=subj_name,
                subject_code=code,
            )
            indexed_notes.append(note)

        return indexed_notes


notes_indexer = NotesIndexer()
