"""Additive identity and preview run persistence; legacy ownership is unchanged."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.learning import CreatedAt


class PasswordCredential(CreatedAt, Base):
    __tablename__ = "password_credentials"
    __table_args__ = (CheckConstraint("email = lower(trim(email))", name="normalized_email"),)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)


class AuthSession(CreatedAt, Base):
    __tablename__ = "auth_sessions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    access_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshCredential(Base):
    __tablename__ = "refresh_credentials"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("auth_sessions.id", ondelete="CASCADE"), index=True
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class LessonRun(CreatedAt, Base):
    __tablename__ = "lesson_runs"
    __table_args__ = (UniqueConstraint("user_id", "request_id"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    current_scene_key: Mapped[UUID | None] = mapped_column(Uuid)
    request_id: Mapped[UUID] = mapped_column(Uuid)
    lesson_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_versions.id", ondelete="RESTRICT")
    )


class SceneCheckpoint(Base):
    __tablename__ = "lesson_scene_progress"
    __table_args__ = (CheckConstraint("page >= 0 AND page <= 10000", name="valid_page"),)
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_runs.id", ondelete="CASCADE"), primary_key=True
    )
    scene_key: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    page: Mapped[int] = mapped_column(Integer)
