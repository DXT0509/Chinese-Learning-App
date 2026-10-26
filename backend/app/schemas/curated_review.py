"""Strict offline contracts for independent semantic reviewers; no provider calls."""

from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, field_validator, model_validator

from app.schemas.curated_vocabulary import CuratedRecord, StrictRecord, Text

POLICY = "zhvi-semantic-v1"
ASPECTS = (
    "simplified",
    "mandarin_pinyin_neutral_tones",
    "vietnamese_definitions",
    "sino_vietnamese",
    "example_correctness",
    "example_pinyin_alignment",
    "learning_difficulty",
    "duplicate_identity",
    "ambiguity",
)
Checksum = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class ModelIdentity(StrictRecord):
    provider: Text
    model: Text
    version: Text


class Finding(StrictRecord):
    aspect: Literal[*ASPECTS]
    severity: Literal["blocking", "warning"]
    message: Text
    resolved: bool = Field(strict=True)


class Assessment(StrictRecord):
    aspect: Literal[*ASPECTS]
    result: Literal["pass", "fail", "uncertain", "not_applicable"]
    rationale: Text


class AutomatedValidation(StrictRecord):
    validator_version: Literal["curated-record-v1"]
    content_checksum: Checksum
    passed: Literal[True]
    checks: list[Text]


class ReviewInput(StrictRecord):
    schema_version: Literal[1] = 1
    policy_version: Literal[POLICY] = POLICY
    generator: ModelIdentity
    content_checksum: Checksum
    content: CuratedRecord
    automated_validation: AutomatedValidation
    lexical_catalog: list[str] = Field(default_factory=list)
    required_aspects: list[str] = Field(default_factory=lambda: list(ASPECTS))
    instructions: str = (
        "Assess every aspect independently. Citation and neutral tones, natural Vietnamese, "
        "optional Sino-Vietnamese, examples and Pinyin alignment, levels 0-5, duplicate lexical "
        "identity and ambiguous senses/readings require semantic assessment. Mark uncertain "
        "items NEEDS_REVIEW. Do not treat mechanical validation as linguistic approval. "
        "Return ReviewResult JSON; never invent model provenance. Compare supplied batch "
        "identities and flag possible duplicates for operator resolution."
    )


class ReviewResult(StrictRecord):
    schema_version: Literal[1]
    review_id: UUID
    policy_version: Literal[POLICY]
    lexical_key: Text
    content_version: int = Field(gt=0, strict=True)
    content_checksum: Checksum
    generator: ModelIdentity
    reviewer: ModelIdentity
    reviewed_at: AwareDatetime
    decision: Literal["AI_APPROVED", "NEEDS_REVIEW", "REJECTED"]
    confidence: float = Field(ge=0, le=1)
    assessments: list[Assessment] = Field(min_length=9, max_length=9)
    findings: list[Finding]
    automated_validation: AutomatedValidation

    @field_validator("reviewed_at")
    @classmethod
    def utc_timestamp(cls, value):
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def evidence_integrity(self):
        if {a.aspect for a in self.assessments} != set(ASPECTS):
            raise ValueError("Each policy aspect must be assessed exactly once")
        if self.reviewed_at > datetime.now(UTC):
            raise ValueError("Review timestamp is in the future")
        if self.automated_validation.content_checksum != self.content_checksum:
            raise ValueError("Validation checksum mismatch")
        if self.decision == "AI_APPROVED":
            if self.generator.provider.casefold() == self.reviewer.provider.casefold() and (
                self.generator.model.casefold() == self.reviewer.model.casefold()
            ):
                raise ValueError("Independent model or provider required")
            if (
                self.confidence < 0.95
                or any(a.result not in {"pass", "not_applicable"} for a in self.assessments)
                or any(f.severity == "blocking" and not f.resolved for f in self.findings)
            ):
                raise ValueError("Unresolved or low-confidence assessment cannot approve")
            if any(
                a.result == "not_applicable" and a.aspect != "sino_vietnamese"
                for a in self.assessments
            ):
                raise ValueError("Required semantic checks cannot be skipped")
        return self
