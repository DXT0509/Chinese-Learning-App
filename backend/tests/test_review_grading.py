import unicodedata

import pytest
from pydantic import ValidationError

from app.schemas.review_engine import StageSubmission
from app.services.review_grading import grade, hanzi, pinyin_matches


@pytest.mark.parametrize(
    ("answer", "target", "correct"),
    [
        (" nǐ hǎo ", "ni3 hao3", True),
        ("ni3hao3", "ni3 hao3", True),
        ("ni2 hao3", "ni3 hao3", False),
        ("ni hao", "ni3 hao3", False),
        ("ma", "ma5", True),
        ("ma5", "ma5", True),
        ("ma1", "ma5", False),
        ("nǚ", "nü3", True),
        ("nv3", "nü3", True),
        ("nü3", "nü3", True),
        ("nu:3", "nü3", True),
        ("NV3", "nü3", True),
        ("nv4", "nü3", False),
        ("lü4 se4", "lü4 se4", True),
        ("lv4 se4", "lü4 se4", True),
        ("lu:4se4", "lü4 se4", True),
        ("lu4 se4", "lü4 se4", False),
        ("NU:3", "nü3", True),
        ("nu3", "nü3", False),
        ("xī’ān", "xi1 an1", True),
        ("xiān", "xi1 an1", False),
        ("xīān", "xi1 an1", False),
        ("xi1an1", "xi1 an1", True),
        ("xi1 an", "xi1 an1", False),
        ("xǐ3", "xi3", False),
        ("ma0", "ma5", False),
        ("shéi", "shei2", True),
        ("shuí", "shei2", False),
        ("shen2 me5", "shen2 me5", True),
        ("shén me", "shen2 me5", True),
        ("shen2 me2", "shen2 me5", False),
    ],
)
def test_pinyin_tones_boundaries_and_reading_identity(answer, target, correct):
    assert pinyin_matches(answer, target) is correct
    assert pinyin_matches(unicodedata.normalize("NFD", answer), target) is correct


def test_hanzi_exact_lexical_identity_and_pos_set():
    target = {"accepted_simplified": ["学"], "accepted_pos": ["noun", "classifier"]}
    assert hanzi(" 学 ") == "学"
    assert grade("HANZI", " 学 ", target)
    for answer in ("學", "学习", "学。", "学\u200b"):
        assert not grade("HANZI", answer, target)
    assert grade("POS", ["classifier", "noun"], target)
    for answer in (["noun"], ["noun", "noun", "classifier"], ["verb"], "noun"):
        assert not grade("POS", answer, target)


@pytest.mark.parametrize(
    "changes",
    [
        {"correct": True},
        {"mastery": 5},
        {"phase": "REVIEW"},
        {"passed": True},
        {"next_review_at": "2030-01-01"},
        {"answer": ["noun"]},
        {"action": "HINT", "answer": "学"},
        {"stage": "POS", "answer": "noun"},
    ],
)
def test_client_cannot_supply_verdict_or_wrong_shape(changes):
    with pytest.raises(ValidationError):
        StageSubmission.model_validate(
            {
                "submission_key": "00000000-0000-0000-0000-000000000001",
                "stage": "HANZI",
                "answer": "学",
                **changes,
            }
        )


def test_reviewed_measure_word_sense_and_pronunciation_identity():
    from types import SimpleNamespace
    from uuid import uuid4

    from app.services.review_targets import ReviewedPolicy

    identifier = uuid4()
    word = SimpleNamespace(
        id=identifier,
        lexical_key="口|kou3",
        simplified="口",
        pinyin="kǒu",
        pinyin_numbered="kou3",
        part_of_speech="noun; classifier",
        content_version=1,
        checksum="a" * 64,
    )
    policy = ReviewedPolicy(
        vocabulary_id=identifier,
        content_version=1,
        checksum="a" * 64,
        policy_version="fixture-v1",
        sense_key="family-member-classifier",
        vietnamese_prompt="Lượng từ chỉ số người trong gia đình",
        reviewed_by="synthetic fixture",
        ambiguity_resolution="Selected classifier sense, excludes mouth",
        accepted_pos=["classifier"],
    )
    target = policy.target(word)
    assert target.gradeable and target.accepted_pos == ("classifier",)
    assert grade("POS", ["classifier"], target.snapshot())
    assert not grade("POS", ["noun", "classifier"], target.snapshot())
    assert not grade("PINYIN", "kou4", target.snapshot())
    with pytest.raises(ValueError, match="Stale policy"):
        policy.model_copy(update={"checksum": "b" * 64}).target(word)
    with pytest.raises(ValidationError):
        ReviewedPolicy.model_validate(policy.model_dump() | {"vietnamese_prompt": "口 là gì?"})
