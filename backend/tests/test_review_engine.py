"""Persisted evaluator and authenticated HTTP checks on explicitly isolated PostgreSQL."""

import asyncio
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.models.srs import SrsTargetPolicy
from app.schemas.review_engine import StageSubmission
from app.services.review_engine import TTL, ReviewEngine
from app.services.review_targets import ReviewedPolicy, ReviewedTargets
from app.services.srs import SrsService
from tests.test_curated_vocabulary import (
    curated_client as curated_client,  # noqa: PLC0414 -- pytest fixture re-export
)
from tests.test_curated_vocabulary import (
    curated_sessions as curated_sessions,  # noqa: PLC0414 -- pytest fixture re-export
)
from tests.test_curated_vocabulary import (
    register,
)
from tests.test_srs_postgres import NOW, setup_word

pytestmark = pytest.mark.postgres


def submission(stage, answer=None, action="ANSWER", key=None):
    from tests.test_fsrs_v2 import ink

    evidence = ink(answer) if stage == "HANZI" and action == "ANSWER" else None
    return StageSubmission(
        submission_key=key or uuid4(),
        stage=stage,
        answer=answer,
        action=action,
        handwriting=evidence,
    )


async def policy_for(sessions, word_id, pos=True):
    async with sessions() as session, session.begin():
        word = await session.get(Word, word_id)
        word.part_of_speech = "verb; noun" if pos else None
        policy = ReviewedPolicy(
            vocabulary_id=word.id,
            content_version=word.content_version,
            checksum=word.checksum,
            policy_version="test-reviewed-v1",
            sense_key="activity",
            vietnamese_prompt="học (một chữ)",
            reviewed_by="synthetic fixture",
            ambiguity_resolution="Fixture-specific isolated meaning",
            accepted_pos=["verb", "noun"] if pos else [],
            pos_skip_reason=None if pos else "MISSING_POS",
        )
        session.add(
            SrsTargetPolicy(
                vocabulary_id=word.id,
                content_version=word.content_version,
                checksum=word.checksum,
                policy=policy.model_dump(mode="json"),
            )
        )


async def start(sessions, owner, saved_id, now=NOW):
    async with sessions() as session:
        return (await SrsService(session, lambda: now).initialize(owner, saved_id))["attempt_id"]


async def send(sessions, owner, attempt, body, now=NOW):
    async with sessions() as session:
        return await ReviewEngine(session, lambda: now).submit(owner, attempt, body)


async def finish(sessions, owner, attempt, now=NOW):
    async with sessions() as session:
        return await ReviewEngine(session, lambda: now).finalize(owner, attempt)


@pytest.mark.parametrize(
    ("answers", "outcome"),
    [
        (("学", "xué", ["noun", "verb"]), "PASS"),
        (("學", "xue2", ["verb", "noun"]), "FAIL"),
        (("学", "xue3", ["verb", "noun"]), "FAIL"),
        (("学", "xue2", ["verb"]), "PASS"),
        (("错", "xue4", ["classifier"]), "FAIL"),
    ],
)
async def test_server_grading_first_answers_and_one_schedule_change(
    curated_sessions, answers, outcome
):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word)
    attempt = await start(sessions, owner, saved)
    for stage, answer in zip(("HANZI", "PINYIN"), answers[:2], strict=True):
        await send(sessions, owner, attempt, submission(stage, answer))
    # Correct retries never replace an original error.
    await send(sessions, owner, attempt, submission("HANZI", "学"))
    result = await finish(sessions, owner, attempt)
    assert result["outcome"] == outcome and result["scheduling_applied"]
    assert await finish(sessions, owner, attempt, NOW + timedelta(days=1)) == result
    async with sessions() as session:
        row = await session.get(Saved, saved)
        history = await session.get(Attempt, attempt)
        assert row.due_review_count == row.schedule_version == 1
        assert row.failure_count == (outcome == "FAIL")
        assert history.submissions[0]["answer"] == answers[0][0]
        from datetime import datetime

        assert row.next_review_at == datetime.fromisoformat(result["state_after"]["fsrs"]["due"])


@pytest.mark.parametrize("action", ["HINT", "REVEAL"])
async def test_assistance_disqualifies_without_advancing_stage(curated_sessions, action):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word, pos=False)
    attempt = await start(sessions, owner, saved)
    if action == "REVEAL":
        with pytest.raises(HTTPException) as error:
            await send(sessions, owner, attempt, submission("HANZI", action=action))
        assert error.value.status_code == 409
        await send(sessions, owner, attempt, submission("HANZI", "?"))
        with pytest.raises(HTTPException):
            await send(sessions, owner, attempt, submission("HANZI", action=action))
        await send(sessions, owner, attempt, submission("PINYIN", "xue2"))
    assistance = await send(sessions, owner, attempt, submission("HANZI", action=action))
    assert assistance["stage"] is None if action == "REVEAL" else assistance["stage"] == "HANZI"
    if action == "HINT":
        assert "correct_answer" not in assistance["feedback"][0]
    await send(sessions, owner, attempt, submission("HANZI", "学"))
    await send(sessions, owner, attempt, submission("PINYIN", "xue2"))
    result = await finish(sessions, owner, attempt)
    assert result["outcome"] == "FAIL"
    assert len(result["feedback"]) == 2


