"""Catalog cue safety, reproducibility and transactional operator imports."""

from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsTargetPolicy
from app.services.policy_installation import import_policies
from app.services.policy_preparation import CatalogEntry, catalog_entries, prepare
from app.services.review_targets import ReviewedTargets
from tests.test_curated_vocabulary import (
    curated_sessions as curated_sessions,  # noqa: PLC0414
)
from tests.test_srs_postgres import setup_word


def entry(**changes):
    values = {
        "id": uuid4(),
        "simplified": "学",
        "pinyin": "xué",
        "pinyin_numbered": "xue2",
        "lexical_key": "学|xue2",
        "sino_vietnamese": "học",
        "part_of_speech": "verb",
        "content_version": 1,
        "checksum": "a" * 64,
        "review_status": "HUMAN_APPROVED",
    }
    values.update(changes)
    return CatalogEntry(Word(**values), ["học"], True)


def test_standard_and_repeatable_generation():
    e = entry()
    first, report = prepare([e])
    assert prepare([e]) == (first, report)
    assert first[0].target(e.word).gradeable
    assert "«học»" in first[0].vietnamese_prompt
    assert first[0].accepted_pos == ["verb"]
    assert report["counts"]["final_proposed_coverage"] == 1


def test_multiple_meanings_retained_without_sense_alignment():
    e = entry()
    e.meanings = ["học", "nghiên cứu"]
    policies, _ = prepare([e])
    assert "học; nghiên cứu" in policies[0].vietnamese_prompt
    assert policies[0].sense_key == "whole-lexeme-cued-recall"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"part_of_speech": None}, "MISSING_POS"),
        ({"part_of_speech": "verb; noun"}, "MULTIPLE_POS_REQUIRES_SENSE_REVIEW"),
        ({"part_of_speech": "quantifier"}, "UNSUPPORTED_POS"),
        ({"sino_vietnamese": None}, "MISSING_OR_UNSUITABLE_HAN_VIET_CUE"),
        ({"sino_vietnamese": "học / hiệu"}, "MISSING_OR_UNSUITABLE_HAN_VIET_CUE"),
        ({"pinyin_numbered": "xue3"}, "INVALID_LEXICAL_IDENTITY_OR_PROMPT"),
        ({"simplified": "學"}, "INVALID_LEXICAL_IDENTITY_OR_PROMPT"),
    ],
)
def test_unresolved_linguistic_data(changes, reason):
    policies, report = prepare([entry(**changes)])
    assert policies == []
    assert report["records"][0]["status"] == "NEEDS_GRADING_REVIEW"
    assert reason in report["records"][0]["reasons"]


@pytest.mark.parametrize("meanings", [[], [" "], ["学"], ["..."]])
def test_missing_or_unsuitable_vietnamese(meanings):
    e = entry()
    e.meanings = meanings
    policies, report = prepare([e])
    assert not policies
    assert report["counts"]["MISSING_OR_UNSUITABLE_VIETNAMESE_PROMPT"] == 1


def test_measure_word_supported_without_inventing_pos():
    e = entry(part_of_speech="measure word")
    assert prepare([e])[0][0].accepted_pos == ["classifier"]


def test_multiple_readings_even_when_other_identity_is_held():
    first = entry()
    other = entry(
        pinyin_numbered="xue4", pinyin="xuè", lexical_key="学|xue4", sino_vietnamese="hiệu"
    )
    other.published = False
    policies, report = prepare([first, other])
    assert not policies
    assert report["counts"]["MULTIPLE_PRONUNCIATIONS_REQUIRE_SENSE_REVIEW"] == 2
    assert report["counts"]["PUBLICATION_EXCLUDED"] == 1


def test_shared_cue_against_held_entry_and_unicode_normalization():
    e = entry()
    other = entry(
        simplified="校",
        pinyin_numbered="xiao4",
        pinyin="xiào",
        lexical_key="校|xiao4",
        sino_vietnamese=" HỌC ",
    )
    other.published = False
    assert not prepare([e, other])[0]


def test_shared_gloss_with_distinct_explicit_cues_is_not_free_translation():
    first = entry()
    other = entry(
        simplified="习",
        pinyin_numbered="xi2",
        pinyin="xí",
        lexical_key="习|xi2",
        sino_vietnamese="tập",
    )
    policies, _ = prepare([other, first])
    assert len(policies) == 2
    assert policies[0].vietnamese_prompt != policies[1].vietnamese_prompt
    assert prepare([first, other])[0] == policies


def test_manual_policy_preserved_and_stale_policy_reported():
    e = entry()
    manual = prepare([e])[0][0].model_copy(
        update={
            "policy_version": "manual-v1",
            "vietnamese_prompt": "Ngữ cảnh riêng đã duyệt",
        }
    )
    assert prepare([e], [manual])[0] == [manual]
    stale = manual.model_copy(update={"checksum": "b" * 64})
    _, report = prepare([e], [stale])
    assert report["counts"]["outdated_or_unknown_preserved_policies"] == 1
    with pytest.raises(ValueError, match="Stale"):
        stale.target(e.word)
    e.published = False
    assert prepare([e], [manual])[0] == []


