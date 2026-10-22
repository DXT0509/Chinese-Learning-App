"""Real PostgreSQL maintenance/enrichment tests, rolled back after each test."""

import os
from dataclasses import asdict, replace
from uuid import uuid5

import httpx
import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.dependencies.authentication import current_user_id
from app.dependencies.database import get_session
from app.main import create_app
from app.models import (
    DictionaryCharacterEnrichment,
    DictionaryEnrichmentImport,
    DictionaryEntry,
    DictionaryImport,
    User,
    Vocabulary,
)
from app.repositories.dictionary import DictionaryRepository
from app.schemas.dictionary import DictionaryQuery
from app.services.cedict import NAMESPACE, SOURCE, DictionaryImportError, parse_row
from app.services.dictionary import DictionaryService
from app.services.dictionary_enrichment import (
    CharacterDataset,
    CharacterRecord,
    import_character_enrichment,
)
from app.services.dictionary_import import import_dictionary
from app.services.dictionary_maintenance import correct_revision
from app.services.dictionary_revision import artifact_revision
from tests.test_dictionary import FIXTURE, fixture_dataset
from tests.test_dictionary_enrichment import character_dataset

pytestmark = pytest.mark.postgres


@pytest.fixture
async def sessions():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            yield async_sessionmaker(
                connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            await transaction.rollback()
    finally:
        await engine.dispose()


async def seed_legacy(sessions):
    dataset = fixture_dataset()
    legacy_id = uuid5(NAMESPACE, f"{SOURCE}:revision:your-actual-source-release")
    async with sessions() as session, session.begin():
        # Simulate the historical pre-validation import; new imports cannot use this label.
        await session.execute(
            insert(DictionaryImport).values(
                id=legacy_id,
                source=SOURCE,
                revision="your-actual-source-release",
                sha256=dataset.sha256,
                source_url="https://www.mdbg.net/chinese/dictionary?page=cedict",
                license="CC-BY-SA-4.0",
                license_url="https://creativecommons.org/licenses/by-sa/4.0/",
                attribution="Test source attribution preserved",
                changes="Test transformation preserved",
                entry_count=len(dataset.entries),
            )
        )
        await session.execute(
            insert(DictionaryEntry),
            [
                dict(asdict(row), source=SOURCE, import_id=legacy_id, active=True)
                for row in dataset.entries
            ],
        )
        session.add(User(display_name="Preserved user"))
        session.add(Vocabulary(simplified="测试", pinyin="cè shì", vietnamese_meaning="TEST ONLY"))
    return dataset, legacy_id


async def snapshot(sessions, model):
    async with sessions() as session:
        return [dict(row) for row in (await session.execute(select(model.__table__))).mappings()]


async def test_dry_run_then_idempotent_repair_preserves_every_entry_and_reference(sessions):
    dataset, legacy_id = await seed_legacy(sessions)
    entries_before = await snapshot(sessions, DictionaryEntry)
    imports_before = await snapshot(sessions, DictionaryImport)
    users_before, curriculum_before = (
        await snapshot(sessions, User),
        await snapshot(sessions, Vocabulary),
    )
    async with sessions() as session:
        preview = await correct_revision(session, FIXTURE, dataset.sha256)
        assert not preview["changed"] and not preview["already_corrected"]
    assert await snapshot(sessions, DictionaryImport) == imports_before
    async with sessions() as session:
        applied = await correct_revision(session, FIXTURE, dataset.sha256, confirm=True)
        repeated = await correct_revision(session, FIXTURE, dataset.sha256, confirm=True)
        assert applied["changed"] and repeated["already_corrected"] and not repeated["changed"]
        # Replay the corrected label: no duplicate snapshot despite preserving the old UUID.
        replay = await import_dictionary(session, dataset, applied["to_revision"])
        assert replay["replayed"]
    after = await snapshot(sessions, DictionaryImport)
    assert len(after) == 1 and after[0]["id"] == legacy_id
    for field in (
        "sha256",
        "source_url",
        "attribution",
        "license",
        "license_url",
        "changes",
        "imported_at",
    ):
        assert after[0][field] == imports_before[0][field]
    assert after[0]["revision_correction"]["original_revision"] == "your-actual-source-release"
    assert await snapshot(sessions, DictionaryEntry) == entries_before
    assert await snapshot(sessions, User) == users_before
    assert await snapshot(sessions, Vocabulary) == curriculum_before
    async with sessions() as session:
        result = await DictionaryService(DictionaryRepository(session)).search(
            DictionaryQuery(q="学")
        )
        assert {row.source_revision for row in result.items} == {applied["to_revision"]}


async def test_repair_rejects_collision_and_wrong_checksum(sessions):
    dataset, _ = await seed_legacy(sessions)
    async with sessions() as session:
        with pytest.raises(DictionaryImportError, match="SHA-256"):
            await correct_revision(session, FIXTURE, "0" * 64, confirm=True)
        target = artifact_revision(FIXTURE, dataset.sha256)["revision"]
        with pytest.raises(DictionaryImportError, match="placeholder import"):
            await import_dictionary(session, dataset, target)
        async with session.begin():
            # Simulate an already ambiguous database; the maintenance command must refuse it.
            existing = (await session.execute(select(DictionaryImport.__table__))).mappings().one()
            duplicate = dict(existing)
            duplicate.update(id=uuid5(NAMESPACE, f"{SOURCE}:revision:{target}"), revision=target)
            await session.execute(insert(DictionaryImport).values(duplicate))
        with pytest.raises(DictionaryImportError, match="unambiguous"):
            await correct_revision(session, FIXTURE, dataset.sha256, confirm=True)


async def test_new_import_service_rejects_placeholders(sessions):
    async with sessions() as session:
        with pytest.raises(DictionaryImportError, match="placeholder"):
            await import_dictionary(session, fixture_dataset(), "your-actual-source-release")


async def install_catalog(sessions):
    dataset = fixture_dataset()
    # Extra synthetic dictionary rows test repeated characters and independent readings.
    extra = [
        parse_row(row)
        for row in [
            "我 我 [wo3] /TEST SELF/",
            "學學 学学 [xue2 xue2] /TEST REPETITION/",
            "學生 学生 [Xue2 sheng1] /TEST DISTINCT CASE/",
        ]
    ]
    dataset = replace(dataset, entries=dataset.entries + extra)
    async with sessions() as session:
        await import_dictionary(session, dataset, "synthetic-test-v1")


async def test_genuine_character_enrichment_is_idempotent_and_does_not_write_lexical_data(sessions):
    await install_catalog(sessions)
    before = await snapshot(sessions, DictionaryEntry)
    async with sessions() as session:
        first = await import_character_enrichment(session, character_dataset(), "genuine-subset-v1")
        second = await import_character_enrichment(
            session, character_dataset(), "genuine-subset-v1"
        )
        assert first == {"records": 2, "replayed": False, "batches": 1}
        assert second["replayed"]
        assert (
            await session.scalar(select(func.count()).select_from(DictionaryCharacterEnrichment))
            == 2
        )
        assert (
            await session.scalar(select(func.count()).select_from(DictionaryEnrichmentImport)) == 1
        )
        await session.rollback()
        with pytest.raises(DictionaryImportError, match="immutable"):
            await import_character_enrichment(
                session, replace(character_dataset(), sha256="a" * 64), "genuine-subset-v1"
            )
    assert await snapshot(sessions, DictionaryEntry) == before
    async with sessions() as session:
        service = DictionaryService(DictionaryRepository(session))
        for text in ("学", "學", "学生", "我", "学学"):
            result = await service.search(DictionaryQuery(q=text))
            for row in result.items:
                detail = await service.get_entry(row.entry_id)
                assert row.short_vi_meaning is None and row.available_languages == ["en"]
                assert "vi" not in detail.meanings and detail.sino_vietnamese is None
                assert detail.character_enrichments
                info = detail.character_enrichments[0]
                assert info.scope == "character"
                assert info.provenance.license == "CC-BY-4.0"
                assert "Kai Hanzi" in info.provenance.attribution
                assert info.provenance.sha256 == character_dataset().sha256
                assert (
                    info.provenance.review_status
                    == "source_declared_manual_not_independently_reviewed"
                )
                if text == "学学":
                    assert info.positions == info.traditional_positions == [0, 1]
                if text == "学生":
                    assert info.matches_entry_pronunciation is None


async def test_homographs_keep_character_scope_and_pronunciation_mismatch_explicit(sessions):
    await install_catalog(sessions)
    # Synthetic annotation tests ambiguity handling; no invented fact is shipped as source data.
    row = CharacterRecord(
        hanzi="行",
        traditional=None,
        pinyin="háng",
        sinoViet="TEST READING",
        meaningVi="TEST CHARACTER GLOSS",
    )
    async with sessions() as session:
        await import_character_enrichment(
            session, CharacterDataset("a" * 64, [row]), "synthetic-v1"
        )
        service = DictionaryService(DictionaryRepository(session))
        results = await service.search(DictionaryQuery(q="行"))
        for suggestion in results.items:
            detail = await service.get_entry(suggestion.entry_id)
            assert detail.sino_vietnamese is None and "vi" not in detail.meanings
            assert detail.character_enrichments[0].matches_entry_pronunciation == (
                detail.primary_pinyin == "háng"
            )


async def test_partial_imports_do_not_infer_missing_traditional_or_accept_ambiguous_alias(sessions):
    data = character_dataset()
    async with sessions() as session:
        await import_character_enrichment(
            session, CharacterDataset(data.sha256, data.records[:1]), "partial-v1"
        )
        await import_character_enrichment(
            session, CharacterDataset("a" * 64, data.records[1:]), "partial-v2"
        )
        assert (
            await session.scalar(select(func.count()).select_from(DictionaryCharacterEnrichment))
            == 2
        )
        await session.rollback()
        conflict = data.records[1].model_copy(update={"traditional": data.records[0].hanzi})
        with pytest.raises(DictionaryImportError, match="Ambiguous"):
            await import_character_enrichment(
                session, CharacterDataset("b" * 64, [conflict]), "conflict-v3"
            )
        assert (
            await session.scalar(select(func.count()).select_from(DictionaryEnrichmentImport)) == 2
        )


async def test_http_contract_is_additive_and_missing_enrichment_stays_empty(sessions):
    await install_catalog(sessions)
    async with sessions() as session:
        await import_character_enrichment(session, character_dataset(), "genuine-subset-v1")
    app = create_app()

    async def database():
        async with sessions() as session:
            yield session

    # Existing dictionary tests cover real authentication and revocation; isolate mapping here.
    app.dependency_overrides[get_session] = database
    app.dependency_overrides[current_user_id] = lambda: "test-identity"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        for query, expected in (("学", True), ("你", False)):
            results = (await client.get("/api/v1/dictionary/search", params={"q": query})).json()
            entry = results["items"][0]
            response = await client.get(f"/api/v1/dictionary/entries/{entry['entry_id']}")
            assert response.status_code == 200
            detail = response.json()
            assert bool(detail["character_enrichments"]) == expected
            assert detail["short_vi_meaning"] is None
            assert detail["sino_vietnamese"] is None and detail["available_languages"] == ["en"]