async def test_order_replay_expiry_early_practice_and_missing_pos(curated_sessions):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word, pos=False)
    attempt = await start(sessions, owner, saved)
    for operation in (
        send(sessions, owner, attempt, submission("PINYIN", "xue2")),
        finish(sessions, owner, attempt),
    ):
        with pytest.raises(HTTPException) as error:
            await operation
        assert error.value.status_code == 409
    body = submission("HANZI", "學")
    first = await send(sessions, owner, attempt, body)
    assert await send(sessions, owner, attempt, body) == first
    with pytest.raises(HTTPException) as error:
        await send(sessions, owner, attempt, submission("HANZI", "学", key=body.submission_key))
    assert error.value.status_code == 409
    await send(sessions, owner, attempt, submission("PINYIN", "xue2"))
    await finish(sessions, owner, attempt)
    early = await start(sessions, owner, saved, NOW + timedelta(seconds=30))
    for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
        await send(sessions, owner, early, submission(stage, answer), NOW + timedelta(minutes=11))
    result = await finish(sessions, owner, early, NOW + timedelta(minutes=11))
    assert result["outcome"] == "PASS" and not result["scheduling_applied"]
    expired = await start(sessions, owner, saved, NOW + timedelta(minutes=12))
    with pytest.raises(HTTPException) as error:
        await send(
            sessions, owner, expired, submission("HANZI", "学"), NOW + timedelta(minutes=12) + TTL
        )
    assert error.value.status_code == 410
    with pytest.raises(HTTPException):
        await finish(sessions, owner, expired, NOW + timedelta(days=1))
    async with sessions() as session:
        row = await session.get(Saved, saved)
        assert row.due_review_count == 1 and row.practice_count == 1
        assert (await session.get(Attempt, expired)).completed_at is None


async def test_policy_exclusions_and_no_fabricated_pos(curated_sessions):
    sessions = curated_sessions
    owner, saved, word_id = await setup_word(sessions)
    async with sessions() as session:
        report = await ReviewEngine(session).targets_report(owner, 50, 0)
        assert report["items"] == [] and len(report["excluded"]) == 1
    attempt = await start(sessions, owner, saved)
    with pytest.raises(HTTPException):
        await send(sessions, owner, attempt, submission("HANZI", "学"))
    await policy_for(sessions, word_id, pos=False)
    async with sessions() as session:
        word = await session.get(Word, word_id)
        target = await ReviewedTargets().resolve(session, word)
        assert target.gradeable and target.disabled_stages == (("POS", "MISSING_POS"),)
        stored = await session.get(SrsTargetPolicy, (word.id, word.content_version, word.checksum))
        policy = ReviewedPolicy.model_validate(stored.policy)
        with pytest.raises(ValueError, match="catalog support"):
            policy.model_copy(update={"accepted_pos": ["noun"], "pos_skip_reason": None}).target(
                word
            )
        word.checksum = "b" * 64
        assert not (await ReviewedTargets().resolve(session, word)).gradeable


async def test_http_hidden_answers_ownership_strict_input_and_duplicate_requests(
    curated_client, curated_sessions
):
    client, sessions = curated_client, curated_sessions
    owner = await register(client, "review-owner")
    other = await register(client, "review-other")
    from tests.test_curated_vocabulary import approve, install

    await install(sessions)
    word = await approve(sessions)
    await policy_for(sessions, word)
    saved = (
        await client.post(
            "/api/v1/me/vocabulary", headers=owner, json={"dictionary_entry_id": str(word)}
        )
    ).json()["id"]
    await client.post(
        "/api/v1/me/srs/daily-plans", headers=owner, json={"request_id": str(uuid4())}
    )
    base = "/api/v1/me/srs/sessions"
    response = await client.post(base, headers=owner, json={"saved_id": saved})
    assert response.status_code == 201
    attempt = response.json()["attempt_id"]
    url = f"{base}/{attempt}"
    question = await client.get(url + "/question", headers=owner)
    assert question.headers["cache-control"] == "no-store"
    assert question.json()["stage"] == "HANZI"
    assert "学" not in question.text and "xue2" not in question.text and "xué" not in question.text
    assert "accepted_" not in question.text
    for suffix in ("/question",):
        assert (await client.get(url + suffix)).status_code == 401
        assert (await client.get(url + suffix, headers=other)).status_code == 404
    for suffix, body in (
        ("/submissions", submission("HANZI", "学").model_dump(mode="json")),
        ("/finalize", {}),
    ):
        assert (await client.post(url + suffix, headers=other, json=body)).status_code == 404
        assert (await client.post(url + suffix, json=body)).status_code == 401
    forged = submission("HANZI", "学").model_dump(mode="json") | {"correct": True}
    assert (await client.post(url + "/submissions", headers=owner, json=forged)).status_code == 422
    for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
        body = submission(stage, answer).model_dump(mode="json")
        a = await client.post(url + "/submissions", headers=owner, json=body)
        b = await client.post(url + "/submissions", headers=owner, json=body)
        assert a.status_code == b.status_code == 200 and a.json() == b.json()
        if stage == "HANZI":
            assert "xue2" not in a.text and "xué" not in a.text
    result = await client.post(url + "/finalize", headers=owner, json={})
    assert result.json()["outcome"] == "PASS"
    assert result.json() == (await client.post(url + "/finalize", headers=owner, json={})).json()
    assert (
        await client.post(url + "/finalize", headers=owner, json={"passed": True})
    ).status_code == 422


