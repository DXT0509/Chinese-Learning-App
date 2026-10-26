from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.dictionary import DictionarySense


class CuratedSuggestion(BaseModel):
    entry_id: UUID
    simplified: str
    primary_pinyin: str
    short_vi_meaning: str
    available_languages: list[str]
    source: str = "APP_CURATED"
    content_version: int
    learning_level: int


class CuratedSearchResult(BaseModel):
    items: list[CuratedSuggestion]
    next_offset: int | None


class CuratedDetail(CuratedSuggestion):
    pinyin_numbered: str
    citation_pinyin: str
    meanings: dict[str, list[DictionarySense]]
    sino_vietnamese: str | None
    part_of_speech: str | None
    examples: list[dict[str, str]]
    review_status: str
    active: bool = True


class CuratedSaved(BaseModel):
    id: UUID
    dictionary_entry_id: UUID
    saved_at: datetime
    simplified: str
    pinyin: str
    short_vi_meaning: str
    short_en_meaning: str | None = None
    active: bool
    mastery_level: int
    next_review_at: datetime | None
    last_reviewed_at: datetime | None


class CuratedVocabularyPage(BaseModel):
    items: list[CuratedSaved]
    total: int
    next_cursor: str | None
