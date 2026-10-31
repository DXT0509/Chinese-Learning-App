"""Draft views never expose unsubmitted answer keys; canonical order stays unchanged."""

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.review_engine import StageResponse
from app.services.review_engine import ReviewEngine, evaluate
from app.services.review_grading import pinyin_mismatches


def attempt():
    return SimpleNamespace(
        id=uuid4(),
        started_at=datetime.now(UTC),
        completed_at=None,
        submissions=[],
        target={
            "applicable_stages": ["HANZI", "PINYIN"],
            "review_version": "two-stage-v2",
            "disabled_stages": [],
            "vietnamese_prompt": "con ngựa",
            "accepted_simplified": ["马"],
            "accepted_pinyin_numbered": ["ma3"],
            "accepted_pos": ["noun"],
            "pos_prompt_vi": "Chọn từ loại.\n【马】跑了。",
            "pos_options": ["noun", "verb"],
        },
    )


def test_drafts_hide_chinese_and_pinyin_before_hanzi():
    row = attempt()
    view = ReviewEngine(None)._view(row)
    StageResponse.model_validate(view)
    payload = json.dumps(jsonable_encoder(view), ensure_ascii=False)
    assert "马" not in payload and "ma3" not in payload
    assert set(view["draft_questions"]) == {"HANZI", "PINYIN"}
    assert view["feedback"] == [] and view["stage"] == "HANZI"


def test_only_sealed_stage_reveals_solution_and_unanswered_cannot_finalize():
    row = attempt()
    row.submissions = [{"stage": "HANZI", "action": "ANSWER", "answer": "错", "correct": False}]
    view = ReviewEngine(None)._view(row)
    assert "correct_answer" not in view["feedback"][0]
    assert "ma3" not in json.dumps(jsonable_encoder(view), ensure_ascii=False)
    assert "simplified" not in view["draft_questions"]["PINYIN"]
    assert view["stage"] == "PINYIN"
    with pytest.raises(HTTPException) as failure:
        evaluate(row)
    assert failure.value.status_code == 409


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("ma4", {"tone_mismatches": [1], "syllable_mismatches": []}),
        ("ba3", {"tone_mismatches": [], "syllable_mismatches": [1]}),
        ("mǎ", {}),
        ("ma", {}),
        ("ma3ma3", {}),
    ],
)
def test_conservative_pinyin_diagnosis(answer, expected):
    assert pinyin_mismatches(answer, "ma3") == expected
