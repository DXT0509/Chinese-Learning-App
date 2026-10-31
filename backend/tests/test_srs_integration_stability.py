"""Creation replay and display contracts; fixtures are synthetic and isolated only."""

import asyncio
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import User
from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.services.curated_catalog import CuratedCatalog
from app.services.review_engine import TTL, ReviewEngine
from app.services.srs import SrsService
from tests.test_curated_vocabulary import approve, install, record, register
from tests.test_curated_vocabulary import curated_client as curated_client  # noqa: PLC0414
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_review_engine import finish, policy_for, send, submission
from tests.test_srs_postgres import NOW, setup_word

pytestmark = pytest.mark.postgres


async def create(sessions, owner, saved, key, now=NOW):
    async with sessions() as session:
        return await SrsService(session, lambda: now).initialize(owner, saved, key)


async def test_creation_replay_before_after_commit_expiry_and_completion(curated_sessions):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word, pos=False)
    key = uuid4()
    # Simulate loss before commit: force the transaction to roll back after insertion.
    async with sessions() as session:
        from sqlalchemy import event

        def reject_commit(session):
            raise RuntimeError("Synthetic interrupted commit")

        event.listen(session.sync_session, "before_commit", reject_commit)
        with pytest.raises(RuntimeError, match="Synthetic"):
            await SrsService(session, lambda: NOW).initialize(owner, saved, key)
    async with sessions() as session:
        assert await session.get(Attempt, key) is None
    original = await create(sessions, owner, saved, key)
    # Lost response after commit: reissue the exact body, even after the attempt TTL.
    assert original["attempt_id"] == key
    assert await create(sessions, owner, saved, key, NOW + TTL) == original
    async with sessions() as session:
        with pytest.raises(HTTPException) as error:
            await ReviewEngine(session, lambda: NOW + TTL).question(owner, key)
        assert error.value.status_code == 410
    for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
        await send(sessions, owner, key, submission(stage, answer))
    result = await finish(sessions, owner, key)
    assert await create(sessions, owner, saved, key, NOW + timedelta(days=1)) == original
    assert result["previous_mastery_level"] == 0
    assert result["resulting_mastery_level"] == result["state_after"]["mastery_level"]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Attempt)) == 1
        row = await session.get(Saved, saved)
        assert row.due_review_count == row.schedule_version == 1


async def test_http_keys_are_owned_bound_strict_and_legacy_start_still_works(
    curated_client, curated_sessions
):
    client, sessions = curated_client, curated_sessions
    owner = await register(client, "replay-owner")
    other = await register(client, "replay-other")
    await install(sessions)
    word = await approve(sessions)
    saved = (
        await client.post(
            "/api/v1/me/vocabulary", headers=owner, json={"dictionary_entry_id": str(word)}
        )
    ).json()["id"]
    foreign = (
        await client.post(
            "/api/v1/me/vocabulary", headers=other, json={"dictionary_entry_id": str(word)}
        )
    ).json()["id"]
    await policy_for(sessions, word, pos=False)
    await client.post(
        "/api/v1/me/srs/daily-plans", headers=owner, json={"request_id": str(uuid4())}
    )
    base = "/api/v1/me/srs/sessions"
    body = {"saved_id": saved, "request_id": str(uuid4())}
    assert (await client.post(base, json=body)).status_code == 401
    assert (await client.post(base, headers=other, json=body)).status_code == 404
    first = await client.post(base, headers=owner, json=body)
    assert first.status_code == 201 and first.headers["cache-control"] == "no-store"
    assert (await client.post(base, headers=owner, json=body)).json() == first.json()
    await client.post(
        "/api/v1/me/srs/daily-plans", headers=other, json={"request_id": str(uuid4())}
    )
    conflict = await client.post(base, headers=other, json=body | {"saved_id": foreign})
    assert conflict.status_code == 409 and "attempt_id" not in conflict.json()
    invalid = await client.post(base, headers=owner, json=body | {"request_id": "not-uuid"})
    assert invalid.status_code == 422
    legacy = await client.post(base, headers=owner, json={"saved_id": saved})
    assert legacy.status_code == 201
    assert legacy.json()["attempt_id"] != first.json()["attempt_id"]
    dashboard = await client.get("/api/v1/me/srs/dashboard", headers=owner)
    assert dashboard.json()["mastery_distribution"] == [
        {"mastery_level": level, "count": int(level == 0)} for level in range(6)
    ]
    assert dashboard.headers["cache-control"] == "no-store"


