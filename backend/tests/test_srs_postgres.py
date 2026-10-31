"""SRS integration uses only explicitly selected isolated test databases."""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import User
from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.services.curated_catalog import CuratedCatalog
from app.services.srs import SrsService
from app.services.srs_contract import (
    ReviewTarget,
    Stage,
    StageEvidence,
    StageVerdict,
    ValidatedReview,
)
from tests.test_curated_vocabulary import (
    approve,
    install,
    register,
)
from tests.test_curated_vocabulary import (
    curated_client as curated_client,  # noqa: PLC0414 -- pytest fixture re-export
)
from tests.test_curated_vocabulary import (
    curated_sessions as curated_sessions,  # noqa: PLC0414 -- pytest fixture re-export
)

pytestmark = pytest.mark.postgres
NOW = datetime(2030, 1, 1, tzinfo=UTC)


class SyntheticTargets:
    """Fixture-only server policy. No production grading implementation."""

    async def resolve(self, session, word):
        return ReviewTarget(
            word.id,
            word.lexical_key,
            word.content_version,
            word.checksum,
            policy_version="fixture",
            sense_key="fixture-only",
            vietnamese_prompt="hoc",
            accepted_simplified=(word.simplified,),
            accepted_pinyin_numbered=(word.pinyin_numbered,),
        )


def validated(attempt_id, correct=True):
    return ValidatedReview(
        attempt_id,
        "synthetic-v1",
        tuple(
            StageEvidence(stage, StageVerdict.CORRECT if correct else StageVerdict.INCORRECT)
            for stage in (Stage.HANZI, Stage.PINYIN)
        ),
    )


async def setup_word(sessions):
    await install(sessions)
    word = await approve(sessions)
    owner = uuid4()
    async with sessions() as session, session.begin():
        session.add(User(id=owner, display_name="SRS test"))
    async with sessions() as session:
        saved = await CuratedCatalog(session).save(owner, word)
    async with sessions() as session, session.begin():
        await session.execute(
            update(Saved).where(Saved.id == saved.id).values(learning_activated=True)
        )
    return owner, saved.id, word


async def initialize(sessions, owner, saved_id, now=NOW):
    async with sessions() as session:
        return await SrsService(session, lambda: now, SyntheticTargets()).initialize(
            owner, saved_id
        )


async def complete(sessions, owner, attempt_id, now=NOW, correct=True):
    async with sessions() as session:
        return await SrsService(session, lambda: now).complete_validated(
            owner, validated(attempt_id, correct)
        )


async def test_atomic_idempotent_due_generation_and_rollback(curated_sessions):
    sessions = curated_sessions
    owner, saved_id, _word = await setup_word(sessions)
    first = await initialize(sessions, owner, saved_id)
    stale = await initialize(sessions, owner, saved_id)
    other_owner = uuid4()
    with pytest.raises(HTTPException) as error:
        await complete(sessions, other_owner, first["attempt_id"])
    assert error.value.status_code == 404
    state = await complete(sessions, owner, first["attempt_id"])
    assert state["phase_step"] == 1
    assert await complete(sessions, owner, first["attempt_id"]) == state
    with pytest.raises(HTTPException) as error:
        await complete(sessions, owner, first["attempt_id"], correct=False)
    assert error.value.status_code == 409
    await complete(sessions, owner, stale["attempt_id"])
    async with sessions() as session:
        saved = await session.get(Saved, saved_id)
        assert saved.due_review_count == 1 and saved.practice_count == 1
        assert saved.schedule_version == 1
        due_at = saved.next_review_at
    # Starting early remains practice even if completion occurs after due time.
    early = await initialize(sessions, owner, saved_id, NOW + timedelta(minutes=1))
    await complete(sessions, owner, early["attempt_id"], NOW + timedelta(days=3), False)
    async with sessions() as session:
        saved = await session.get(Saved, saved_id)
        assert saved.next_review_at == due_at and saved.mastery_level == 0
        assert saved.failure_count == 0 and saved.practice_count == 2
    # Force a DB failure after updating progress; both progress and attempt roll back.
    due = await initialize(sessions, owner, saved_id, due_at)
    async with sessions() as session:
        from sqlalchemy import event

        def reject_flush(session, flush_context, instances):
            for row in session.dirty:
                if isinstance(row, Attempt):
                    row.mode = "INVALID"

        event.listen(session.sync_session, "before_flush", reject_flush)
        with pytest.raises(IntegrityError):
            await SrsService(session, lambda: due_at).complete_validated(
                owner, validated(due["attempt_id"])
            )
    async with sessions() as session:
        saved = await session.get(Saved, saved_id)
        attempt = await session.get(Attempt, due["attempt_id"])
        assert saved.phase_step == 1 and saved.due_review_count == 1
        assert attempt.completed_at is None
    assert (await complete(sessions, owner, due["attempt_id"], due_at))["phase_step"] == 2
    for statement in (
        update(Attempt).where(Attempt.id == due["attempt_id"]).values(outcome="FAIL"),
        delete(Attempt).where(Attempt.id == due["attempt_id"]),
    ):
        async with sessions() as session:
            with pytest.raises(IntegrityError):
                async with session.begin():
                    await session.execute(statement)


