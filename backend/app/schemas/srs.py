from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.services.srs_contract import Stage
from app.services.srs_state import Phase


class InitializeReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    saved_id: UUID
    request_id: UUID | None = None


class Progress(BaseModel):
    saved_id: UUID
    vocabulary_id: UUID
    mastery_level: int
    phase: Phase
    phase_step: int
    level_progress: int
    next_review_at: datetime
    last_reviewed_at: datetime | None
    is_active: bool
    schedule_version: int
    due_review_count: int
    failure_count: int
    practice_count: int


class ProgressDetail(Progress):
    available: bool


class DueQueue(BaseModel):
    as_of: datetime
    items: list[Progress]


class MasteryCount(BaseModel):
    mastery_level: int = Field(ge=0, le=5)
    count: int = Field(ge=0)


class Dashboard(BaseModel):
    scheduler_version: Literal["fsrs-6.3.2/binary-v2"] = "fsrs-6.3.2/binary-v2"
    as_of: datetime
    available_count: int
    due_count: int
    suspended_count: int
    grading_available: bool
    mastery_distribution: list[MasteryCount]
    daily_review: dict | None = None


class ReviewSession(BaseModel):
    attempt_id: UUID
    saved_id: UUID
    mode: Literal["DUE", "PRACTICE"]
    started_at: datetime
    grading_available: bool
    applicable_stages: list[Stage]
    disabled_stages: dict[Stage, str]
    reason: str | None
    content_version: int
    skipped_stages: list[dict[str, str]] = Field(default_factory=list)
