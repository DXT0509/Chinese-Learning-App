"""Coverage extensions retain strict grading, bindings and immutable installed payloads."""

import json
from pathlib import Path

import pytest

from app.services.policy_coverage import catalog_pos, prepare_coverage
from app.services.review_grading import grade
from app.services.review_targets import ReviewedPolicy
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_policy_preparation import entry


@pytest.mark.parametrize(
    "source,expected",
    [
        ("noun; verb", ["noun", "verb"]),
        ("verb, adjective, adverb", ["verb", "adjective", "adverb"]),
        ("proper noun", ["noun"]),
        ("modal verb", ["verb"]),
        ("noun; locality", ["noun"]),
        ("noun; time", ["noun"]),
        ("adjective; word element", ["adjective"]),
        ("measure word", ["classifier"]),
        ("verb|noun", ["noun", "verb"]),
    ],
)
def test_explicit_source_categories(source, expected):
    assert catalog_pos(source) == (expected, [])
    e = entry(part_of_speech=source)
    policies, _ = prepare_coverage([e])
    target = policies[0].target(e.word).snapshot()
    assert set(target["accepted_pos"]) == set(expected)
    assert grade("POS", expected, target)
    assert not grade("POS", expected + [expected[0]], target)
    if len(expected) > 1:
        assert not grade("POS", expected[:1], target)


@pytest.mark.parametrize(
    "source",
    [None, "idiom", "phrase", "quantifier", "word element", "noun; unknown", "phrase; modal"],
)
def test_unknown_categories_never_invented_or_skipped(source):
    policies, report = prepare_coverage([entry(part_of_speech=source)])
    assert not policies
    assert report["remaining_unresolved"] == 1


def test_missing_cue_requires_source_context_and_no_unrestricted_translation():
    e = entry(sino_vietnamese=None)
    assert not prepare_coverage([e])[0]
    e.examples = ["Tôi học mỗi ngày."]
    policies, _ = prepare_coverage([e])
    assert "Tôi học mỗi ngày." in policies[0].vietnamese_prompt
    assert "None" not in policies[0].vietnamese_prompt
    target = policies[0].target(e.word).snapshot()
    assert grade("HANZI", e.word.simplified, target)
    assert not grade("HANZI", "习", target)
    assert grade("PINYIN", "xue2", target)
    assert not grade("PINYIN", "xue3", target)


def test_shared_cue_is_not_a_collision_when_full_meaning_disambiguates():
    first = entry(part_of_speech="verb; noun")
    other = entry(simplified="校", lexical_key="校|xiao4", pinyin="xiào", pinyin_numbered="xiao4")
    other.meanings = ["trường học"]
    policies, _ = prepare_coverage([first, other])
    assert len(policies) == 2
    other.meanings = ["học"]
    assert not prepare_coverage([first, other])[0]
    other.published = False
    assert not prepare_coverage([first, other])[0]


def test_no_cue_cannot_evade_conflict_with_cued_peer():
    first = entry(sino_vietnamese=None)
    first.examples = ["Tôi học."]
    other = entry(
        simplified="习",
        lexical_key="习|xi2",
        pinyin="xí",
        pinyin_numbered="xi2",
        sino_vietnamese="tập",
    )
    policies, report = prepare_coverage([first, other])
    assert first.word.id not in {p.vocabulary_id for p in policies}
    assert report["counts"]["ANSWER_CONFLICT_EDITORIAL_REVIEW"] == 1


def test_new_homograph_cannot_be_conflated_even_when_held():
    first = entry(sino_vietnamese=None)
    first.examples = ["Tôi học."]
    other = entry(pinyin="xuè", pinyin_numbered="xue4", lexical_key="学|xue4")
    other.published = False
    assert not prepare_coverage([first, other])[0]


def test_existing_generated_and_manual_policies_preserved_and_stale_reported():
    e = entry()
    original = prepare_coverage([e])[0]
    assert prepare_coverage([e], original)[0] == original
    manual = original[0].model_copy(update={"policy_version": "authored-context-v1"})
    assert prepare_coverage([e], [manual])[0] == [manual]
    e.word.content_version += 1
    _, report = prepare_coverage([e], [manual])
    assert len(report["outdated_or_unknown_preserved_policies"]) == 1


