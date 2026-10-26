"""Phase 4 validation and authenticated behavior against an isolated PostgreSQL DB."""

import json
import os
from uuid import uuid4, uuid5

import httpx
import pytest
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.endpoints.authentication import attempts
from app.dependencies.database import get_session
from app.main import create_app
from app.models.curated_vocabulary import CuratedUserVocabulary, CuratedVocabulary
from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_import import NAMESPACE, approve_record, import_records, load_records


def record(**changes):
    return CuratedRecord.model_validate(
        {
            "schema_version": 1,
            "lexical_key": "学|xue2",
            "simplified": "学",
            "pinyin": "xué",
            "pinyin_numbered": "xue2",
            "learning_level": 0,
            "content_version": 1,
            "vietnamese_meanings": ["học"],
            **changes,
        }
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"simplified": "學"},
        {"traditional": "學"},
        {"learning_level": -1},
        {"learning_level": 6},
        {"learning_level": True},
        {"vietnamese_meanings": []},
        {"vietnamese_meanings": [" "]},
        {"vietnamese_meanings": ["học", "học"]},
        {"vietnamese_meanings": ["học\u0000"]},
        {"pinyin": "xuě"},
        {"pinyin_numbered": "xue"},
        {"pinyin_numbered": "Xue2"},
        {"review_status": "HUMAN_APPROVED"},
        {"schema_version": 2},
        {"classification_standard": "HSK"},
        {"lexical_key": "unrelated"},
        {"examples": [{"simplified": "學生", "pinyin": "xué shēng", "vietnamese": "học sinh"}]},
    ],
)
def test_reject_invalid_or_unreviewed_claims(changes):
    with pytest.raises((ValidationError, ValueError)):
        record(**changes)


def test_nfc_and_lexical_readings(tmp_path):
    first = record(pinyin="xue\u0301", vietnamese_meanings=["ho\u0323c"])
    assert first.pinyin == "xué" and first.vietnamese_meanings == ["học"]
    path = tmp_path / "words.jsonl"
    path.write_text(json.dumps(first.model_dump(), ensure_ascii=False) + "\n", encoding="utf-8")
    assert len(load_records(path)[1]) == 1
    path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_records(path)
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        load_records(path)
    assert record(lexical_key="女|nü3", simplified="女", pinyin="nǚ", pinyin_numbered="nü3")


@pytest.fixture
async def curated_sessions():
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


@pytest.fixture
async def curated_client(curated_sessions):
    app = create_app()

    async def database():
        async with curated_sessions() as session:
            yield session

    app.dependency_overrides[get_session] = database
    attempts.clear()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    attempts.clear()


async def register(client, name):
    response = await client.post(
        "/api/v1/auth/register", json={"email": f"{name}@example.com", "password": "test-password"}
    )
    assert response.status_code == 201
    return {"Authorization": "Bearer " + response.json()["access_token"]}


async def install(sessions, rows=None, batch="batch1", checksum="a" * 64):
    rows = rows or [record()]
    async with sessions() as session:
        result = await import_records(session, batch, checksum, rows)
    return result


async def approve(sessions, row=None):
    identifier = uuid5(NAMESPACE, (row or record()).lexical_key)
    async with sessions() as session:
        word = await session.get(CuratedVocabulary, identifier)
        checksum = word.checksum
        await session.rollback()
        await approve_record(session, identifier, checksum, "Test human reviewer")
    return identifier


