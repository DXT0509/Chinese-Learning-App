"""Additive memory, recoverable plans and idempotent active-time receipts."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SrsMemory(Base):
    __tablename__ = "srs_memory"
    user_vocabulary_id: Mapped[UUID] = mapped_column(
        ForeignKey("curated_user_vocabulary.id", ondelete="RESTRICT"), primary_key=True
    )
    scheduler_version: Mapped[str] = mapped_column(Text)
    configuration: Mapped[dict] = mapped_column(JSONB)
    card: Mapped[dict] = mapped_column(JSONB)
    adopted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SrsDailyPlan(Base):
    __tablename__ = "srs_daily_plans"
    __table_args__ = (
        CheckConstraint("target_seconds > 0", name="target_seconds"),
        Index("ix_srs_daily_plans_owner_day", "user_id", "local_day"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    local_day: Mapped[date] = mapped_column(Date)
    timezone: Mapped[str] = mapped_column(Text)
    target_seconds: Mapped[int] = mapped_column(Integer, server_default="1200")
    items: Mapped[list] = mapped_column(JSONB)
    new_items: Mapped[list] = mapped_column(JSONB, server_default="[]")
    completed: Mapped[list] = mapped_column(JSONB, server_default="[]")
    deferred: Mapped[list] = mapped_column(JSONB, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SrsActiveTime(Base):
    __tablename__ = "srs_active_time"
    __table_args__ = (CheckConstraint("active_ms >= 0", name="active_ms"),)
    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey("srs_review_attempts.id", ondelete="RESTRICT"), primary_key=True
    )
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("srs_daily_plans.id", ondelete="RESTRICT"))
    active_ms: Mapped[int] = mapped_column(Integer, server_default="0")
    daily_ms: Mapped[dict] = mapped_column(JSONB, server_default="{}")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
