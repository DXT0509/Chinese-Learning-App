"""Progress state and UTC contracts. All intervals are calculated by upstream FSRS."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class Phase(StrEnum):
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class Outcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


def utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timezone-aware time required")
    return value.astimezone(UTC)


@dataclass(frozen=True)
class State:
    mastery_level: int
    phase: Phase
    phase_step: int
    level_progress: int
    next_review_at: datetime
    last_reviewed_at: datetime | None = None

    def __post_init__(self):
        utc(self.next_review_at)
        if self.last_reviewed_at is not None:
            utc(self.last_reviewed_at)
        valid = (
            (
                self.phase == Phase.LEARNING
                and self.mastery_level == 0
                and self.phase_step in (0, 1, 2)
                and self.level_progress == 0
            )
            or (
                self.phase == Phase.REVIEW
                and 1 <= self.mastery_level <= 5
                and self.phase_step == 0
                and self.level_progress in (0, 1)
                and (self.mastery_level < 5 or self.level_progress == 0)
            )
            or (
                self.phase == Phase.RELEARNING
                and 1 <= self.mastery_level <= 4
                and self.phase_step in (0, 1)
                and self.level_progress == 0
            )
        )
        if not valid:
            raise ValueError("Invalid SRS state")
