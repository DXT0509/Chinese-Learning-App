"""Pinned review attempts and retained evidence across historical and FSRS versions."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SrsReviewAttempt(Base):
    __tablename__ = "srs_review_attempts"
    __table_args__ = (
        CheckConstraint("mode IN ('DUE','PRACTICE')", name="mode"),
        CheckConstraint("schedule_version >= 0", name="schedule_version"),
        CheckConstraint(
            "(completed_at IS NULL AND outcome IS NULL AND evidence IS NULL "
            "AND state_after IS NULL AND scheduling_applied IS NULL) OR "
            "(completed_at IS NOT NULL AND outcome IS NOT NULL AND outcome IN ('PASS','FAIL') "
            "AND evidence IS NOT NULL AND state_after IS NOT NULL "
            "AND scheduling_applied IS NOT NULL AND completed_at >= started_at)",
            name="completion",
        ),
        Index("ix_srs_review_attempts_progress_started", "user_vocabulary_id", "started_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_user_vocabulary.id", ondelete="RESTRICT")
    )
    mode: Mapped[str] = mapped_column(Text)
    schedule_version: Mapped[int] = mapped_column(Integer)
    target: Mapped[dict] = mapped_column(JSONB)
    state_before: Mapped[dict] = mapped_column(JSONB)
    state_after: Mapped[dict | None] = mapped_column(JSONB)
    evidence: Mapped[dict | None] = mapped_column(JSONB)
    outcome: Mapped[str | None] = mapped_column(Text)
    scheduling_applied: Mapped[bool | None]
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submissions: Mapped[list] = mapped_column(JSONB, server_default="[]")


class SrsTargetPolicy(Base):
    """Operator-reviewed policies, pinned by catalog checksum; never learner input."""

    __tablename__ = "srs_target_policies"
    vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_vocabulary.id"), primary_key=True
    )
    content_version: Mapped[int] = mapped_column(Integer, primary_key=True)
    checksum: Mapped[str] = mapped_column(Text, primary_key=True)
    policy: Mapped[dict] = mapped_column(JSONB)
