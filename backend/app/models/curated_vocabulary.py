"""Phase 4 catalog; legacy tables remain isolated until explicit maintenance."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CuratedBatch(Base):
    __tablename__ = "curated_vocabulary_batches"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    checksum: Mapped[str] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CuratedVocabulary(Base):
    __tablename__ = "curated_vocabulary"
    __table_args__ = (
        UniqueConstraint("simplified", "pinyin_numbered"),
        CheckConstraint("learning_level BETWEEN 0 AND 5", name="level_range"),
        CheckConstraint("content_version > 0", name="positive_version"),
        CheckConstraint("classification_standard = 'APP_CURATED'", name="classification"),
        CheckConstraint("difficulty_reference = 'HSK_2_0'", name="difficulty"),
        CheckConstraint(
            "review_status IN ('GENERATED_UNREVIEWED','NEEDS_REVIEW','AI_APPROVED',"
            "'HUMAN_APPROVED','REJECTED','LOCAL_CODEX_REVIEWED')",
            name="quality",
        ),
        Index("ix_curated_vocabulary_simplified", "simplified"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    lexical_key: Mapped[str] = mapped_column(Text, unique=True)
    simplified: Mapped[str] = mapped_column(Text)
    pinyin: Mapped[str] = mapped_column(Text)
    pinyin_numbered: Mapped[str] = mapped_column(Text)
    sino_vietnamese: Mapped[str | None] = mapped_column(Text)
    part_of_speech: Mapped[str | None] = mapped_column(Text)
    learning_level: Mapped[int] = mapped_column(Integer)
    classification_standard: Mapped[str] = mapped_column(Text, server_default="APP_CURATED")
    difficulty_reference: Mapped[str] = mapped_column(Text, server_default="HSK_2_0")
    review_status: Mapped[str] = mapped_column(Text, server_default="GENERATED_UNREVIEWED")
    content_version: Mapped[int] = mapped_column(Integer)
    batch_id: Mapped[str] = mapped_column(ForeignKey("curated_vocabulary_batches.id"))
    checksum: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class VocabularyMeaning(Base):
    __tablename__ = "vocabulary_meanings"
    __table_args__ = (
        CheckConstraint("language IN ('vi','en')", name="language"),
        CheckConstraint("length(trim(gloss)) > 0 AND position >= 0", name="usable_meaning"),
    )
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_vocabulary.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(Text, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    gloss: Mapped[str] = mapped_column(Text)


class VocabularyExample(Base):
    __tablename__ = "vocabulary_examples"
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_vocabulary.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    simplified: Mapped[str] = mapped_column(Text)
    pinyin: Mapped[str] = mapped_column(Text)
    vietnamese: Mapped[str] = mapped_column(Text)


class VocabularyRevision(Base):
    __tablename__ = "curated_vocabulary_revisions"
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_vocabulary.id", ondelete="CASCADE"), primary_key=True
    )
    content_version: Mapped[int] = mapped_column(Integer, primary_key=True)
    checksum: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VocabularyAIReview(Base):
    """Append-only operator-submitted semantic evidence, separate from learner reviews."""

    __tablename__ = "curated_vocabulary_ai_reviews"
    __table_args__ = (
        CheckConstraint("decision IN ('AI_APPROVED','NEEDS_REVIEW','REJECTED')", name="decision"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    vocabulary_id: Mapped[UUID] = mapped_column(ForeignKey("curated_vocabulary.id"))
    content_version: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(Text)
    evidence_checksum: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSONB)
    submitted_by: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class VocabularyLocalReview(Base):
    """Local operator-attested session notes, never authenticated provider evidence."""

    __tablename__ = "curated_vocabulary_local_reviews"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    vocabulary_id: Mapped[UUID] = mapped_column(ForeignKey("curated_vocabulary.id"))
    content_version: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(Text)
    evidence_checksum: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSONB)
    submitted_by: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CuratedUserVocabulary(Base):
    __tablename__ = "curated_user_vocabulary"
    __table_args__ = (
        UniqueConstraint("user_id", "vocabulary_id"),
        CheckConstraint("mastery_level BETWEEN 0 AND 5", name="mastery_range"),
        CheckConstraint(
            "(phase = 'LEARNING' AND mastery_level = 0 AND phase_step BETWEEN 0 AND 2 "
            "AND level_progress = 0) OR "
            "(phase = 'REVIEW' AND mastery_level BETWEEN 1 AND 5 AND phase_step = 0 "
            "AND level_progress BETWEEN 0 AND 1 AND (mastery_level < 5 OR level_progress = 0)) OR "
            "(phase = 'RELEARNING' AND mastery_level BETWEEN 1 AND 4 "
            "AND phase_step BETWEEN 0 AND 1 AND level_progress = 0)",
            name="srs_state",
        ),
        CheckConstraint(
            "schedule_version >= 0 AND due_review_count >= 0 AND "
            "practice_count >= 0 AND failure_count BETWEEN 0 AND due_review_count",
            name="srs_counters",
        ),
        Index("ix_curated_user_vocabulary_owner_due", "user_id", "is_active", "next_review_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_vocabulary.id", ondelete="RESTRICT")
    )
    mastery_level: Mapped[int] = mapped_column(Integer, server_default="0")
    phase: Mapped[str] = mapped_column(Text, server_default="LEARNING")
    phase_step: Mapped[int] = mapped_column(Integer, server_default="0")
    level_progress: Mapped[int] = mapped_column(Integer, server_default="0")
    schedule_version: Mapped[int] = mapped_column(Integer, server_default="0")
    due_review_count: Mapped[int] = mapped_column(Integer, server_default="0")
    practice_count: Mapped[int] = mapped_column(Integer, server_default="0")
    failure_count: Mapped[int] = mapped_column(Integer, server_default="0")
    legacy_srs_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    learning_activated: Mapped[bool] = mapped_column(Boolean, server_default="false")
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")


class VocabularyReviewSubmission(Base):
    """Reserved review history/idempotency storage; no evaluator or writer API yet."""

    __tablename__ = "curated_vocabulary_reviews"
    __table_args__ = (
        UniqueConstraint("user_vocabulary_id", "submission_key"),
        CheckConstraint("content_version > 0", name="positive_content_version"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_user_vocabulary.id", ondelete="RESTRICT")
    )
    submission_key: Mapped[UUID] = mapped_column(Uuid)
    content_version: Mapped[int] = mapped_column(Integer)
    vietnamese_prompt: Mapped[str] = mapped_column(Text)
    answer_simplified: Mapped[str] = mapped_column(Text)
    answer_pinyin: Mapped[str] = mapped_column(Text)
    result: Mapped[dict] = mapped_column(JSONB)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
