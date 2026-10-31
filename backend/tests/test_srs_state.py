from datetime import UTC, datetime

import pytest

from app.services.review_mastery import advance_mastery
from app.services.srs_contract import Stage, StageEvidence, StageVerdict, ValidatedReview
from app.services.srs_state import Outcome, Phase, State

NOW = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("mastery", range(6))
def test_mastery_changes_without_calculating_due_dates(mastery):
    state = State(mastery, Phase.REVIEW if mastery else Phase.LEARNING, 0, 0, NOW)
    failed = advance_mastery(state, Outcome.FAIL, NOW)
    assert failed.mastery_level == max(0, mastery - 1)
    assert failed.next_review_at == NOW
    first = advance_mastery(state, Outcome.PASS, NOW)
    second = advance_mastery(first, Outcome.PASS, NOW)
    assert second.next_review_at == NOW
    if 0 < mastery < 5:
        assert second.mastery_level == mastery + 1


def test_typed_ordered_first_submission_contract():
    from uuid import uuid4

    stages = (Stage.HANZI, Stage.PINYIN)
    evidence = tuple(StageEvidence(s, StageVerdict.CORRECT) for s in stages)
    assert ValidatedReview(uuid4(), "test", evidence).outcome(stages) == Outcome.PASS
    assert (
        ValidatedReview(
            uuid4(),
            "test",
            (evidence[0], StageEvidence(Stage.PINYIN, StageVerdict.CORRECT, hints_used=True)),
        ).outcome(stages)
        == Outcome.FAIL
    )
    assert (
        ValidatedReview(
            uuid4(), "test", (StageEvidence(Stage.HANZI, StageVerdict.INCORRECT), evidence[1])
        ).outcome(stages)
        == Outcome.FAIL
    )
    with pytest.raises(ValueError):
        ValidatedReview(uuid4(), "test", evidence[::-1]).outcome(stages)
    with pytest.raises(ValueError):
        ValidatedReview(uuid4(), "test", evidence).outcome((*stages, Stage.POS))
    with pytest.raises(ValueError):
        ValidatedReview(uuid4(), "test", evidence[:1]).outcome(stages)
    assert (
        ValidatedReview(
            uuid4(), "test", (StageEvidence(Stage.HANZI, StageVerdict.INCORRECT),)
        ).outcome(stages)
        == Outcome.FAIL
    )


def test_review_target_requires_explicit_supported_sense_and_pos_policy():
    from uuid import uuid4

    from app.services.srs_contract import ReviewTarget

    target = ReviewTarget(uuid4(), "test|test1", 1, "fixture-checksum")
    assert not target.gradeable
    from dataclasses import replace

    supported = replace(
        target,
        policy_version="fixture",
        sense_key="sense-1",
        vietnamese_prompt="fixture",
        accepted_simplified=("fixture",),
        accepted_pinyin_numbered=("test1",),
    )
    assert supported.gradeable
    with pytest.raises(ValueError):
        replace(target, disabled_stages=())
    pos = replace(
        supported, applicable_stages=(Stage.HANZI, Stage.PINYIN, Stage.POS), disabled_stages=()
    )
    assert not pos.gradeable
