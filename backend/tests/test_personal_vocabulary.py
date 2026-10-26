"""Private wordbook tests use isolated PostgreSQL and rollback fixtures."""

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.endpoints.authentication import attempts
from app.dependencies.database import get_session
from app.main import create_app
from app.models import (
    DictionaryEntry,
    DictionaryImport,
    PersonalVocabularyEntry,
    User,
)
from app.services.personal_vocabulary import PersonalVocabularyService
from tests.test_dictionary import fixture_dataset
from tests.test_dictionary_postgres import dictionary_sessions as dictionary_fixture

pytestmark = pytest.mark.postgres
PATH = "/api/v1/me/vocabulary"
dictionary_sessions = dictionary_fixture


@pytest.fixture
async def client(dictionary_sessions):
    app = create_app()

    async def database():
        async with dictionary_sessions() as session:
            yield session

    app.dependency_overrides[get_session] = database
    attempts.clear()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    attempts.clear()


async def register(client, name):
    result = await client.post(
        "/api/v1/auth/register", json={"email": f"{name}@example.com", "password": "test-password"}
    )
    assert result.status_code == 201
    return {"Authorization": "Bearer " + result.json()["access_token"]}


async def save(client, headers, entry):
    result = await client.post(PATH, json={"dictionary_entry_id": str(entry.id)}, headers=headers)
    assert result.status_code == 200
    return result.json()


async def test_legacy_dictionary_ids_are_not_available_in_curated_collection(client):
    headers = await register(client, "legacy-owner")
    entry = fixture_dataset().entries[0]
    assert (await client.get(PATH, headers=headers)).json()["items"] == []
    assert (
        await client.post(PATH, json={"dictionary_entry_id": str(entry.id)}, headers=headers)
    ).status_code == 404
    assert (
        await client.get("/api/v1/dictionary/entries/" + str(entry.id), headers=headers)
    ).status_code == 404
    assert (
        await client.get(
            PATH + "/status", params={"dictionary_entry_id": str(entry.id)}, headers=headers
        )
    ).json()["saved_id"] is None


async def test_concurrent_saves_and_removals_use_real_independent_transactions():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    user_id, entry_id, import_id = uuid4(), uuid4(), uuid4()
    # Unique test-owned rows; cleanup never touches existing fixtures or real users.
    try:
        async with sessions() as session, session.begin():
            session.add(User(id=user_id, display_name="concurrent test"))
            session.add(
                DictionaryImport(
                    id=import_id,
                    source=str(import_id),
                    revision="test",
                    sha256="a" * 64,
                    source_url="https://example.com",
                    license="test",
                    license_url="https://example.com",
                    attribution="synthetic test",
                    changes="test",
                    entry_count=1,
                )
            )
            await session.flush()
            session.add(
                DictionaryEntry(
                    id=entry_id,
                    import_id=import_id,
                    source=str(import_id),
                    simplified="test",
                    traditional="test",
                    pinyin_numbered="test",
                    pinyin="test",
                    english_glosses=["test"],
                )
            )

        async def concurrent_save():
            async with sessions() as session:
                return await PersonalVocabularyService(session).save(user_id, entry_id)

        results = await asyncio.gather(*(concurrent_save() for _ in range(5)))
        assert len({x.id for x in results}) == 1

        async def concurrent_remove():
            async with sessions() as session:
                await PersonalVocabularyService(session).remove(user_id, results[0].id)

        await asyncio.gather(concurrent_remove(), concurrent_remove())
        async with sessions() as session:
            assert await PersonalVocabularyService(session).status(user_id, entry_id) is None
    finally:
        async with sessions() as session, session.begin():
            await session.execute(
                delete(PersonalVocabularyEntry).where(PersonalVocabularyEntry.user_id == user_id)
            )
            await session.execute(delete(User).where(User.id == user_id))
            await session.execute(delete(DictionaryEntry).where(DictionaryEntry.id == entry_id))
            await session.execute(delete(DictionaryImport).where(DictionaryImport.id == import_id))
        await engine.dispose()
