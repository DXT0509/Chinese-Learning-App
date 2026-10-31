import asyncio
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import User
from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.srs import SrsReviewAttempt as Attempt
from app.models.srs_v2 import SrsActiveTime, SrsDailyPlan, SrsMemory
from app.schemas.review_engine import StageSubmission
from app.services.curated_catalog import CuratedCatalog
from app.services.review_engine import ReviewEngine
from app.services.srs import SrsService
from tests.test_curated_vocabulary import approve, install, record
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_fsrs_v2 import ink
from tests.test_review_engine import finish, policy_for, send, start
from tests.test_srs_postgres import NOW, SyntheticTargets, setup_word

pytestmark = pytest.mark.postgres


@pytest.fixture
def v2(monkeypatch):
    pass


async def plan(sessions, owner, now=NOW, request=None, beyond=False):
    async with sessions() as session:
        return (
            await ReviewEngine(session, lambda: now)
            .planner()
            .create(owner, request or uuid4(), beyond)
        )


async def test_26_reviewed_words_then_four_new_saves_are_immediately_due(curated_sessions):
    sessions = curated_sessions
    rows = [
        record(lexical_key=f"{chr(0x4E00 + i)}|xue2", simplified=chr(0x4E00 + i)) for i in range(30)
    ]
    await install(sessions, rows)
    words = [await approve(sessions, row) for row in rows]
    owner = uuid4()
    async with sessions() as session, session.begin():
        session.add(User(id=owner, display_name="New saves regression"))
    for word in words[:26]:
        async with sessions() as session:
            await CuratedCatalog(session).save(owner, word)
    async with sessions() as session, session.begin():
        await session.execute(
            update(Saved)
            .where(Saved.user_id == owner)
            .values(learning_activated=True, next_review_at=NOW + timedelta(days=1))
        )
        # A previous plan has already used more than the former daily intake cap.
        previous_ids = [
            str(i) for i in await session.scalars(select(Saved.id).where(Saved.user_id == owner))
        ]
        session.add(
            SrsDailyPlan(
                id=uuid4(),
                user_id=owner,
                local_day=NOW.date(),
                timezone="Asia/Ho_Chi_Minh",
                target_seconds=1200,
                items=previous_ids,
                new_items=previous_ids,
                completed=previous_ids,
                created_at=NOW,
            )
        )
    empty_key = uuid4()
    async with sessions() as session:
        empty = (
            await SrsService(session, lambda: NOW, SyntheticTargets())
            .planner()
            .create(owner, empty_key)
        )
        assert empty["items"] == []
    new_ids = []
    for word in words[26:]:
        async with sessions() as session:
            new_ids.append(str((await CuratedCatalog(session).save(owner, word)).id))
    async with sessions() as session:
        dashboard = await SrsService(session, lambda: NOW).dashboard(owner)
        assert dashboard["available_count"] == 30
        assert dashboard["due_count"] == dashboard["daily_review"]["overdue_count"] == 4
        assert dashboard["daily_review"]["pending_count"] == 4
        due = await SrsService(session, lambda: NOW).due(owner, 50)
        assert {str(i["saved_id"]) for i in due["items"]} == set(new_ids)
    async with sessions() as session:
        selected = (
            await SrsService(session, lambda: NOW, SyntheticTargets())
            .planner()
            .create(owner, uuid4())
        )
    assert {i["saved_id"] for i in selected["items"]} == set(new_ids)
    for saved_id in new_ids:
        async with sessions() as session:
            initialized = await SrsService(session, lambda: NOW, SyntheticTargets()).initialize(
                owner, saved_id
            )
            assert initialized["mode"] == "DUE" and initialized["grading_available"]


