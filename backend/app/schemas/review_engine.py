from datetime import datetime
from itertools import pairwise
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.services.srs_contract import Stage

AnswerText = Annotated[str, StringConstraints(max_length=500)]
PosAnswer = Annotated[list[Annotated[str, StringConstraints(max_length=40)]], Field(max_length=11)]


class InkPoint(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    x: float = Field(ge=0, le=10000)
    y: float = Field(ge=0, le=10000)
    t: int = Field(ge=0)


class InkCharacter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    strokes: list[Annotated[list[InkPoint], Field(min_length=2, max_length=128)]] = Field(
        min_length=1, max_length=64
    )
    candidates: list[Annotated[str, StringConstraints(min_length=1, max_length=1)]] = Field(
        min_length=1, max_length=20
    )
    selected: Annotated[str, StringConstraints(min_length=1, max_length=1)]

    @model_validator(mode="after")
    def valid_ink(self):
        if self.selected not in self.candidates:
            raise ValueError("Selected transcription must be a recognized candidate")
        for stroke in self.strokes:
            if any(b.t < a.t for a, b in pairwise(stroke)):
                raise ValueError("Stroke timestamps must be monotonic")
            if len({(p.x, p.y) for p in stroke}) < 2:
                raise ValueError("A stroke must contain movement")
        return self


class HandwritingEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recognizer: Literal["MLKIT_DIGITAL_INK_ZH_HANS_V1"]
    characters: list[InkCharacter] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def bounded_points(self):
        if sum(len(s) for c in self.characters for s in c.strokes) > 6000:
            raise ValueError("Too many ink points")
        return self


class StageSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    submission_key: UUID
    stage: Stage
    action: Literal["ANSWER", "HINT", "REVEAL"] = "ANSWER"
    answer: AnswerText | PosAnswer | None = None
    handwriting: HandwritingEvidence | None = None

    @model_validator(mode="after")
    def answer_shape(self):
        if self.action == "ANSWER":
            if self.stage == Stage.POS and not isinstance(self.answer, list):
                raise ValueError("POS requires a category array")
            if self.stage != Stage.POS and not isinstance(self.answer, str):
                raise ValueError("Text answer required")
        elif self.answer is not None:
            raise ValueError("Hint/reveal does not accept an answer")
        if self.handwriting is not None and (self.stage != Stage.HANZI or self.action != "ANSWER"):
            raise ValueError("Ink belongs to the Hanzi answer only")
        return self


class FinalizeReview(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DailyPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    continue_beyond_target: bool = False


class ActiveTimeReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active_ms: int = Field(ge=0, le=1800000)


class StageFeedback(BaseModel):
    stage: Stage
    first_correct: bool | None
    assisted: bool
    correct_answer: list[str] | None = None
    tone_mismatches: list[int] = Field(default_factory=list)
    syllable_mismatches: list[int] = Field(default_factory=list)


class StageQuestion(BaseModel):
    input_mode: Literal["TEXT", "SINGLE_SELECT", "MULTI_SELECT"]
    prompt_vi: str | None = None
    simplified: str | None = None
    options: list[str] | None = None
    character_count: int | None = Field(default=None, ge=1)


class StageResponse(BaseModel):
    review_version: str = "three-stage-v1"
    attempt_id: UUID
    stage: Stage | None
    expires_at: datetime
    status: Literal["COMPLETED", "READY_TO_FINALIZE", "IN_PROGRESS"]
    disabled_stages: dict[Stage, str]
    skipped_stages: list[dict[str, str]]
    feedback: list[StageFeedback]
    question: StageQuestion | None = None
    draft_questions: dict[Stage, StageQuestion] = Field(default_factory=dict)
    submission_correct: bool | None = None
    hint_vi: str | None = None


class FinalizedResponse(BaseModel):
    attempt_id: UUID
    outcome: Literal["PASS", "FAIL"]
    scheduling_applied: bool
    mode: Literal["DUE", "PRACTICE"]
    state_after: dict
    previous_mastery_level: int = Field(ge=0, le=5)
    resulting_mastery_level: int = Field(ge=0, le=5)
    completed_at: datetime
    feedback: list[StageFeedback]
