"""Strict authoring contract. Validation never publishes content."""

import re
import unicodedata
from typing import Annotated, Literal

from opencc import OpenCC
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.core.pinyin import tone_marks

Text = Annotated[str, StringConstraints(min_length=1, max_length=1000)]
converter = OpenCC("t2s")


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize(cls, value):
        if isinstance(value, str):
            value = unicodedata.normalize("NFC", value.strip())
            if any(unicodedata.category(c).startswith("C") for c in value):
                raise ValueError("Control characters are forbidden")
        return value


def is_hanzi(character):
    return "\u3400" <= character <= "\u9fff" or "\U00020000" <= character <= "\U000323af"


def simplified_only(value: str):
    if converter.convert(value) != value or not any(is_hanzi(c) for c in value):
        raise ValueError("Expected Simplified Chinese")
    return value


class CuratedExample(StrictRecord):
    simplified: Text
    pinyin: Text
    vietnamese: Text
    _simplified = field_validator("simplified")(simplified_only)

    @field_validator("pinyin")
    @classmethod
    def tone_marked_example(cls, value):
        if any(c.isdigit() for c in value) or not any(c.isalpha() for c in value):
            raise ValueError("Examples require readable tone-marked Pinyin")
        return value


class CuratedRecord(StrictRecord):
    schema_version: Literal[1]
    lexical_key: Text
    simplified: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    pinyin: Text
    pinyin_numbered: Text
    sino_vietnamese: Text | None = None
    part_of_speech: Text | None = None
    learning_level: int = Field(ge=0, le=5, strict=True)
    classification_standard: Literal["APP_CURATED"] = "APP_CURATED"
    difficulty_reference: Literal["HSK_2_0"] = "HSK_2_0"
    review_status: Literal["GENERATED_UNREVIEWED", "NEEDS_REVIEW"] = "GENERATED_UNREVIEWED"
    content_version: int = Field(ge=1, strict=True)
    vietnamese_meanings: list[Text] = Field(min_length=1, max_length=30)
    english_meanings: list[Text] = Field(default_factory=list, max_length=30)
    examples: list[CuratedExample] = Field(default_factory=list, max_length=10)
    _simplified = field_validator("simplified")(simplified_only)

    @field_validator("simplified")
    @classmethod
    def lexical_hanzi(cls, value):
        if not all(is_hanzi(c) for c in value):
            raise ValueError("Lexical forms must contain only Han characters")
        return value

    @field_validator("vietnamese_meanings", "english_meanings")
    @classmethod
    def meanings(cls, values):
        values = [unicodedata.normalize("NFC", v.strip()) for v in values]
        if len(values) != len(set(values)) or any(
            not v or any(unicodedata.category(c).startswith("C") for c in v) for v in values
        ):
            raise ValueError("Duplicate, empty or invalid meanings")
        return values

    @model_validator(mode="after")
    def pronunciation_identity(self):
        # Explicit syllable boundaries and neutral tone 5 keep lexical identity stable.
        if not re.fullmatch(r"[a-zü]+[1-5](?: [a-zü]+[1-5])*", self.pinyin_numbered):
            raise ValueError("Use lowercase numbered syllables separated by spaces")
        if tone_marks(self.pinyin_numbered) != self.pinyin:
            raise ValueError("Pinyin forms disagree")
        if len(self.pinyin_numbered.split()) != len(self.simplified):
            raise ValueError("Expected one syllable per character")
        if self.lexical_key != f"{self.simplified}|{self.pinyin_numbered}":
            raise ValueError("Lexical key must match form and pronunciation")
        return self
