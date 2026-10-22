import unicodedata
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints, field_validator

QueryText = Annotated[str, StringConstraints(min_length=1, max_length=64)]


class DictionaryQuery(BaseModel):
    q: QueryText
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0, le=1000)

    @field_validator("q")
    @classmethod
    def normalize(cls, value: str):
        value = unicodedata.normalize("NFC", value.strip())
        if not value or any(unicodedata.category(c).startswith("C") for c in value):
            raise ValueError("Invalid dictionary query")
        return value


class DictionarySuggestion(BaseModel):
    entry_id: UUID
    simplified: str
    traditional: str | None
    primary_pinyin: str
    short_vi_meaning: str | None = None
    available_languages: list[str]
    source: str
    source_revision: str


class DictionarySearchResult(BaseModel):
    items: list[DictionarySuggestion]
    next_offset: int | None


class DictionarySense(BaseModel):
    sense_number: int
    gloss: str


class DictionaryProvenance(BaseModel):
    source: str
    revision: str
    sha256: str
    source_url: str
    license: str
    license_url: str
    attribution: str
    changes: str


class CharacterEnrichmentProvenance(DictionaryProvenance):
    review_status: str


class DictionaryCharacterInfo(BaseModel):
    scope: str = "character"
    form: str
    positions: list[int]
    traditional_positions: list[int]
    source_hanzi: str
    traditional: str | None
    pinyin: str
    sino_vietnamese: str
    vietnamese_gloss: str
    # A false value prevents treating another reading as this lexical entry's reading.
    matches_entry_pronunciation: bool | None
    provenance: CharacterEnrichmentProvenance


class DictionaryExample(BaseModel):
    text: str
    translations: dict[str, str] = Field(default_factory=dict)
    source: str


class DictionaryAudio(BaseModel):
    reference: str
    source: str
    license: str


class DictionaryDetail(DictionarySuggestion):
    pinyin_numbered: str
    citation_pinyin: str
    meanings: dict[str, list[DictionarySense]]
    sino_vietnamese: str | None = None
    parts_of_speech: list[str] = Field(default_factory=list)
    examples: list[DictionaryExample] = Field(default_factory=list)
    audio: list[DictionaryAudio] = Field(default_factory=list)
    active: bool
    provenance: DictionaryProvenance
    character_enrichments: list[DictionaryCharacterInfo] = Field(default_factory=list)
