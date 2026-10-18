"""Strict version 1 authoring contracts. No executable expressions or runtime scoring."""

import unicodedata
from typing import Annotated, Literal, Self
from uuid import UUID, uuid5

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

CONTENT_NAMESPACE = UUID("10e2d39e-7898-5d09-867a-5b517e52daf0")
Identifier = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,99}$")]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Notes = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
Position = Annotated[int, Field(ge=0, le=1000)]
Version = Annotated[int, Field(ge=1, le=100000)]


def content_id(kind: str, alias: str) -> UUID:
    """Explicit UUIDs allow reviewed adoption; aliases never depend on file paths."""
    try:
        return UUID(alias)
    except ValueError:
        return uuid5(CONTENT_NAMESPACE, f"{kind}:{alias}")


def version_id(kind: str, alias: str, version: int) -> UUID:
    return uuid5(CONTENT_NAMESPACE, f"{kind}:{content_id(kind, alias)}:v{version}")


class ContentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_text(cls, value):
        if isinstance(value, dict):
            for key in ("schema_version", "contract_version"):
                if key in value and type(value[key]) is not int:
                    raise ValueError(f"{key} must be an integer")
            return {
                key: unicodedata.normalize("NFC", item) if isinstance(item, str) else item
                for key, item in value.items()
            }
        return value


def hanzi_occurrences(text: str) -> list[tuple[int, str]]:
    """Supported Hanzi with optional variation selector; offsets are Unicode scalars."""
    result = []
    for offset, char in enumerate(text):
        code = ord(char)
        if 0xFE00 <= code <= 0xFE0F or 0xE0100 <= code <= 0xE01EF:
            if not result or len(result[-1][1]) != 1:
                raise ValueError("variation selector must follow one Hanzi")
            position, base = result[-1]
            result[-1] = (position, base + char)
        elif 0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF or 0x20000 <= code <= 0x323AF:
            result.append((offset, char))
        else:
            raise ValueError("Slice 1 supports Hanzi and attached variation selectors only")
    if not result:
        raise ValueError("at least one Hanzi is required")
    return result


class CharacterDefinition(ContentModel):
    id: Identifier
    hanzi: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    stroke_count: Annotated[int, Field(gt=0, le=100)] | None = None
    stroke_order_asset: Identifier | None = None

    @field_validator("hanzi")
    @classmethod
    def one_character(cls, value):
        if len(hanzi_occurrences(value)) != 1:
            raise ValueError("character definition must have exactly one Hanzi")
        return value


class CharacterOccurrence(ContentModel):
    position: Position
    character: Identifier


class VocabularyDefinition(ContentModel):
    schema_version: Literal[1]
    id: Identifier
    simplified: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    pinyin: ShortText
    sino_vietnamese: ShortText | None = None
    vietnamese_meaning: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
    ]
    part_of_speech: ShortText | None = None
    notes: Notes | None = None
    audio_asset: Identifier | None = None
    characters: Annotated[list[CharacterDefinition], Field(min_length=1, max_length=100)]
    occurrences: Annotated[list[CharacterOccurrence], Field(min_length=1, max_length=255)]

    @model_validator(mode="after")
    def aligned_occurrences(self) -> Self:
        ids = [content_id("character", character.id) for character in self.characters]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate character identifiers")
        glyphs = {content_id("character", item.id): item.hanzi for item in self.characters}
        actual = []
        for item in self.occurrences:
            key = content_id("character", item.character)
            if key not in glyphs:
                raise ValueError(f"occurrences: missing character reference {item.character}")
            actual.append((item.position, glyphs[key]))
        if actual != hanzi_occurrences(self.simplified):
            raise ValueError("occurrences must follow exact Hanzi source offsets and spelling")
        if set(glyphs) != {content_id("character", item.character) for item in self.occurrences}:
            raise ValueError("unused character definition")
        return self


class TargetVocabulary(ContentModel):
    binding: Literal["TARGET_VOCABULARY"]


class InformationConfig(ContentModel):
    vocabulary_ref: TargetVocabulary
    fields: Annotated[
        list[Literal["PINYIN", "SINO_VIETNAMESE", "MEANING", "POS", "NOTES"]],
        Field(min_length=1, max_length=5),
    ]

    @field_validator("fields")
    @classmethod
    def unique_fields(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("duplicate information fields")
        return value


class AnalysisConfig(ContentModel):
    vocabulary_ref: TargetVocabulary
    expansion: Literal["ORDERED_CHARACTERS"]
    missing_analysis: Literal["SHOW_UNREVIEWED_PLACEHOLDER"]


class SceneEnvelope(ContentModel):
    scene_key: Identifier
    position: Position
    contract_version: Literal[1]
    required: bool


class InformationScene(SceneEnvelope):
    scene_type: Literal["VOCABULARY_INFORMATION"]
    config: InformationConfig


class AnalysisScene(SceneEnvelope):
    scene_type: Literal["CHARACTER_ANALYSIS"]
    config: AnalysisConfig


Scene = Annotated[InformationScene | AnalysisScene, Field(discriminator="scene_type")]


class TemplateDefinition(ContentModel):
    schema_version: Literal[1]
    id: Identifier
    version: Version
    description: Notes
    scenes: Annotated[list[Scene], Field(min_length=1, max_length=30)]

    @model_validator(mode="after")
    def ordered_scenes(self) -> Self:
        keys = [content_id("scene", scene.scene_key) for scene in self.scenes]
        positions = [scene.position for scene in self.scenes]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate scene identifiers")
        if len(set(positions)) != len(positions) or positions != sorted(positions):
            raise ValueError("scene positions must be unique and in increasing order")
        return self


class TemplateReference(ContentModel):
    id: Identifier
    version: Version


class VocabularyTarget(ContentModel):
    vocabulary: Identifier
    position: Position
    role: Literal["TEACHES"]


class LessonDefinition(ContentModel):
    schema_version: Literal[1]
    id: Identifier
    version: Version
    lesson_type: Literal["VOCABULARY"]
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    template: TemplateReference
    vocabulary: Annotated[list[VocabularyTarget], Field(min_length=1, max_length=1)]


class AssetMetadata(ContentModel):
    width: Annotated[int, Field(gt=0)] | None = None
    height: Annotated[int, Field(gt=0)] | None = None
    duration_ms: Annotated[int, Field(gt=0)] | None = None
    format: ShortText | None = None


class AssetDefinition(ContentModel):
    schema_version: Literal[1]
    id: Identifier
    storage_key: Annotated[str, StringConstraints(pattern=r"^sha256/[0-9a-f]{64}\.[a-z0-9]+$")]
    media_type: Literal[
        "audio/mpeg", "audio/wav", "image/png", "image/webp", "image/gif", "application/json"
    ]
    sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: Annotated[int, Field(gt=0, le=50000000)]
    metadata: AssetMetadata

    @model_validator(mode="after")
    def hash_matches_key(self) -> Self:
        if self.storage_key.split("/")[1].split(".")[0] != self.sha256:
            raise ValueError("storage key must contain the declared SHA-256")
        return self