def test_duplicate_input_and_conflicting_manual_rejected():
    e = entry()
    with pytest.raises(ValueError, match="Duplicate"):
        prepare([e, e])
    p = prepare([e])[0][0]
    with pytest.raises(ValueError, match="Conflicting"):
        prepare([e], [p, p.model_copy(update={"vietnamese_prompt": "other"})])


async def prepared_fixture(sessions):
    owner, saved, identifier = await setup_word(sessions)
    async with sessions() as session, session.begin():
        w = await session.get(Word, identifier)
        w.sino_vietnamese, w.part_of_speech = "học", "verb"
    async with sessions() as session:
        policies, _ = prepare(await catalog_entries(session))
    return owner, saved, identifier, policies


@pytest.mark.postgres
async def test_import_dry_run_idempotence_and_manual_preservation(curated_sessions):
    sessions = curated_sessions
    _, _, identifier, policies = await prepared_fixture(sessions)
    assert len(policies) == 1
    async with sessions() as session, session.begin():
        assert (await import_policies(session, policies))["inserted"] == 0
        assert not list(await session.scalars(select(SrsTargetPolicy)))
        assert (await import_policies(session, policies, install=True))["inserted"] == 1
        assert (await import_policies(session, policies, install=True))["unchanged"] == 1
    # Simulate an already installed manual policy in this isolated fixture.
    async with sessions() as session, session.begin():
        existing = await session.get(SrsTargetPolicy, (identifier, 1, policies[0].checksum))
        manual = deepcopy(existing.policy)
        manual.update(policy_version="manual-v1", vietnamese_prompt="Đã duyệt riêng")
        existing.policy = manual
    async with sessions() as session, session.begin():
        assert (await import_policies(session, policies, install=True))["preserved_manual"] == 1
        assert (
            await session.get(SrsTargetPolicy, (identifier, 1, policies[0].checksum))
        ).policy == manual


@pytest.mark.postgres
async def test_import_duplicates_stale_and_publication_guard(curated_sessions):
    sessions = curated_sessions
    _, _, identifier, policies = await prepared_fixture(sessions)
    async with sessions() as session, session.begin():
        with pytest.raises(ValueError, match="Duplicate"):
            await import_policies(session, policies * 2, install=True)
        with pytest.raises(ValueError, match="Stale"):
            await import_policies(session, [policies[0].model_copy(update={"checksum": "b" * 64})])
        forged = policies[0].model_copy(update={"vietnamese_prompt": "Unreviewed substitute"})
        with pytest.raises(ValueError, match="regenerate"):
            await import_policies(session, [forged])
        w = await session.get(Word, identifier)
        w.review_status = "NEEDS_REVIEW"
        await session.flush()
        with pytest.raises(ValueError, match="not currently published"):
            await import_policies(session, policies, install=True)


@pytest.mark.postgres
@pytest.mark.parametrize("change", ["checksum", "cue_collision"])
async def test_new_ambiguity_disables_generated_policy_without_penalty(curated_sessions, change):
    from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
    from app.services.srs import SrsService

    sessions = curated_sessions
    owner, saved, identifier, policies = await prepared_fixture(sessions)
    async with sessions() as session, session.begin():
        await import_policies(session, policies, install=True)
        w = await session.get(Word, identifier)
        assert (await ReviewedTargets().resolve(session, w)).gradeable
    async with sessions() as session, session.begin():
        w = await session.get(Word, identifier)
        if change == "checksum":
            w.checksum = "b" * 64
        else:
            session.add(
                Word(
                    id=uuid4(),
                    lexical_key="校|xiao4",
                    simplified="校",
                    pinyin="xiào",
                    pinyin_numbered="xiao4",
                    sino_vietnamese="học",
                    part_of_speech="noun",
                    learning_level=0,
                    review_status="NEEDS_REVIEW",
                    content_version=1,
                    checksum="b" * 64,
                    batch_id=w.batch_id,
                )
            )
    async with sessions() as session:
        result = await SrsService(session).initialize(owner, saved)
        assert not result["grading_available"]
        progress = await session.get(Saved, saved)
        assert progress.failure_count == progress.due_review_count == progress.schedule_version == 0


@pytest.mark.postgres
async def test_import_is_all_or_nothing(curated_sessions):
    sessions = curated_sessions
    _, _, _, policies = await prepared_fixture(sessions)
    unknown = policies[0].model_copy(update={"vocabulary_id": uuid4()})
    with pytest.raises(ValueError, match="not currently published"):
        async with sessions() as session, session.begin():
            await import_policies(session, [*policies, unknown], install=True)
    async with sessions() as session:
        assert not list(await session.scalars(select(SrsTargetPolicy)))


def test_installed_generated_policies_are_reassessed_and_not_treated_as_manual():
    e = entry()
    installed = prepare([e])[0]
    e.word.part_of_speech = "verb; noun"
    policies, report = prepare([e], installed)
    assert policies == []
    assert report["counts"]["existing_manually_reviewed_policies"] == 0
