"""Read-only full-population session selection and non-revealing character counts."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.review_engine import ReviewEngine
from tests.test_curated_vocabulary import curated_client as curated_client  # noqa: PLC0414
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_review_engine import policy_for, start
from tests.test_srs_postgres import NOW, setup_word


@pytest.mark.parametrize("word", ["口", "学生", "你好", "图书馆", "对不起"])
def test_structured_word_length_is_not_a_recognition_hint(word):
    attempt = SimpleNamespace(
        id=uuid4(),
        started_at=NOW,
        completed_at=None,
        submissions=[],
        target={
            "applicable_stages": ["HANZI", "PINYIN"],
            "review_version": "two-stage-v2",
            "disabled_stages": [],
            "accepted_simplified": [word],
            "vietnamese_prompt": "nghĩa đầy đủ",
        },
    )
    question = ReviewEngine(None)._view(attempt)["question"]
    assert question == {
        "input_mode": "TEXT",
        "prompt_vi": "nghĩa đầy đủ",
        "character_count": len(word),
    }


@pytest.mark.postgres
async def test_hanzi_count_does_not_reveal_simplified_or_pinyin(curated_sessions):
    owner, saved, word = await setup_word(curated_sessions)
    await policy_for(curated_sessions, word)
    attempt = await start(curated_sessions, owner, saved)
    async with curated_sessions() as session:
        question = (await ReviewEngine(session, lambda: NOW).question(owner, attempt))["question"]
        assert question["character_count"] == 1
        assert "simplified" not in question and "pinyin" not in question
