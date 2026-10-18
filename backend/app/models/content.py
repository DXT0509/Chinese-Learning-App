"""Slice 1 definitions; public content only, no execution or personal state."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.learning import CreatedAt


class Asset(CreatedAt, Base):
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("byte_length > 0", name="positive_byte_length"),
        CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="valid_sha256"),
        CheckConstraint("jsonb_typeof(metadata) = 'object'", name="metadata_object"),
        CheckConstraint(
            "storage_key ~ '^sha256/[0-9a-f]{64}\\.[a-z0-9]+$'", name="stable_storage_key"
        ),
        CheckConstraint("length(trim(media_type)) > 0", name="nonblank_media_type"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    storage_key: Mapped[str] = mapped_column(Text, unique=True)
    media_type: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    byte_length: Mapped[int] = mapped_column(BigInteger)
    asset_metadata: Mapped[dict] = mapped_column("metadata", JSONB)


class LessonTemplate(Base):
    __tablename__ = "lesson_templates"
    __table_args__ = (CheckConstraint("length(trim(code)) > 0", name="nonblank_code"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(Text, unique=True)
    description: Mapped[str] = mapped_column(Text)


class LessonTemplateVersion(CreatedAt, Base):
    __tablename__ = "lesson_template_versions"
    __table_args__ = (
        UniqueConstraint("template_id", "version"),
        CheckConstraint("version >= 1", name="positive_version"),
        CheckConstraint("status IN ('DRAFT','PUBLISHED')", name="valid_status"),
        CheckConstraint(
            "(status = 'PUBLISHED') = (published_at IS NOT NULL)", name="publication_timestamp"
        ),
        CheckConstraint("published_at >= created_at", name="publication_time_order"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_templates.id", ondelete="RESTRICT")
    )
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), server_default="DRAFT")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scenes: Mapped[list["LessonTemplateScene"]] = relationship(
        lazy="raise", order_by="LessonTemplateScene.position"
    )


class LessonTemplateScene(Base):
    __tablename__ = "lesson_template_scenes"
    __table_args__ = (
        UniqueConstraint("template_version_id", "position"),
        CheckConstraint("position >= 0", name="nonnegative_position"),
        CheckConstraint("contract_version = 1", name="supported_contract"),
        CheckConstraint(
            "scene_type IN ('VOCABULARY_INFORMATION','CHARACTER_ANALYSIS')", name="supported_type"
        ),
        CheckConstraint("jsonb_typeof(config) = 'object'", name="config_object"),
    )
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_template_versions.id", ondelete="RESTRICT"), primary_key=True
    )
    scene_key: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    position: Mapped[int] = mapped_column(Integer)
    scene_type: Mapped[str] = mapped_column(String(40))
    contract_version: Mapped[int] = mapped_column(Integer)
    required: Mapped[bool] = mapped_column(Boolean)
    config: Mapped[dict] = mapped_column(JSONB)


class LessonVersion(CreatedAt, Base):
    __tablename__ = "lesson_versions"
    __table_args__ = (
        UniqueConstraint("lesson_id", "version"),
        UniqueConstraint("id", "lesson_id", name="uq_lesson_versions_id_lesson_id"),
        CheckConstraint("version >= 1", name="positive_version"),
        CheckConstraint("status IN ('DRAFT','PUBLISHED')", name="valid_status"),
        CheckConstraint("length(trim(title)) > 0", name="nonblank_title"),
        CheckConstraint(
            "(status = 'DRAFT' AND bundle_asset_id IS NULL AND published_at IS NULL) OR "
            "(status = 'PUBLISHED' AND bundle_asset_id IS NOT NULL AND published_at IS NOT NULL)",
            name="publication_fields",
        ),
        CheckConstraint("published_at >= created_at", name="publication_time_order"),
        Index("ix_lesson_versions_lesson_status_version", "lesson_id", "status", "version"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id", ondelete="RESTRICT"))
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_template_versions.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), server_default="DRAFT")
    bundle_asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"), index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
