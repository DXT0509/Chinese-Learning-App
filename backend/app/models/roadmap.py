"""Executable ordering around existing lesson versions; preview runs remain separate."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.learning import CreatedAt


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    active_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("roadmap_versions.id", use_alter=True, name="fk_roadmap_active_version")
    )


class RoadmapVersion(CreatedAt, Base):
    __tablename__ = "roadmap_versions"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "version"),
        CheckConstraint("version > 0", name="positive_version"),
        CheckConstraint("status IN ('DRAFT','PUBLISHED')", name="status"),
        CheckConstraint("(status = 'PUBLISHED') = (published_at IS NOT NULL)", name="published"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    roadmap_id: Mapped[UUID] = mapped_column(ForeignKey("roadmaps.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default="DRAFT")
    definition: Mapped[dict] = mapped_column(JSONB)
    bundle_asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("assets.id"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RoadmapNode(Base):
    __tablename__ = "roadmap_node_identities"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    roadmap_id: Mapped[UUID] = mapped_column(ForeignKey("roadmaps.id"))
    node_type: Mapped[str] = mapped_column(Text)
    vocabulary_id: Mapped[UUID | None] = mapped_column(ForeignKey("curated_vocabulary.id"))
    __table_args__ = (
        CheckConstraint("node_type IN ('NEW_WORD','REVIEW')", name="type"),
        CheckConstraint("(node_type = 'NEW_WORD') = (vocabulary_id IS NOT NULL)", name="one_word"),
    )


class RoadmapNodeVersion(Base):
    __tablename__ = "roadmap_nodes"
    __table_args__ = (
        UniqueConstraint("roadmap_version_id", "node_id", name="uq_roadmap_nodes_identity"),
        UniqueConstraint("roadmap_version_id", "position", name="uq_roadmap_nodes_position"),
        CheckConstraint("position >= 0", name="position"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    roadmap_version_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_versions.id"))
    node_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_node_identities.id"))
    position: Mapped[int] = mapped_column(Integer)
    lesson_version_id: Mapped[UUID] = mapped_column(ForeignKey("lesson_versions.id"))


class RoadmapVocabulary(Base):
    __tablename__ = "roadmap_vocabulary"
    __table_args__ = (
        ForeignKeyConstraint(
            ["vocabulary_id", "content_version"],
            [
                "curated_vocabulary_revisions.vocabulary_id",
                "curated_vocabulary_revisions.content_version",
            ],
        ),
    )
    node_version_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_nodes.id"), primary_key=True)
    vocabulary_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    content_version: Mapped[int] = mapped_column(Integer)


class NodeProgress(Base):
    __tablename__ = "roadmap_progress"
    __table_args__ = (
        CheckConstraint(
            "status IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','SKIPPED')", name="status"
        ),
        CheckConstraint("(status = 'COMPLETED') = (completed_at IS NOT NULL)", name="completion"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    node_id: Mapped[UUID] = mapped_column(
        ForeignKey("roadmap_node_identities.id"), primary_key=True
    )
    status: Mapped[str] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_completed_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("roadmap_nodes.id"))


class NodeRun(CreatedAt, Base):
    __tablename__ = "roadmap_runs"
    __table_args__ = (
        Index(
            "uq_roadmap_runs_first",
            "user_id",
            "node_version_id",
            unique=True,
            postgresql_where=text("NOT replay"),
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    node_version_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_nodes.id"))
    # A durable practice run after first completion; never changes the completion record.
    replay: Mapped[bool] = mapped_column(Boolean)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ActivityReceipt(CreatedAt, Base):
    __tablename__ = "roadmap_activity_receipts"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_runs.id"), primary_key=True)
    request_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    activity_id: Mapped[UUID] = mapped_column(Uuid)
    evidence: Mapped[dict] = mapped_column(JSONB)
    accepted: Mapped[bool] = mapped_column(Boolean)
    evaluator: Mapped[str] = mapped_column(Text)


class ExpGrant(CreatedAt, Base):
    __tablename__ = "roadmap_exp_grants"
    __table_args__ = (CheckConstraint("amount >= 0", name="amount"),)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    node_id: Mapped[UUID] = mapped_column(
        ForeignKey("roadmap_node_identities.id"), primary_key=True
    )
    node_version_id: Mapped[UUID] = mapped_column(ForeignKey("roadmap_nodes.id"))
    amount: Mapped[int] = mapped_column(Integer)