async def test_removal_resave_and_publication_suspend_without_history_loss(curated_sessions):
    sessions = curated_sessions
    owner, saved_id, word = await setup_word(sessions)
    started = await initialize(sessions, owner, saved_id)
    async with sessions() as session:
        original = await CuratedCatalog(session).save(owner, word)
    async with sessions() as session:
        await CuratedCatalog(session).remove(owner, saved_id)
    with pytest.raises(HTTPException):
        await initialize(sessions, owner, saved_id)
    async with sessions() as session:
        restored = await CuratedCatalog(session).save(owner, word)
    assert restored.id == original.id and restored.next_review_at == original.next_review_at
    await complete(sessions, owner, started["attempt_id"])
    async with sessions() as session:
        saved = await session.get(Saved, saved_id)
        assert saved.due_review_count == 0 and saved.practice_count == 1
    pending = await initialize(sessions, owner, saved_id)
    async with sessions() as session, session.begin():
        await session.execute(
            update(Word).where(Word.id == word).values(review_status="NEEDS_REVIEW")
        )
    async with sessions() as session:
        dash = await SrsService(session, lambda: NOW).dashboard(owner)
        assert dash["due_count"] == 0 and dash["suspended_count"] == 1
    with pytest.raises(HTTPException):
        await complete(sessions, owner, pending["attempt_id"])
    async with sessions() as session:
        assert await session.get(Attempt, started["attempt_id"])
        assert (await SrsService(session).progress(owner, saved_id))["available"] is False


async def test_api_auth_isolation_no_result_writer_and_grading_gate(
    curated_sessions, curated_client
):
    client, sessions = curated_client, curated_sessions
    owner = await register(client, "srs-owner")
    other = await register(client, "srs-other")
    await install(sessions)
    word = await approve(sessions)
    saved = (
        await client.post(
            "/api/v1/me/vocabulary", headers=owner, json={"dictionary_entry_id": str(word)}
        )
    ).json()
    base = "/api/v1/me/srs"
    for suffix in ("/dashboard", "/due", "/progress/" + saved["id"]):
        assert (await client.get(base + suffix)).status_code == 401
    dash = (await client.get(base + "/dashboard", headers=owner)).json()
    assert (
        dash["due_count"] == 1
        and dash["daily_review"]["pending_count"] == 1
        and not dash["grading_available"]
    )
    assert (await client.get(base + "/due", headers=other)).json()["items"] == []
    assert (await client.get(base + "/progress/" + saved["id"], headers=other)).status_code == 404
    assert (await client.get(base + "/due?limit=101", headers=owner)).status_code == 422
    assert (
        await client.post(base + "/sessions", headers=other, json={"saved_id": saved["id"]})
    ).status_code == 404
    assert (
        await client.post(
            base + "/sessions", headers=owner, json={"saved_id": saved["id"], "correct": True}
        )
    ).status_code == 422
    result = await client.post(base + "/sessions", headers=owner, json={"saved_id": saved["id"]})
    assert result.status_code == 409


async def test_concurrent_attempts_use_independent_connections():
    """Committed fixtures retained in the isolated DB; no shared-connection fake race."""
    url = os.environ.get("SRS_CONCURRENCY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SRS_CONCURRENCY_TEST_DATABASE_URL to an isolated migrated DB")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        owner, saved_id, _word = await setup_word(sessions)
        a = await initialize(sessions, owner, saved_id)
        b = await initialize(sessions, owner, saved_id)
        await asyncio.gather(
            complete(sessions, owner, a["attempt_id"]),
            complete(sessions, owner, b["attempt_id"]),
            complete(sessions, owner, a["attempt_id"]),
        )
        async with sessions() as session:
            saved = await session.get(Saved, saved_id)
            assert saved.phase_step == 1 and saved.due_review_count == 1
            assert saved.practice_count == 1
            attempts = list(
                await session.scalars(select(Attempt).where(Attempt.user_vocabulary_id == saved_id))
            )
            assert len(attempts) == 2 and sum(a.scheduling_applied for a in attempts) == 1
    finally:
        await engine.dispose()