async def test_plan_recovery_ink_validation_sealed_grading_and_atomic_fsrs(
    curated_sessions, v2, monkeypatch
):
    sessions = curated_sessions
    owner, saved_id, word = await setup_word(sessions)
    await policy_for(sessions, word)
    async with sessions() as session:
        original = await session.get(Saved, saved_id)
        due = original.next_review_at
    key = uuid4()
    first = await plan(sessions, owner, request=key)
    assert first["target_seconds"] == 1200
    assert first["items"][0]["saved_id"] == str(saved_id)
    assert (await plan(sessions, owner))["plan_id"] == first["plan_id"]
    attempt = await start(sessions, owner, saved_id)
    async with sessions() as session:
        row = await session.get(Saved, saved_id)
        assert row.next_review_at == due and row.mastery_level == 0
        assert await session.get(SrsMemory, saved_id) is None
        target = (await session.get(Attempt, attempt)).target
        assert target["applicable_stages"] == ["HANZI", "PINYIN"] and not target["accepted_pos"]
    with pytest.raises(HTTPException) as error:
        await send(
            sessions,
            owner,
            attempt,
            StageSubmission(submission_key=uuid4(), stage="HANZI", answer="学"),
        )
    assert error.value.status_code == 422
    body = StageSubmission(submission_key=uuid4(), stage="HANZI", answer="学", handwriting=ink())
    result = await send(sessions, owner, attempt, body)
    assert result == await send(sessions, owner, attempt, body)
    with pytest.raises(HTTPException) as changed_body:
        await send(sessions, owner, attempt, body.model_copy(update={"handwriting": None}))
    assert changed_body.value.status_code == 409
    assert "correct_answer" not in result["feedback"][0] and "simplified" not in result["question"]
    with pytest.raises(HTTPException):
        await finish(sessions, owner, attempt)
    await send(
        sessions,
        owner,
        attempt,
        StageSubmission(submission_key=uuid4(), stage="PINYIN", answer="xue2"),
    )
    result = await finish(sessions, owner, attempt)
    assert result["outcome"] == "PASS" and result["state_after"]["fsrs_review_log"]["rating"] == 3
    assert result == await finish(sessions, owner, attempt)
    async with sessions() as session:
        row = await session.get(Saved, saved_id)
        assert row.schedule_version == row.due_review_count == 1 and row.learning_activated
        assert (await session.get(SrsMemory, saved_id)).card == result["state_after"]["fsrs"]
        stored = await session.get(SrsDailyPlan, first["plan_id"])
        assert stored.completed == [str(saved_id)]


async def test_timing_receipts_and_legacy_attempt_read_only(curated_sessions, monkeypatch):
    sessions = curated_sessions
    owner, saved_id, word = await setup_word(sessions)
    await policy_for(sessions, word)
    legacy = uuid4()
    async with sessions() as session, session.begin():
        session.add(
            Attempt(
                id=legacy,
                user_vocabulary_id=saved_id,
                mode="DUE",
                schedule_version=0,
                target={"applicable_stages": ["HANZI", "PINYIN", "POS"], "gradeable": True},
                state_before={"mastery_level": 0},
                started_at=NOW,
            )
        )
    # Historical snapshots stay intact and available to the reader.
    async with sessions() as session:
        old = await session.get(Attempt, legacy)
        assert "POS" in old.target["applicable_stages"]
    with pytest.raises(HTTPException):
        await send(
            sessions,
            owner,
            legacy,
            StageSubmission(submission_key=uuid4(), stage="HANZI", answer="学", handwriting=ink()),
        )
    await plan(sessions, owner)
    attempt = await start(sessions, owner, saved_id)
    for total, seconds in [(5000, 5), (5000, 6), (10000, 10)]:
        async with sessions() as session, session.begin():
            engine = ReviewEngine(session, lambda seconds=seconds: NOW + timedelta(seconds=seconds))
            row = await engine._locked(owner, attempt)
            assert (await engine.planner().receipt(owner, row, total))["active_ms"] == total
    async with sessions() as session:
        assert (await session.get(SrsActiveTime, attempt)).active_ms == 10000
        metrics = await ReviewEngine(session, lambda: NOW).planner().metrics(owner)
        assert metrics["active_seconds"] == 10
    async with sessions() as session, session.begin():
        engine = ReviewEngine(session, lambda: NOW + timedelta(seconds=11))
        row = await engine._locked(owner, attempt)
        with pytest.raises(HTTPException):
            await engine.planner().receipt(owner, row, 100000)


