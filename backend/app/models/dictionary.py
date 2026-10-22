"""Shared lookup data; deliberately unrelated to curriculum and user vocabulary."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DictionaryImport(Base):
    __tablename__ = "dictionary_imports"
    __table_args__ = (
        UniqueConstraint("source", "revision"),
        CheckConstraint("entry_count > 0", name="positive_entry_count"),
        CheckConstraint("length(sha256) = 64", name="sha256_length"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    revision: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str] = mapped_column(Text)
    license: Mapped[str] = mapped_column(String(100))
    license_url: Mapped[str] = mapped_column(Text)
    attribution: Mapped[str] = mapped_column(Text)
    changes: Mapped[str] = mapped_column(Text)
    entry_count: Mapped[int] = mapped_column(Integer)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    revision_correction: Mapped[dict | None] = mapped_column(JSONB)


class DictionaryEnrichmentImport(Base):
    __tablename__ = "dictionary_enrichment_imports"
    __table_args__ = (
        UniqueConstraint("source", "revision"),
        CheckConstraint("record_count > 0", name="positive_record_count"),
        CheckConstraint("length(sha256) = 64", name="sha256_length"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    revision: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str] = mapped_column(Text)
    license: Mapped[str] = mapped_column(String(100))
    license_url: Mapped[str] = mapped_column(Text)
    attribution: Mapped[str] = mapped_column(Text)
    changes: Mapped[str] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(100))
    record_count: Mapped[int] = mapped_column(Integer)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DictionaryCharacterEnrichment(Base):
    __tablename__ = "dictionary_character_enrichments"
    __table_args__ = (
        CheckConstraint("length(hanzi) = 1", name="single_hanzi"),
        CheckConstraint(
            "traditional IS NULL OR length(traditional) = 1", name="single_traditional"
        ),
        CheckConstraint(
            "length(pinyin) > 0 AND length(sino_vietnamese) > 0 AND length(vietnamese_gloss) > 0",
            name="nonempty_content",
        ),
        Index("ix_dictionary_character_enrichments_traditional", "traditional"),
    )
    source: Mapped[str] = mapped_column(String(50), primary_key=True)
    hanzi: Mapped[str] = mapped_column(String(1, collation="C"), primary_key=True)
    traditional: Mapped[str | None] = mapped_column(String(1, collation="C"))
    pinyin: Mapped[str] = mapped_column(String(100))
    sino_vietnamese: Mapped[str] = mapped_column(String(200))
    vietnamese_gloss: Mapped[str] = mapped_column(Text)
    import_id: Mapped[UUID] = mapped_column(
        ForeignKey("dictionary_enrichment_imports.id", ondelete="RESTRICT")
    )


class DictionaryEntry(Base):
    __tablename__ = "dictionary_entries"
    __table_args__ = (
        UniqueConstraint("source", "traditional", "simplified", "pinyin_numbered"),
        CheckConstraint(
            "length(simplified) > 0 AND length(traditional) > 0", name="nonempty_forms"
        ),
        CheckConstraint("jsonb_array_length(english_glosses) > 0", name="nonempty_glosses"),
        Index("ix_dictionary_entries_simplified", "simplified"),
        Index("ix_dictionary_entries_traditional", "traditional"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    import_id: Mapped[UUID] = mapped_column(
        ForeignKey("dictionary_imports.id", ondelete="RESTRICT")
    )
    simplified: Mapped[str] = mapped_column(String(255, collation="C"))
    traditional: Mapped[str] = mapped_column(String(255, collation="C"))
    pinyin_numbered: Mapped[str] = mapped_column(String(500))
    pinyin: Mapped[str] = mapped_column(String(500))
    english_glosses: Mapped[list] = mapped_column(JSONB)
    active: Mapped[bool] = mapped_column(Boolean, server_default="true")
