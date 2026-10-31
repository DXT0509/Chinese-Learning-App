"""Real reviewed inventory, stage secrecy and isolated persisted grammar grading."""

import json
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.curated_vocabulary import VocabularyExample
from app.schemas.curated_vocabulary import is_hanzi
from app.services.contextual_grammar import POLICY_VERSION, ContextualGrammar
from app.services.policy_installation import import_policies
from app.services.review_engine import ReviewEngine
from app.services.review_grading import grade
from app.services.review_targets import ReviewedPolicy, ReviewedTargets
from app.services.srs import SrsService
from app.services.srs_contract import Stage
from scripts.prepare_remaining_policies import prepare_remaining
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_srs_postgres import NOW, setup_word

DOCS = Path(__file__).resolve().parents[2] / "docs"


def load(name):
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def policies():
    return [
        ReviewedPolicy.model_validate(p) for p in load("datasets/srs-phase41d-remaining-v2.json")
    ]


def source_word(row):
    source = row["source_payload"]
    return Word(
        id=UUID(row["vocabulary_id"]),
        checksum=row["checksum"],
        **{
            key: source[key]
            for key in (
                "lexical_key",
                "simplified",
                "pinyin",
                "pinyin_numbered",
                "content_version",
                "part_of_speech",
            )
        },
    )


def test_complete_inventory_no_denominator_reduction_and_previous_payloads_unchanged():
    previous = load("datasets/srs-phase41d-policies.json")
    complete = load("datasets/srs-phase41d-complete-v2.json")
    catalog = load("srs-phase41d-final-audit.json")["records"]
    published = {r["vocabulary_id"] for r in catalog if r["published"]}
    by_id = {p["vocabulary_id"]: p for p in complete}
    assert set(by_id) == published and len(complete) == len(published) == 2804
    assert all(by_id[p["vocabulary_id"]] == p for p in previous)
    assert [ReviewedPolicy.model_validate(p).model_dump(mode="json") for p in previous] == previous
    checkpoint = load("datasets/srs-phase41d-editorial-checkpoint.json")
    remaining, prepared, report = prepare_remaining(checkpoint, previous)
    assert [p.model_dump(mode="json") for p in prepared] == complete
    assert len(remaining) == report["prepared"] == 242 and not report["pending"]
    assert prepare_remaining(checkpoint, previous) == (remaining, prepared, report)


def test_every_review_has_real_source_binding_and_all_three_strict_stages():
    checkpoint = load("datasets/srs-phase41d-editorial-checkpoint.json")
    source = {r["vocabulary_id"]: r for r in checkpoint["records"]}
    roles, assessments = set(), set()
    for policy in policies():
        row = source[str(policy.vocabulary_id)]
        word = source_word(row)
        target = policy.target(word)
        snapshot = target.snapshot()
        review = policy.grammatical_review
        assert review.source_example in {e["simplified"] for e in row["source_payload"]["examples"]}
        assert target.applicable_stages == (Stage.HANZI, Stage.PINYIN, Stage.POS)
        assert not target.disabled_stages and not policy.pos_skip_reason
        assert not any(is_hanzi(c) for c in target.vietnamese_prompt)
        assert word.pinyin_numbered not in target.vietnamese_prompt
        assert target.accepted_pinyin_numbered == (word.pinyin_numbered,)
        assert target.accepted_simplified == (word.simplified,)
        assert f"【{word.simplified}】" in target.pos_prompt_vi
        assert grade("HANZI", word.simplified, snapshot)
        assert not grade("HANZI", "错误", snapshot)
        assert grade("PINYIN", word.pinyin_numbered, snapshot)
        assert not grade("PINYIN", "cuo4 wu4", snapshot)
        assert grade("POS", policy.accepted_pos, snapshot)
        assert not grade("POS", list(review.options), snapshot)
        assert not grade("POS", ["idiom"], snapshot)
        for option in review.options:
            assert grade("POS", [option], snapshot) == (option in policy.accepted_pos)
        roles.update(policy.accepted_pos)
        assessments.add(review.assessment)
    assert {"predicate", "attribute", "adverbial", "object", "subject", "complement"} <= roles
    assert assessments == {
        "SYNTACTIC_ROLE",
        "GRAMMATICAL_FUNCTION",
        "EXPRESSION_KIND",
        "MORPHEME_KIND",
    }


@pytest.mark.parametrize("change", ["missing_evidence", "skip", "accept_idiom", "wrong_family"])
def test_no_blanket_idiom_category_or_implicit_stage_skip(change):
    payload = policies()[0].model_dump(mode="json")
    if change == "missing_evidence":
        payload.pop("grammatical_review")
    elif change == "skip":
        payload.update(accepted_pos=[], pos_skip_reason="DICTIONARY_IS_INCOMPLETE")
    elif change == "accept_idiom":
        payload["accepted_pos"] = ["idiom"]
    else:
        payload["grammatical_review"]["assessment"] = "EXPRESSION_KIND"
    with pytest.raises(ValidationError):
        ReviewedPolicy.model_validate(payload)


