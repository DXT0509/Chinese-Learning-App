"""Filesystem authoring sidecars; executable output remains roadmap schema version 1."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.curated_vocabulary import CuratedExample
from app.schemas.roadmap import Contract, VocabularyReference

Text = Annotated[str, Field(min_length=1, max_length=4000)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
QuizKind = Literal["CHARACTER", "PINYIN", "WORD_TO_MEANING", "MEANING_TO_WORD"]


class Review(Contract):
    status: Literal["UNREVIEWED", "REVIEWED"] = "UNREVIEWED"
    reviewer: Text | None = None
    evidence: Text | None = None
    content_sha256: Digest | None = None

    @model_validator(mode="after")
    def attestation(self):
        if self.status == "REVIEWED" and not (
            self.reviewer and self.evidence and self.content_sha256
        ):
            raise ValueError("review needs named reviewer, evidence and exact content checksum")
        return self


class Analysis(Contract):
    character_position: Annotated[int, Field(strict=True, ge=0)]
    character: Annotated[str, Field(min_length=1, max_length=1)]
    component: Annotated[str, Field(min_length=1, max_length=20)]
    position: Literal[
        "LEFT", "RIGHT", "TOP", "BOTTOM", "ENCLOSING", "ENCLOSED", "OVERLAPPING", "WHOLE"
    ]
    role: Literal["SEMANTIC_RADICAL", "PHONETIC", "STRUCTURAL"]
    explanation_vi: Text
    interpretation: Literal["HISTORICAL", "MODERN_MNEMONIC", "ORIGIN_UNAVAILABLE"]
    historical_source: Text | None = None
    review: Review = Review()

    @model_validator(mode="after")
    def supported_history(self):
        if self.interpretation == "HISTORICAL" and not self.historical_source:
            raise ValueError("historical analysis needs a cited source; do not invent etymology")
        if self.interpretation != "HISTORICAL" and self.historical_source:
            raise ValueError("mnemonics/unavailable origins cannot claim historical verification")
        return self


class Example(Contract):
    content: CuratedExample
    pinyin_numbered: Text
    target_character_position: Annotated[int, Field(strict=True, ge=0)]
    difficulty: Annotated[int, Field(strict=True, ge=0, le=5)]
    audio: UUID | None = None
    review: Review = Review()


class EnrichmentInput(Contract):
    reference: VocabularyReference
    components: Annotated[list[Analysis], Field(max_length=100)] = Field(default_factory=list)
    examples: Annotated[list[Example], Field(max_length=10)] = Field(default_factory=list)
    notes_vi: Text | None = None
    notes_review: Review = Review()


class AssetInput(Contract):
    id: UUID
    version: Annotated[int, Field(strict=True, ge=1)]
    purpose: Literal["AUDIO", "STROKE_ORDER", "STRUCTURED_STROKES"]
    reference: VocabularyReference
    simplified: Text
    pinyin_numbered: Text | None = None
    file: Text
    sha256: Digest
    byte_length: Annotated[int, Field(strict=True, ge=1, le=16_777_216)]
    media_type: Literal[
        "audio/wav",
        "audio/mpeg",
        "audio/ogg",
        "image/gif",
        "image/png",
        "application/json",
    ]
    source: Text
    attribution: Text
    license: Text
    redistribution_allowed: bool = False
    origin: Literal["HUMAN_RECORDED", "TTS", "AUTHORED", "DATASET"]
    provider: Text | None = None
    review: Review = Review()


class Group(Contract):
    key: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,100}$")]
    section: Annotated[str, Field(min_length=1, max_length=100)] = "hsk-0"
    vocabulary: Annotated[list[VocabularyReference], Field(min_length=1, max_length=1000)]


class Templates(Contract):
    quizzes: list[QuizKind] = Field(
        default_factory=lambda: ["CHARACTER", "PINYIN", "WORD_TO_MEANING", "MEANING_TO_WORD"]
    )
    choice_count: Annotated[int, Field(strict=True, ge=2, le=10)] = 3
    handwriting: bool = True
    pronunciation: bool = True
    pronunciation_repetitions: Annotated[int, Field(strict=True, ge=1, le=20)] = 2
    review_quizzes: list[QuizKind] | None = None
    components_activity: bool = True
    review_introduction_required: bool = True
    pinyin_tone_distractors: bool = False

    @model_validator(mode="after")
    def no_duplicates(self):
        if len(self.quizzes) != len(set(self.quizzes)):
            raise ValueError("duplicate quiz templates")
        if self.review_quizzes is not None and (
            not self.review_quizzes or len(self.review_quizzes) != len(set(self.review_quizzes))
        ):
            raise ValueError("review quizzes must be nonempty and unique")
        return self


class PreparationPlan(Contract):
    schema_version: Literal[1] = 1
    id: UUID
    code: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,100}$")]
    version: Annotated[int, Field(strict=True, ge=1)]
    title: Annotated[str, Field(min_length=1, max_length=255)]
    review_interval: Annotated[int, Field(strict=True, ge=1, le=100)] = 3
    groups: Annotated[list[Group], Field(min_length=1, max_length=1000)]
    templates: Templates = Templates()
    enrichments: list[EnrichmentInput] = Field(default_factory=list)
    assets: list[AssetInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def stable_identities(self):
        words = [r.vocabulary_id for g in self.groups for r in g.vocabulary]
        for items, label in (
            (words, "vocabulary introductions"),
            ([g.key for g in self.groups], "group keys"),
            ([e.reference.vocabulary_id for e in self.enrichments], "enrichments"),
            ([a.id for a in self.assets], "assets"),
        ):
            if len(items) != len(set(items)):
                raise ValueError(f"duplicate {label}")
        if any(e.reference.vocabulary_id not in words for e in self.enrichments):
            raise ValueError("enrichment must target an introduced identity")
        return self


class StrokeCharacter(Contract):
    character: Annotated[str, Field(min_length=1, max_length=1)]
    # Ordered original centerlines in normalized coordinates, no inferred stroke order.
    strokes: Annotated[
        list[Annotated[list[tuple[float, float]], Field(min_length=2, max_length=1000)]],
        Field(min_length=1, max_length=100),
    ]

    @model_validator(mode="after")
    def normalized(self):
        if any(not (0 <= x <= 1 and 0 <= y <= 1) for s in self.strokes for x, y in s):
            raise ValueError("stroke points must be finite normalized coordinates")
        return self


class StructuredStrokes(Contract):
    schema_version: Literal[1] = 1
    characters: Annotated[list[StrokeCharacter], Field(min_length=1, max_length=100)]
