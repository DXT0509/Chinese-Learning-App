import unicodedata
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SaveVocabulary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dictionary_entry_id: UUID


class VocabularyQuery(BaseModel):
    q: str = Field(default="", max_length=64)
    limit: int = Field(default=20, ge=1, le=50)
    cursor: str | None = Field(default=None, max_length=160)

    @field_validator("q")
    @classmethod
    def normalize(cls, value):
        if any(unicodedata.category(c).startswith("C") for c in value):
            raise ValueError("Invalid query")
        return unicodedata.normalize("NFC", value.strip())


class SavedVocabulary(BaseModel):
    id: UUID
    dictionary_entry_id: UUID
    saved_at: datetime
    simplified: str
    traditional: str
    pinyin: str
    short_vi_meaning: str | None = None
    short_en_meaning: str | None
    active: bool
    source_revision_at_save: str
    saved_snapshot: dict


class VocabularyPage(BaseModel):
    items: list[SavedVocabulary]
    total: int
    next_cursor: str | None


class VocabularyStatus(BaseModel):
    saved_id: UUID | None