async def test_new_saves_have_no_daily_intake_cap_and_deferral_preserves_schedules(
    curated_sessions, v2
):
    sessions = curated_sessions
    rows = [
        record(lexical_key=f"{chr(0x4E00 + i)}|xue2", simplified=chr(0x4E00 + i)) for i in range(12)
    ]
    await install(sessions, rows)
    words = [await approve(sessions, row) for row in rows]
    owner = uuid4()
    async with sessions() as session, session.begin():
        session.add(User(id=owner, display_name="Planner fixture"))
    saved_ids = []
    for word in words:
        async with sessions() as session:
            saved_ids.append((await CuratedCatalog(session).save(owner, word)).id)
    async with sessions() as session:
        selected = (
            await ReviewEngine(session, lambda: NOW, SyntheticTargets())
            .planner()
            .create(owner, uuid4())
        )
    assert len(selected["items"]) == 12 and selected["pending_count"] == 12
    assert selected["overdue_count"] == 12
    original_dues = {}
    async with sessions() as session:
        for saved in await session.scalars(select(Saved).where(Saved.user_id == owner)):
            original_dues[saved.id] = saved.next_review_at
            assert not saved.learning_activated
    for item in selected["items"]:
        async with sessions() as session:
            attempt = await SrsService(session, lambda: NOW, SyntheticTargets()).initialize(
                owner, item["saved_id"]
            )
        async with sessions() as session, session.begin():
            engine = ReviewEngine(session, lambda: NOW)
            row = await engine._locked(owner, attempt["attempt_id"])
            await engine.planner().defer(row)
    async with sessions() as session:
        empty = (
            await ReviewEngine(session, lambda: NOW, SyntheticTargets())
            .planner()
            .create(owner, uuid4())
        )
        assert len(empty["items"]) == 12
    async with sessions() as session:
        tomorrow = (
            await ReviewEngine(session, lambda: NOW + timedelta(days=1), SyntheticTargets())
            .planner()
            .create(owner, uuid4())
        )
        assert len(tomorrow["items"]) == 12
    async with sessions() as session:
        for saved in await session.scalars(select(Saved).where(Saved.user_id == owner)):
            assert saved.next_review_at == original_dues[saved.id] and saved.due_review_count == 0


async def test_v2_concurrent_first_answers_and_finalization(v2):
    url = os.environ.get("SRS_V2_CONCURRENCY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Requires isolated migrated v2 concurrency database")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        owner, saved, word = await setup_word(sessions)
        await policy_for(sessions, word)
        await plan(sessions, owner)
        first, second = await asyncio.gather(
            start(sessions, owner, saved), start(sessions, owner, saved)
        )

        async def answer(attempt):
            body = StageSubmission(
                submission_key=uuid4(), stage="HANZI", answer="错", handwriting=ink("错")
            )
            results = await asyncio.gather(
                send(sessions, owner, attempt, body), send(sessions, owner, attempt, body)
            )
            assert results[0] == results[1]
            await send(
                sessions,
                owner,
                attempt,
                StageSubmission(
                    submission_key=uuid4(), stage="HANZI", answer="学", handwriting=ink()
                ),
            )
            await send(
                sessions,
                owner,
                attempt,
                StageSubmission(submission_key=uuid4(), stage="PINYIN", answer="xue2"),
            )

        await asyncio.gather(answer(first), answer(second))
        results = await asyncio.gather(
            finish(sessions, owner, first),
            finish(sessions, owner, first),
            finish(sessions, owner, second),
        )
        assert all(r["outcome"] == "FAIL" for r in results)
        assert results[0] == results[1]
        assert sum(r["scheduling_applied"] for r in (results[0], results[2])) == 1
        async with sessions() as session:
            saved_row = await session.get(Saved, saved)
            assert (
                saved_row.schedule_version
                == saved_row.due_review_count
                == saved_row.failure_count
                == 1
            )
            assert (await session.get(SrsMemory, saved)).card["last_review"] == NOW.isoformat()
    finally:
        await engine.dispose()


async def test_active_time_splits_midnight_and_deferral_does_not_schedule(curated_sessions, v2):
    sessions = curated_sessions
    owner, saved_id, word = await setup_word(sessions)
    await policy_for(sessions, word)
    midnight = NOW.replace(hour=16, minute=59, second=55)  # 23:59:55 Vietnam
    await plan(sessions, owner, now=midnight)
    attempt = await start(sessions, owner, saved_id, now=midnight)
    for seconds, total in [(4, 4000), (9, 9000)]:
        async with sessions() as session, session.begin():
            engine = ReviewEngine(
                session, lambda seconds=seconds: midnight + timedelta(seconds=seconds)
            )
            row = await engine._locked(owner, attempt)
            await engine.planner().receipt(owner, row, total)
    async with sessions() as session:
        today = await ReviewEngine(session, lambda: midnight).planner().metrics(owner)
        tomorrow = (
            await ReviewEngine(session, lambda: midnight + timedelta(seconds=10))
            .planner()
            .metrics(owner)
        )
        assert today["active_seconds"] == 4 and tomorrow["active_seconds"] == 5
        assert (await session.get(Saved, saved_id)).due_review_count == 0
