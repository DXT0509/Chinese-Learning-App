"""Internal Phase 4.1B boundary, deliberately absent from HTTP input schemas.

Only the server evaluator may construct ValidatedReview after grading a
pinned target. This module defines evidence, not a client correctness protocol.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.services.srs_state import Outcome


class Stage(StrEnum):
    HANZI = "HANZI"
    PINYIN = "PINYIN"
    POS = "POS"


class StageVerdict(StrEnum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"


@dataclass(frozen=True)
class ReviewTarget:
    """Pinned identity and editorial policy; answer sets are never sent to clients.

    A sense key is scoped to this content version, not an invented catalog sense ID.
    An unqualified Vietnamese gloss is not itself an acceptable answer policy.
    """

    vocabulary_id: UUID
    lexical_key: str
    content_version: int
    checksum: str
    applicable_stages: tuple[Stage, ...] = (Stage.HANZI, Stage.PINYIN)
    disabled_stages: tuple[tuple[Stage, str], ...] = (
        (Stage.POS, "POS_REQUIRES_REVIEWED_SENSE_POLICY"),
    )
    policy_version: str | None = None
    sense_key: str | None = None
    vietnamese_prompt: str | None = None
    accepted_simplified: tuple[str, ...] = ()
    accepted_pinyin_numbered: tuple[str, ...] = ()
    accepted_pos: tuple[str, ...] = ()
    pos_prompt_vi: str | None = None
    pos_options: tuple[str, ...] = ()

    def __post_init__(self):
        if self.content_version < 1 or not self.lexical_key or not self.checksum:
            raise ValueError("Pinned vocabulary identity required")
        if self.applicable_stages not in (
            (Stage.HANZI, Stage.PINYIN),
            (Stage.HANZI, Stage.PINYIN, Stage.POS),
        ):
            raise ValueError("Ordered Hanzi/Pinyin and optional POS required")
        disabled = dict(self.disabled_stages)
        if any(s in disabled for s in self.applicable_stages) or (
            Stage.POS not in self.applicable_stages and not disabled.get(Stage.POS)
        ):
            raise ValueError("Skipped POS requires an explicit reason")

    @property
    def gradeable(self) -> bool:
        return bool(
            self.policy_version
            and self.sense_key
            and self.vietnamese_prompt
            and self.accepted_simplified
            and self.accepted_pinyin_numbered
            and (Stage.POS not in self.applicable_stages or self.accepted_pos)
        )

    def snapshot(self) -> dict:
        from dataclasses import asdict

        return {
            **asdict(self),
            "vocabulary_id": str(self.vocabulary_id),
            "gradeable": self.gradeable,
        }


@dataclass(frozen=True)
class StageEvidence:
    stage: Stage
    first_submission: StageVerdict
    hints_used: bool = False
    answer_revealed: bool = False


@dataclass(frozen=True)
class ValidatedReview:
    attempt_id: UUID
    evaluator_version: str
    stages: tuple[StageEvidence, ...]

    def outcome(self, applicable: tuple[Stage, ...]) -> Outcome:
        if (
            not self.evaluator_version.strip()
            or applicable != (Stage.HANZI, Stage.PINYIN)
            or not self.stages
            or len(self.stages) > len(applicable)
            or tuple(s.stage for s in self.stages) != applicable[: len(self.stages)]
        ):
            raise ValueError("Ordered server evidence required")
        if any(not isinstance(s.first_submission, StageVerdict) for s in self.stages):
            raise ValueError("Typed server verdict required")
        failed = any(
            s.first_submission == StageVerdict.INCORRECT or s.hints_used or s.answer_revealed
            for s in self.stages
        )
        if failed:
            return Outcome.FAIL
        if len(self.stages) != len(applicable):
            raise ValueError("All applicable stages required for PASS")
        return (
            Outcome.PASS
            if all(
                s.first_submission == StageVerdict.CORRECT
                and not s.hints_used
                and not s.answer_revealed
                for s in self.stages
            )
            else Outcome.FAIL
        )


class ReviewEvaluator(Protocol):
    async def evaluate(self, attempt_id: UUID) -> ValidatedReview:
        """Read persisted ordered first submissions/hints and pinned answer policy."""
        ...
