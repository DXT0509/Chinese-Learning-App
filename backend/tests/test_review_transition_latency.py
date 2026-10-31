"""Opt-in synthetic PostgreSQL service timing; not a physical-device benchmark."""

import json
from time import perf_counter
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models.srs import SrsReviewAttempt
from app.services.curated_catalog import CuratedCatalog
from app.services.review_engine import ReviewEngine
from app.services.srs import SrsService
from tests.test_curated_vocabulary import approve, install, record
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_review_engine import policy_for, send, submission
from tests.test_srs_postgres import NOW, setup_word

pytestmark = pytest.mark.postgres


async def test_real_database_finalize_and_next_preparation(curated_sessions):
    sessions = curated_sessions
    owner, saved, word = await setup_word(sessions)
    await policy_for(sessions, word)
    row = record(lexical_key="马|ma3", simplified="马", pinyin="mǎ", pinyin_numbered="ma3")
    await install(sessions, [row], batch="next-word", checksum="b" * 64)
    next_word = await approve(sessions, row)
    await policy_for(sessions, next_word)
    async with sessions() as session:
        next_saved = (await CuratedCatalog(session).save(owner, next_word)).id
    async with sessions() as session:
        first = await SrsService(session, lambda: NOW).initialize(owner, saved, uuid4())
    for stage, answer in (("HANZI", "学"), ("PINYIN", "xue2")):
        await send(sessions, owner, first["attempt_id"], submission(stage, answer))
    started = perf_counter()
    async with sessions() as session:
        result = await ReviewEngine(session, lambda: NOW).finalize(owner, first["attempt_id"])
    finalize_ms = (perf_counter() - started) * 1000
    async with sessions() as session:
        await ReviewEngine(session, lambda: NOW).planner().create(owner, uuid4())
    key = uuid4()
    started = perf_counter()
    async with sessions() as session:
        next_attempt = await SrsService(session, lambda: NOW).initialize(owner, next_saved, key)
    creation_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    async with sessions() as session:
        view = await ReviewEngine(session, lambda: NOW).question(owner, key)
    question_ms = (perf_counter() - started) * 1000
    async with sessions() as session:
        replay = await SrsService(session, lambda: NOW).initialize(owner, next_saved, key)
    assert replay == next_attempt and result["outcome"] == "PASS"
    assert view["stage"] == "HANZI" and not view["feedback"]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(SrsReviewAttempt)) == 2
    print(
        "PHASE44_LOCAL_POSTGRES_MS="
        + json.dumps(
            {
                "finalize": finalize_ms,
                "next_creation": creation_ms,
                "next_question": question_ms,
                "next_preparation_total": creation_ms + question_ms,
            }
        )
    )