async def test_independent_connection_duplicate_answers_and_finalizations():
    url = os.environ.get("REVIEW_CONCURRENCY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set REVIEW_CONCURRENCY_TEST_DATABASE_URL to an isolated migrated database")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        owner, saved, word = await setup_word(sessions)
        await policy_for(sessions, word)
        a, b = await start(sessions, owner, saved), await start(sessions, owner, saved)
        for attempt in (a, b):
            for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
                body = submission(stage, answer)
                results = await asyncio.gather(
                    *(send(sessions, owner, attempt, body) for _ in range(3))
                )
                assert results[0] == results[1] == results[2]
        await asyncio.gather(
            finish(sessions, owner, a), finish(sessions, owner, b), finish(sessions, owner, a)
        )
        async with sessions() as session:
            row = await session.get(Saved, saved)
            assert row.due_review_count == row.schedule_version == row.practice_count == 1
            attempts = list(
                await session.scalars(select(Attempt).where(Attempt.user_vocabulary_id == saved))
            )
            assert len(attempts) == 2 and all(len(a.submissions) == 2 for a in attempts)
    finally:
        await engine.dispose()


async def test_finalization_rollback_and_append_only_evidence(curated_sessions):
    from sqlalchemy import event, update

    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word, pos=False)
    attempt = await start(sessions, owner, saved)
    for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
        await send(sessions, owner, attempt, submission(stage, answer))
    async with sessions() as session:

        def reject_flush(session, flush_context, instances):
            for row in session.dirty:
                if isinstance(row, Attempt):
                    row.mode = "INVALID"

        event.listen(session.sync_session, "before_flush", reject_flush)
        with pytest.raises(IntegrityError):
            await ReviewEngine(session, lambda: NOW).finalize(owner, attempt)
    async with sessions() as session:
        assert (await session.get(Saved, saved)).due_review_count == 0
        history = await session.get(Attempt, attempt)
        assert history.completed_at is None and len(history.submissions) == 2
        await session.rollback()
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(
                    update(Attempt).where(Attempt.id == attempt).values(submissions=[])
                )
    assert (await finish(sessions, owner, attempt))["outcome"] == "PASS"


async def test_multiple_errors_demote_only_once_and_restarts_award_nothing(curated_sessions):
    from sqlalchemy import update

    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word)
    async with sessions() as session, session.begin():
        await session.execute(
            update(Saved)
            .where(Saved.id == saved)
            .values(mastery_level=4, phase="REVIEW", next_review_at=NOW)
        )
    abandoned = await start(sessions, owner, saved)
    await send(sessions, owner, abandoned, submission("HANZI", "错"))
    async with sessions() as session:
        assert (await session.get(Saved, saved)).mastery_level == 4
    restarted = await start(sessions, owner, saved)
    for stage, answer in (("HANZI", "错"), ("PINYIN", "xue4")):
        await send(sessions, owner, restarted, submission(stage, answer))
    result = await finish(sessions, owner, restarted)
    assert result["state_after"]["mastery_level"] == 3
    assert result["state_after"]["phase"] == "RELEARNING"
    async with sessions() as session:
        row = await session.get(Saved, saved)
        assert row.failure_count == row.due_review_count == row.schedule_version == 1
        assert (await session.get(Attempt, abandoned)).completed_at is None


async def test_ambiguous_glosses_are_reported_without_learner_penalties(curated_sessions):
    from app.models.curated_vocabulary import VocabularyMeaning
    from tests.test_curated_vocabulary import install, record

    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await install(
        sessions,
        rows=[record(lexical_key="习|xi2", simplified="习", pinyin="xí", pinyin_numbered="xi2")],
        batch="shared-meaning",
        checksum="b" * 64,
    )
    async with sessions() as session, session.begin():
        session.add(
            VocabularyMeaning(vocabulary_id=word, language="vi", position=1, gloss="đi học")
        )
    async with sessions() as session:
        report = await ReviewEngine(session).targets_report(owner, 50, 0)
        assert report["items"] == []
        flags = report["excluded"][0]["editorial_flags"]
        assert "SHARED_VIETNAMESE_GLOSS" in flags
        assert "MULTIPLE_MEANINGS_REQUIRE_SENSE_REVIEW" in flags
        row = await session.get(Saved, saved)
        assert row.mastery_level == row.failure_count == row.due_review_count == 0
