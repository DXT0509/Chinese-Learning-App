"""Learner-facing progress only. Never calculates an interval or a due timestamp."""

from dataclasses import replace

from app.services.srs_state import Outcome, Phase, State


def advance_mastery(state: State, outcome: Outcome, now) -> State:
    mastery, phase, step, progress = (
        state.mastery_level,
        state.phase,
        state.phase_step,
        state.level_progress,
    )
    if outcome == Outcome.FAIL:
        mastery = max(0, mastery - 1)
        phase, step, progress = Phase.RELEARNING if mastery else Phase.LEARNING, 0, 0
    elif phase == Phase.LEARNING:
        if step == 2:
            mastery, phase, step = 1, Phase.REVIEW, 0
        else:
            step += 1
    elif phase == Phase.RELEARNING:
        if step == 0:
            step = 1
        else:
            phase, step = Phase.REVIEW, 0
    elif mastery < 5:
        progress += 1
        if progress == 2:
            mastery, progress = mastery + 1, 0
    return replace(
        state,
        mastery_level=mastery,
        phase=phase,
        phase_step=step,
        level_progress=progress,
        last_reviewed_at=now,
    )
