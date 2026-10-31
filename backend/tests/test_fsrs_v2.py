from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fsrs import Rating
from pydantic import ValidationError

from app.schemas.review_engine import HandwritingEvidence
from app.services.daily_review import TARGET_SECONDS, capacity, priority
from app.services.fsrs_scheduler import configuration, rating, replay, retrievability, review
from app.services.review_engine import ReviewEngine, evaluate
from app.services.srs_state import Outcome
from tests.test_review_draft_views import attempt
from tests.test_srs_postgres import NOW


def ink(answer="学"):
    return {
        "recognizer": "MLKIT_DIGITAL_INK_ZH_HANS_V1",
        "characters": [
            {
                "strokes": [[{"x": 1, "y": 1, "t": 0}, {"x": 5, "y": 5, "t": 20}]],
                "candidates": [c],
                "selected": c,
            }
            for c in answer
        ],
    }


def test_upstream_binary_schedule_expands_past_21_days_and_lapses():
    config = configuration()
    assert config["desired_retention"] == 0.9 and config["maximum_interval"] == 36500
    assert rating(Outcome.PASS) == Rating.Good and rating(Outcome.FAIL) == Rating.Again
    card, log = review(None, Outcome.PASS, NOW, config)
    assert log["rating"] == Rating.Good and card["stability"] > 0
    intervals = []
    from datetime import datetime

    for _ in range(12):
        now = datetime.fromisoformat(card["due"])
        card, _ = review(card, Outcome.PASS, now, config)
        intervals.append((datetime.fromisoformat(card["due"]) - now).total_seconds() / 86400)
    assert max(intervals) > 21
    overdue = datetime.fromisoformat(card["due"]) + timedelta(days=30)
    assert retrievability(card, overdue, config) < retrievability(
        card, datetime.fromisoformat(card["due"]), config
    )
    card, log = review(card, Outcome.FAIL, overdue, config)
    assert card["state"] == 3 and log["rating"] == Rating.Again
    assert datetime.fromisoformat(card["due"]) == overdue + timedelta(minutes=10)


def test_replay_is_deterministic_and_does_not_invent_history():
    config = configuration()
    assert replay([], config) is None
    history = [("PASS", NOW), ("FAIL", NOW + timedelta(days=10))]
    assert replay(history, config) == replay(history, config)
    card = replay(history, config)
    assert card["last_review"] == history[-1][1].isoformat()
    with pytest.raises(ValueError):
        review(card, Outcome.PASS, NOW, config)
    with pytest.raises(ValueError):
        configuration(1)


@pytest.mark.parametrize(
    "hanzi,pinyin,expected",
    [(True, True, "PASS"), (False, True, "FAIL"), (True, False, "FAIL"), (False, False, "FAIL")],
)
def test_two_stage_binary_and_no_answer_leakage(hanzi, pinyin, expected):
    row = attempt()
    row.target.update(review_version="two-stage-v2", applicable_stages=["HANZI", "PINYIN"])
    row.submissions = [{"stage": "HANZI", "action": "ANSWER", "answer": "错", "correct": hanzi}]
    view = ReviewEngine(None)._view(row)
    assert "correct_answer" not in view["feedback"][0]
    assert "simplified" not in view["question"]
    assert all("simplified" not in q for q in view["draft_questions"].values())
    with pytest.raises(HTTPException):
        evaluate(row)
    row.submissions.append(
        {"stage": "PINYIN", "action": "ANSWER", "answer": "ma3", "correct": pinyin}
    )
    assert evaluate(row).outcome(("HANZI", "PINYIN")) == expected
    assert ReviewEngine(None)._view(row)["feedback"][0]["correct_answer"] == ["马"]


@pytest.mark.parametrize("change", ["empty", "stationary", "time", "candidate", "nan", "oversized"])
def test_handwriting_contract_rejects_invalid_evidence(change):
    body = ink()
    char = body["characters"][0]
    if change == "empty":
        char["strokes"] = []
    if change == "stationary":
        char["strokes"][0][1].update(x=1, y=1)
    if change == "time":
        char["strokes"][0][1]["t"] = -1
    if change == "candidate":
        char["selected"] = "错"
    if change == "nan":
        char["strokes"][0][0]["x"] = float("nan")
    if change == "oversized":
        char["strokes"][0] *= 100
    with pytest.raises(ValidationError):
        HandwritingEvidence.model_validate(body)


def test_multicharacter_ink_and_daily_capacity_risk_order():
    assert len(HandwritingEvidence.model_validate(ink("学习")).characters) == 2
    assert TARGET_SECONDS == 1200
    assert capacity(0, 45) == 26 and capacity(1200, 45) == 0
    assert capacity(1200, 45, beyond=True) == 26
    a = SimpleNamespace(
        id="a", learning_activated=True, next_review_at=NOW - timedelta(days=1), saved_at=NOW
    )
    b = SimpleNamespace(
        id="b", learning_activated=False, next_review_at=NOW - timedelta(days=1), saved_at=NOW
    )
    assert priority(a, None, NOW) < priority(b, None, NOW)
    card = replay([("PASS", NOW - timedelta(days=10))], configuration())
    m = SimpleNamespace(card=card, configuration=configuration())
    assert priority(a, m, NOW) == priority(a, m, NOW)