def test_bound_version_source_pos_and_marked_occurrence_cannot_drift():
    policy = policies()[0]
    row = load("datasets/srs-phase41d-editorial-checkpoint.json")["records"][0]
    word = source_word(row)
    word.checksum = "f" * 64
    with pytest.raises(ValueError, match="Stale"):
        policy.target(word)
    word.checksum = row["checksum"]
    word.part_of_speech = "noun"
    with pytest.raises(ValueError, match="source POS changed"):
        policy.target(word)
    word.part_of_speech = "idiom"
    altered = policy.model_copy(deep=True)
    altered.grammatical_review.context_simplified = "这是另一句话。"
    with pytest.raises(ValueError, match="exact lexical form"):
        altered.target(word)


async def install_fixture(sessions):
    owner, saved, identifier = await setup_word(sessions)
    async with sessions() as session, session.begin():
        word = await session.get(Word, identifier)
        word.part_of_speech = "phrase"
        session.add(
            VocabularyExample(
                vocabulary_id=identifier,
                position=0,
                simplified="我学汉语。",
                pinyin="Wǒ xué Hànyǔ.",
                vietnamese="Tôi học tiếng Trung.",
            )
        )
        await session.flush()
        policy = ReviewedPolicy(
            vocabulary_id=identifier,
            content_version=word.content_version,
            checksum=word.checksum,
            policy_version=POLICY_VERSION,
            sense_key="synthetic-contextual-fixture",
            vietnamese_prompt="Học (một chữ đã học).",
            reviewed_by="synthetic isolated fixture",
            ambiguity_resolution="Exact synthetic fixture spelling and reading, contextual role only.",
            accepted_pos=["predicate"],
            grammatical_review=ContextualGrammar(
                lexical_category="expression",
                assessment="SYNTACTIC_ROLE",
                source_part_of_speech="phrase",
                source_example="我学汉语。",
                context_simplified="我学汉语。",
                rationale="Learning is the predicate of I.",
                question_vi="Phần trong ngoặc giữ chức năng nào trong câu?",
            ),
        )
        before = (await session.execute(select(Saved.__table__))).mappings().all()
        assert (await import_policies(session, [policy]))["would_insert"] == 1
        assert (await import_policies(session, [policy], install=True))["inserted"] == 1
        assert (await import_policies(session, [policy], install=True))["unchanged"] == 1
        assert (await session.execute(select(Saved.__table__))).mappings().all() == before
    return owner, saved, identifier, policy


@pytest.mark.postgres
@pytest.mark.parametrize("wrong_stage", [None, "HANZI", "PINYIN"])
async def test_persisted_contextual_review_no_keys_leak_and_any_wrong_stage_fails(
    curated_sessions, wrong_stage
):
    from tests.test_review_engine import submission

    sessions = curated_sessions
    owner, saved, _, _policy = await install_fixture(sessions)
    async with sessions() as session:
        attempt = (await SrsService(session, lambda: NOW).initialize(owner, saved))["attempt_id"]
    async with sessions() as session:
        first = await ReviewEngine(session, lambda: NOW).question(owner, attempt)
        assert first["question"]["input_mode"] == "TEXT"
        assert not any(is_hanzi(c) for c in first["question"]["prompt_vi"])
        # Phase 4.4 permits draft option lists, including every possible answer;
        # the actual accepted set and source review evidence remain private.
        assert set(first["draft_questions"]) == {"HANZI", "PINYIN"}
        assert "accepted_pos" not in str(first) and "source_example" not in str(first)
        assert "学" not in str(first) and "xue2" not in str(first)
        assert first["feedback"] == []
    for stage, answer in [("HANZI", "学"), ("PINYIN", "xue2")]:
        if stage == wrong_stage:
            answer = "xue3" if stage == "PINYIN" else "\u9519"
        async with sessions() as session:
            await ReviewEngine(session, lambda: NOW).submit(
                owner, attempt, submission(stage, answer)
            )
    async with sessions() as session:
        state = await session.get(Saved, saved)
        assert state.mastery_level == state.due_review_count == state.failure_count == 0
    async with sessions() as session:
        result = await ReviewEngine(session, lambda: NOW).finalize(owner, attempt)
        assert result["outcome"] == ("PASS" if wrong_stage is None else "FAIL")


@pytest.mark.postgres
async def test_context_source_mismatch_rejects_install_and_runtime_without_penalty(
    curated_sessions,
):
    sessions = curated_sessions
    owner, saved, identifier, policy = await install_fixture(sessions)
    async with sessions() as session, session.begin():
        source = await session.get(VocabularyExample, (identifier, 0))
        source.simplified = "他学习。"
    async with sessions() as session, session.begin():
        with pytest.raises(ValueError, match="source example"):
            await import_policies(session, [policy])
        word = await session.get(Word, identifier)
        assert not (await ReviewedTargets().resolve(session, word)).gradeable
    async with sessions() as session:
        result = await SrsService(session, lambda: NOW).initialize(owner, saved)
        assert not result["grading_available"]
        state = await session.get(Saved, saved)
        assert state.mastery_level == state.failure_count == state.schedule_version == 0
