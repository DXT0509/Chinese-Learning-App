from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PersonalVocabularyEntry(Base):
    __tablename__ = "personal_vocabulary_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "dictionary_entry_id"),
        Index("ix_personal_vocabulary_owner_saved", "user_id", "saved_at", "id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    dictionary_entry_id: Mapped[UUID] = mapped_column(
        ForeignKey("dictionary_entries.id", ondelete="RESTRICT")
    )
    source_revision_at_save: Mapped[str] = mapped_column(Text)
    saved_snapshot: Mapped[dict] = mapped_column(JSONB)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
