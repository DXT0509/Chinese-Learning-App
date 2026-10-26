"""Dictionary behavior against PostgreSQL, inside rollback-only outer transactions."""

import os
from dataclasses import replace
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.endpoints.authentication import attempts
from app.dependencies.database import get_session
from app.main import create_app
from app.models import DictionaryEntry, DictionaryImport, UserVocabulary, Vocabulary
from app.repositories.dictionary import DictionaryRepository
from app.schemas.dictionary import DictionaryQuery
from app.services.cedict import DictionaryImportError, parse_row
from app.services.dictionary import DictionaryService
from app.services.dictionary_import import import_dictionary
from tests.test_dictionary import fixture_dataset

pytestmark = pytest.mark.postgres


@pytest.fixture
async def dictionary_sessions():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            sessions = async_sessionmaker(
                connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            async with sessions() as session:
                await import_dictionary(session, fixture_dataset(), "synthetic-test-v1")
            yield sessions
            await transaction.rollback()
    finally:
        await engine.dispose()


async def search(sessions, q, **kwargs):
    async with sessions() as session:
        return await DictionaryService(DictionaryRepository(session)).search(
            DictionaryQuery(q=q, **kwargs)
        )


@pytest.mark.parametrize(
    "q,expected",
    [
        ("你", ["你", "你们", "你好"]),
        ("你好", ["你好"]),
        ("学", ["学", "学校", "学生"]),
        ("學生", ["学生"]),
        ("學", ["学", "学校", "学生"]),
        ("𠀀", ["𠀀"]),
        ("不存在", []),
        ("%", []),
        ("_", []),
        ("' OR 1=1 --", []),
    ],
)
async def test_exact_prefix_ranking_unicode_and_no_sql_wildcards(dictionary_sessions, q, expected):
    result = await search(dictionary_sessions, q)
    assert [item.simplified for item in result.items] == expected


async def test_pagination_and_multiple_readings(dictionary_sessions):
    first = await search(dictionary_sessions, "学", limit=1)
    second = await search(dictionary_sessions, "学", limit=1, offset=first.next_offset)
    third = await search(dictionary_sessions, "学", limit=1, offset=second.next_offset)
    assert [first.items[0].simplified, second.items[0].simplified, third.items[0].simplified] == [
        "学",
        "学校",
        "学生",
    ]
    assert third.next_offset is None
    readings = await search(dictionary_sessions, "行")
    assert {item.primary_pinyin for item in readings.items} == {"háng", "xíng"}
    assert len({item.entry_id for item in readings.items}) == 2


async def test_idempotency_revision_immutability_and_no_curriculum_writes(dictionary_sessions):
    async with dictionary_sessions() as session:
        counts = [
            await session.scalar(select(func.count()).select_from(model))
            for model in (Vocabulary, UserVocabulary)
        ]
        await session.rollback()
        summary = await import_dictionary(session, fixture_dataset(), "synthetic-test-v1")
        assert summary["replayed"] and summary["batches"] == 0
        assert await session.scalar(select(func.count()).select_from(DictionaryEntry)) == 10
        assert await session.scalar(select(func.count()).select_from(DictionaryImport)) == 1
        assert counts == [
            await session.scalar(select(func.count()).select_from(model))
            for model in (Vocabulary, UserVocabulary)
        ]
        await session.rollback()
        with pytest.raises(DictionaryImportError, match="immutable"):
            await import_dictionary(
                session, replace(fixture_dataset(), sha256="f" * 64), "synthetic-test-v1"
            )


async def test_new_revision_updates_senses_preserves_ids_and_retires_missing(dictionary_sessions):
    original = fixture_dataset()
    updated = replace(original.entries[0], english_glosses=["updated test gloss"])
    changed = replace(original, sha256="a" * 64, entries=[updated])
    async with dictionary_sessions() as session:
        await import_dictionary(session, changed, "synthetic-test-v2")
    result = await search(dictionary_sessions, "你")
    assert [item.entry_id for item in result.items] == [original.entries[0].id]
    assert result.items[0].source_revision == "synthetic-test-v2"
    async with dictionary_sessions() as session:
        service = DictionaryService(DictionaryRepository(session))
        detail = await service.get_entry(original.entries[0].id)
        assert detail.meanings["en"][0].gloss == "updated test gloss"
        assert (await service.get_entry(original.entries[1].id)).active is False
        await session.rollback()
        with pytest.raises(DictionaryImportError, match="superseded"):
            await import_dictionary(session, original, "synthetic-test-v1")


async def test_real_authenticated_api_detail_and_revocation(dictionary_sessions):
    app = create_app()

    async def database():
        async with dictionary_sessions() as session:
            yield session

    app.dependency_overrides[get_session] = database
    attempts.clear()
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            registered = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "dictionary@example.com",
                    "password": "test-password-123",
                },
            )
            assert registered.status_code == 201
            pair = registered.json()
            headers = {"Authorization": f"Bearer {pair['access_token']}"}
            result = await client.get(
                "/api/v1/dictionary/search", params={"q": "你"}, headers=headers
            )
            assert result.status_code == 200
            # Retired provider rows remain stored until explicit maintenance, but
            # public lookup now reads only the curated catalog.
            assert result.json()["items"] == []
            path = f"/api/v1/dictionary/entries/{fixture_dataset().entries[0].id}"
            assert (await client.get(path, headers=headers)).status_code == 404
            missing = await client.get(f"/api/v1/dictionary/entries/{uuid4()}", headers=headers)
            assert missing.status_code == 404
            assert (
                await client.post(
                    "/api/v1/auth/logout",
                    json={
                        "refresh_token": pair["refresh_token"],
                    },
                )
            ).status_code == 204
            assert (await client.get(path, headers=headers)).status_code == 401
    finally:
        attempts.clear()


async def test_failed_later_batch_rolls_back_entire_snapshot(dictionary_sessions):
    original = fixture_dataset()
    entries = [parse_row(f"测试{i} 测试{i} [ce4 shi4] /synthetic test/") for i in range(501)]
    entries[-1] = replace(entries[-1], english_glosses=[])
    failed = replace(original, entries=entries, sha256="c" * 64)
    async with dictionary_sessions() as session:
        with pytest.raises(IntegrityError):
            await import_dictionary(session, failed, "synthetic-failed-v2")
        assert await session.scalar(select(func.count()).select_from(DictionaryImport)) == 1
        assert await session.scalar(select(func.count()).select_from(DictionaryEntry)) == 10
    result = await search(dictionary_sessions, "你")
    assert len(result.items) == 3
    assert {item.source_revision for item in result.items} == {"synthetic-test-v1"}