async def test_mastery_distribution_same_availability_scope_and_zero_buckets(curated_sessions):
    sessions = curated_sessions
    owner = uuid4()
    async with sessions() as session, session.begin():
        session.add(User(id=owner, display_name="Synthetic histogram learner"))
    async with sessions() as session:
        empty = await SrsService(session, lambda: NOW).dashboard(owner)
        assert empty["mastery_distribution"] == [{"mastery_level": n, "count": 0} for n in range(6)]
    forms = [
        ("一", "yī", "yi1"),
        ("二", "èr", "er4"),
        ("三", "sān", "san1"),
        ("四", "sì", "si4"),
        ("五", "wǔ", "wu3"),
        ("六", "liù", "liu4"),
        ("七", "qī", "qi1"),
        ("八", "bā", "ba1"),
    ]
    rows = [
        record(
            lexical_key=f"{hanzi}|{numbered}",
            simplified=hanzi,
            pinyin=marked,
            pinyin_numbered=numbered,
        )
        for hanzi, marked, numbered in forms
    ]
    await install(sessions, rows=rows)
    ids = []
    for n, row in enumerate(rows):
        word = await approve(sessions, row)
        async with sessions() as session:
            saved = await CuratedCatalog(session).save(owner, word)
            ids.append(saved.id)
        async with sessions() as session, session.begin():
            level = min(n, 5)
            await session.execute(
                update(Saved)
                .where(Saved.id == saved.id)
                .values(
                    learning_activated=True,
                    mastery_level=level,
                    phase="REVIEW" if level else "LEARNING",
                    next_review_at=NOW + timedelta(days=1) if n % 2 else NOW,
                )
            )
            if n == 6:
                await session.execute(
                    update(Word).where(Word.id == word).values(review_status="NEEDS_REVIEW")
                )
            if n == 7:
                await session.execute(
                    update(Saved).where(Saved.id == saved.id).values(is_active=False)
                )
    # Another owner's progress must never enter any bucket.
    other = uuid4()
    async with sessions() as session, session.begin():
        session.add(User(id=other, display_name="Other synthetic learner"))
        session.add(
            Saved(
                user_id=other,
                vocabulary_id=await session.scalar(
                    select(Saved.vocabulary_id).where(Saved.id == ids[0])
                ),
            )
        )
    async with sessions() as session:
        dashboard = await SrsService(session, lambda: NOW).dashboard(owner)
        assert dashboard["available_count"] == 6
        assert dashboard["due_count"] == 3 and dashboard["suspended_count"] == 1
        assert dashboard["mastery_distribution"] == [
            {"mastery_level": n, "count": 1} for n in range(6)
        ]


async def test_final_mastery_uses_pinned_history_not_current_progress(curated_sessions):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word, pos=False)
    async with sessions() as session, session.begin():
        await session.execute(
            update(Saved)
            .where(Saved.id == saved)
            .values(mastery_level=4, phase="REVIEW", next_review_at=NOW)
        )
    key = uuid4()
    await create(sessions, owner, saved, key)
    for stage, answer in (("HANZI", "错"), ("PINYIN", "xue2")):
        await send(sessions, owner, key, submission(stage, answer))
    result = await finish(sessions, owner, key)
    assert (result["previous_mastery_level"], result["resulting_mastery_level"]) == (4, 3)
    async with sessions() as session, session.begin():
        await session.execute(update(Saved).where(Saved.id == saved).values(mastery_level=2))
    assert await finish(sessions, owner, key) == result


async def test_creation_races_on_independent_connections():
    url = os.environ.get("SRS_CREATION_CONCURRENCY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Requires an isolated migrated creation-concurrency database")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        owner, saved, word = await setup_word(sessions)
        await policy_for(sessions, word, pos=False)
        key = uuid4()
        results = await asyncio.gather(*(create(sessions, owner, saved, key) for _ in range(6)))
        assert all(result == results[0] for result in results)
        async with sessions() as session:
            assert await session.scalar(select(func.count()).select_from(Attempt)) == 1
            row = await session.get(Saved, saved)
            assert row.due_review_count == row.schedule_version == 0
        # Different owners simultaneously colliding on one key get a generic conflict.
        other = uuid4()
        async with sessions() as session, session.begin():
            session.add(User(id=other, display_name="Synthetic collision learner"))
        async with sessions() as session:
            other_saved = await CuratedCatalog(session).save(other, word)
        collision = uuid4()
        results = await asyncio.gather(
            create(sessions, owner, saved, collision),
            create(sessions, other, other_saved.id, collision),
            return_exceptions=True,
        )
        assert sum(isinstance(result, dict) for result in results) == 1
        rejected = next(result for result in results if isinstance(result, Exception))
        assert isinstance(rejected, HTTPException) and rejected.status_code == 409
    finally:
        await engine.dispose()