def test_v2_installed_policy_is_revalidated_not_treated_as_manual():
    e = entry(sino_vietnamese=None)
    e.examples = ["Tôi học."]
    original = prepare_coverage([e])[0]
    assert prepare_coverage([e], original)[0] == original
    e.examples = ["Tôi học mỗi ngày."]
    policies, report = prepare_coverage([e], original)
    assert not policies and report["installed_valid"] == 0
    assert "POLICY_REQUIRES_NEW_CONTENT_VERSION" in report["records"][0]["reasons"]
    e.examples = []
    policies, report = prepare_coverage([e], original)
    assert not policies and report["installed_valid"] == 0
    with pytest.raises(ValueError, match="Conflicting"):
        prepare_coverage([e], [original[0], original[0].model_copy(update={"sense_key": "other"})])
    e.word.checksum = "b" * 64
    assert len(prepare_coverage([e], original)[1]["outdated_or_unknown_preserved_policies"]) == 1


def test_real_bundle_preserves_existing_policies_and_never_skips_pos():
    root = Path(__file__).resolve().parents[2] / "docs"
    before = json.loads(
        (root / "datasets/srs-catalog-policies-v1.json").read_text(encoding="utf-8")
    )
    after = json.loads((root / "datasets/srs-phase41d-policies.json").read_text(encoding="utf-8"))
    by_id = {p["vocabulary_id"]: p for p in after}
    assert len(by_id) == len(after)
    assert all(by_id[p["vocabulary_id"]] == p for p in before)
    for payload in after:
        policy = ReviewedPolicy.model_validate(payload)
        assert policy.accepted_pos and policy.pos_skip_reason is None


@pytest.mark.parametrize(
    "form,numbered,marked,level",
    [
        ("学生", "xue2 sheng1", "xué shēng", 0),
        ("图书馆", "tu2 shu1 guan3", "tú shū guǎn", 1),
        ("北京大学", "bei3 jing1 da4 xue2", "běi jīng dà xué", 5),
    ],
)
def test_character_count_and_complete_level_denominator(form, numbered, marked, level):
    e = entry(
        simplified=form,
        lexical_key=f"{form}|{numbered}",
        pinyin_numbered=numbered,
        pinyin=marked,
        learning_level=level,
        sino_vietnamese=None,
        part_of_speech="noun",
    )
    e.examples = ["Ngữ cảnh của mục từ đã học."]
    policies, report = prepare_coverage([e])
    assert f"{len(form)} chữ Hán" in policies[0].vietnamese_prompt
    assert report["per_level"][str(level)]["published"] == 1
    assert report["per_level"][str(level)]["proposed"] == 1
    assert prepare_coverage([e]) == (policies, report)


@pytest.mark.postgres
async def test_context_import_and_wire_contract_preserve_mastery(curated_sessions):
    from sqlalchemy import select

    from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
    from app.models.curated_vocabulary import CuratedVocabulary as Word
    from app.services.policy_installation import import_policies
    from app.services.policy_preparation import catalog_entries
    from app.services.review_engine import ReviewEngine
    from app.services.review_targets import ReviewedTargets
    from app.services.srs import SrsService
    from tests.test_srs_postgres import setup_word

    sessions = curated_sessions
    owner, saved, identifier = await setup_word(sessions)
    async with sessions() as session, session.begin():
        word = await session.get(Word, identifier)
        word.part_of_speech, word.sino_vietnamese = "verb; noun", "học"
        policies, _ = prepare_coverage(await catalog_entries(session))
        before = (await session.execute(select(Saved.__table__))).mappings().all()
        assert (await import_policies(session, policies))["would_insert"] == 1
        assert (await import_policies(session, policies, install=True))["inserted"] == 1
        assert (await import_policies(session, policies, install=True))["unchanged"] == 1
        assert (await session.execute(select(Saved.__table__))).mappings().all() == before
        target = await ReviewedTargets().resolve(session, word)
        assert target.gradeable and set(target.accepted_pos) == {"noun", "verb"}
    async with sessions() as session:
        attempt_id = (await SrsService(session).initialize(owner, saved))["attempt_id"]
    async with sessions() as session:
        response = await ReviewEngine(session).question(owner, attempt_id)
        from app.services.review_policy_v2 import project

        assert response["question"]["prompt_vi"] == project(target)["vietnamese_prompt"]
        assert response["question"]["character_count"] == 1
        assert "accepted_pos" not in str(response) and "accepted_pinyin" not in str(response)
        state = await session.get(Saved, saved)
        assert state.mastery_level == state.failure_count == state.due_review_count == 0
