from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CreatedAt:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(CreatedAt, Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Lesson(CreatedAt, Base):
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("lesson_order >= 0", name="nonnegative_order"),
        CheckConstraint(
            "lesson_type IN ('VOCABULARY','PRONUNCIATION','GRAMMAR','TOPIC','REVIEW')",
            name="valid_type",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    lesson_type: Mapped[str] = mapped_column(String(40))
    lesson_order: Mapped[int] = mapped_column(Integer, unique=True)
    code: Mapped[str | None] = mapped_column(Text, unique=True)


class Character(CreatedAt, Base):
    __tablename__ = "characters"
    __table_args__ = (
        CheckConstraint("stroke_count >= 0", name="nonnegative_strokes"),
        CheckConstraint("revision >= 1", name="positive_revision"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    hanzi: Mapped[str] = mapped_column(String(8), unique=True)
    radical_info: Mapped[str | None] = mapped_column(Text)
    stroke_count: Mapped[int | None] = mapped_column(Integer)
    stroke_order_asset: Mapped[str | None] = mapped_column(Text)
    stroke_order_asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"), index=True
    )
    revision: Mapped[int] = mapped_column(Integer, server_default="1")


class Vocabulary(CreatedAt, Base):
    __tablename__ = "vocabulary"
    __table_args__ = (
        UniqueConstraint("simplified", "pinyin", "vietnamese_meaning"),
        CheckConstraint("revision >= 1", name="positive_revision"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    simplified: Mapped[str] = mapped_column(String(255))
    pinyin: Mapped[str] = mapped_column(String(500))
    sino_vietnamese: Mapped[str | None] = mapped_column(String(500))
    vietnamese_meaning: Mapped[str] = mapped_column(String(1000))
    notes: Mapped[str | None] = mapped_column(Text)
    audio_reference: Mapped[str | None] = mapped_column(Text)
    audio_asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"), index=True
    )
    part_of_speech: Mapped[str | None] = mapped_column(Text)
    revision: Mapped[int] = mapped_column(Integer, server_default="1")


class VocabularyCharacter(Base):
    __tablename__ = "vocabulary_characters"
    __table_args__ = (CheckConstraint("position >= 0", name="nonnegative_position"),)
    # Position belongs in the PK: repeated characters in one word are valid.
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("vocabulary.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id"), index=True)


class LessonVocabulary(Base):
    __tablename__ = "lesson_vocabulary"
    __table_args__ = (
        UniqueConstraint("lesson_version_id", "vocabulary_id"),
        UniqueConstraint(
            "lesson_version_id", "position", name="uq_lesson_vocabulary_version_position"
        ),
        ForeignKeyConstraint(
            ["lesson_version_id", "lesson_id"],
            ["lesson_versions.id", "lesson_versions.lesson_id"],
            ondelete="RESTRICT",
        ),
        Index(
            "uq_lesson_vocabulary_legacy_target",
            "lesson_id",
            "vocabulary_id",
            unique=True,
            postgresql_where=text("lesson_version_id IS NULL"),
        ),
        Index(
            "uq_lesson_vocabulary_legacy_position",
            "lesson_id",
            "position",
            unique=True,
            postgresql_where=text("lesson_version_id IS NULL"),
        ),
        CheckConstraint(
            "(lesson_version_id IS NULL AND role IS NULL) OR "
            "(lesson_version_id IS NOT NULL AND role IS NOT NULL "
            "AND role IN ('TEACHES','CONTEXT','REVIEWS'))",
            name="version_role",
        ),
        CheckConstraint("position >= 0", name="nonnegative_position"),
    )
    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    vocabulary_id: Mapped[UUID] = mapped_column(ForeignKey("vocabulary.id"), index=True)
    lesson_version_id: Mapped[UUID | None] = mapped_column(Uuid)
    role: Mapped[str | None] = mapped_column(String(20))
    position: Mapped[int] = mapped_column(Integer)


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed')", name="valid_status"
        ),
        CheckConstraint(
            "(status = 'completed') = (completed_at IS NOT NULL)", name="completion_timestamp"
        ),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(30), server_default="not_started")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserVocabulary(Base):
    __tablename__ = "user_vocabulary"
    __table_args__ = (
        UniqueConstraint("user_id", "vocabulary_id"),
        CheckConstraint("source IN ('catalog', 'custom')", name="valid_source"),
        CheckConstraint(
            "(source = 'catalog' AND vocabulary_id IS NOT NULL "
            "AND custom_simplified IS NULL AND custom_pinyin IS NULL AND custom_meaning IS NULL) "
            "OR (source = 'custom' AND vocabulary_id IS NULL "
            "AND length(trim(custom_simplified)) > 0 AND custom_simplified IS NOT NULL "
            "AND length(trim(custom_meaning)) > 0 AND custom_meaning IS NOT NULL)",
            name="source_fields",
        ),
        Index("ix_user_vocabulary_user_id", "user_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    vocabulary_id: Mapped[UUID | None] = mapped_column(ForeignKey("vocabulary.id"))
    source: Mapped[str] = mapped_column(String(20))
    custom_simplified: Mapped[str | None] = mapped_column(String(255))
    custom_pinyin: Mapped[str | None] = mapped_column(String(500))
    custom_meaning: Mapped[str | None] = mapped_column(Text)
    learned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SrsState(Base):
    __tablename__ = "srs_states"
    __table_args__ = (
        CheckConstraint("review_count >= 0", name="nonnegative_reviews"),
        Index("ix_srs_states_due_at", "due_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_vocabulary.id", ondelete="CASCADE"), unique=True
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_count: Mapped[int] = mapped_column(Integer, server_default="0")
    algorithm_version: Mapped[str] = mapped_column(String(40))
    algorithm_state: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