@pytest.mark.postgres
async def test_import_approval_api_ownership_and_unified_mastery(curated_sessions, curated_client):
    client, sessions = curated_client, curated_sessions
    path = "/api/v1/me/vocabulary"
    assert (await client.get(path)).status_code == 401
    a, b = await register(client, "curated-owner"), await register(client, "curated-other")
    assert (await client.get("/api/v1/dictionary/search", params={"q": "学"}, headers=a)).json()[
        "items"
    ] == []
    await install(sessions)
    assert (await install(sessions))["unchanged_batch"]
    identifier = uuid5(NAMESPACE, record().lexical_key)
    body = {"dictionary_entry_id": str(identifier)}
    assert (await client.post(path, json=body, headers=a)).status_code == 404
    async with sessions() as session:
        word = await session.get(CuratedVocabulary, identifier)
        assert word.review_status == "GENERATED_UNREVIEWED"
        await session.rollback()
        with pytest.raises(ValueError):
            await approve_record(session, identifier, "wrong-checksum", "Human")
    await approve(sessions)
    result = (await client.get("/api/v1/dictionary/search", params={"q": "học"}, headers=a)).json()
    assert result["items"][0]["short_vi_meaning"] == "học"
    assert "traditional" not in result["items"][0]
    detail = (await client.get(f"/api/v1/dictionary/entries/{identifier}", headers=a)).json()
    assert detail["review_status"] == "HUMAN_APPROVED"
    assert detail["meanings"]["vi"][0]["gloss"] == "học"
    saved = (await client.post(path, json=body, headers=a)).json()
    assert saved["mastery_level"] == 0 and saved["next_review_at"] is None
    assert (await client.post(path, json=body, headers=a)).json() == saved
    saved_path = path + "/" + saved["id"]
    assert (await client.get(saved_path, headers=b)).status_code == 404
    assert (await client.delete(saved_path, headers=b)).status_code == 204
    assert (await client.get(path, headers=b)).json()["total"] == 0
    for params in ({"cursor": "bad"}, {"cursor": "!!!!"}, {"limit": 51}):
        assert (await client.get(path, params=params, headers=a)).status_code == 422
    assert (
        await client.post(path, json={**body, "user_id": str(uuid4())}, headers=a)
    ).status_code == 422
    async with sessions() as session, session.begin():
        await session.execute(update(CuratedUserVocabulary).values(mastery_level=3))
    await client.delete(saved_path, headers=a)
    assert (await client.get(path, headers=a)).json()["total"] == 0
    readded = (await client.post(path, json=body, headers=a)).json()
    assert readded["id"] == saved["id"] and readded["mastery_level"] == 3
    status = await client.get(path + "/status", params=body, headers=a)
    assert status.json()["saved_id"] == saved["id"]
    # A new revision is staged again, without losing the existing user's mastery.
    await install(
        sessions, [record(content_version=2, vietnamese_meanings=["học tập"])], "batch2", "b" * 64
    )
    assert (
        await client.get(f"/api/v1/dictionary/entries/{identifier}", headers=a)
    ).status_code == 404
    assert (await client.get(saved_path, headers=a)).json()["active"] is False
    await approve(sessions)
    assert (await client.post(path, json=body, headers=a)).json()["mastery_level"] == 3


@pytest.mark.postgres
async def test_homographs_revisions_and_database_constraints(curated_sessions):
    rows = [
        record(lexical_key=f"行|{p}", simplified="行", pinyin=t, pinyin_numbered=p)
        for p, t in [("hang2", "háng"), ("xing2", "xíng")]
    ]
    await install(curated_sessions, rows)
    async with curated_sessions() as session:
        words = list(await session.scalars(select(CuratedVocabulary)))
        assert len(words) == 2 and len({w.id for w in words}) == 2
    with pytest.raises(ValueError, match="different bytes"):
        await install(curated_sessions, rows, checksum="b" * 64)
    with pytest.raises(ValueError, match="increasing"):
        await install(
            curated_sessions,
            [r.model_copy(update={"vietnamese_meanings": ["changed"]}) for r in rows],
            "batch2",
            "b" * 64,
        )
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(update(CuratedVocabulary).values(learning_level=6))
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(
                    update(CuratedVocabulary).values(review_status="AUTO_APPROVED")
                )


@pytest.mark.postgres
async def test_collection_integrity_guards(curated_sessions, curated_client):
    from uuid import UUID

    from sqlalchemy import insert

    headers = await register(curated_client, "integrity")
    owner = UUID((await curated_client.get("/api/v1/auth/me", headers=headers)).json()["id"])
    await install(curated_sessions)
    identifier = uuid5(NAMESPACE, record().lexical_key)
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(
                    insert(CuratedUserVocabulary).values(
                        id=uuid4(), user_id=owner, vocabulary_id=identifier
                    )
                )
    await approve(curated_sessions)
    for changes in ({"user_id": uuid4()}, {"vocabulary_id": uuid4()}, {"mastery_level": 2}):
        async with curated_sessions() as session:
            with pytest.raises(IntegrityError):
                async with session.begin():
                    await session.execute(
                        insert(CuratedUserVocabulary).values(
                            **{
                                "id": uuid4(),
                                "user_id": owner,
                                "vocabulary_id": identifier,
                                **changes,
                            }
                        )
                    )
    async with curated_sessions() as session, session.begin():
        session.add(CuratedUserVocabulary(user_id=owner, vocabulary_id=identifier))
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(
                    insert(CuratedUserVocabulary).values(
                        id=uuid4(), user_id=owner, vocabulary_id=identifier
                    )
                )
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(update(CuratedUserVocabulary).values(mastery_level=6))
