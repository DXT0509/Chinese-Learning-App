import asyncio
import os
from datetime import timedelta

import pytest
from sqlalchemy import MetaData, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tests.test_content_migration import _alembic
from tests.test_review_engine import policy_for


@pytest.mark.postgres
async def test_nonempty_v2_upgrade_preserves_all_existing_columns_and_history():
    url = os.environ.get("SRS_V2_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SRS_V2_MIGRATION_TEST_DATABASE_URL to a fresh empty isolated database")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            assert (
                await connection.scalar(
                    text(
                        "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
                    )
                )
                == 0
            ), "Refusing nonempty rehearsal database"
        await asyncio.to_thread(_alembic, url, "upgrade", "0012_srs_review_engine")
        # 0012 fixtures use reflected SQL because the new ORM includes an additive column.
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            from datetime import UTC, datetime
            from uuid import uuid4

            owner, now = uuid4(), datetime.now(UTC)
            await connection.execute(
                metadata.tables["users"].insert().values(id=owner, display_name="Migration fixture")
            )
            # Reuse catalog/policy preparation helpers, which do not query saved rows.
        from tests.test_curated_vocabulary import approve, install

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        await install(sessions)
        word = await approve(sessions)
        await policy_for(sessions, word)
        from tests.test_curated_vocabulary import record

        second_record = record(
            lexical_key="字|zi4", simplified="字", pinyin="zì", pinyin_numbered="zi4"
        )
        await install(sessions, [second_record], batch="history-fixture", checksum="b" * 64)
        second_word = await approve(sessions, second_record)
        history_saved = uuid4()
        saved_id, attempt_id = uuid4(), uuid4()
        async with engine.begin() as connection:
            await connection.execute(
                metadata.tables["curated_user_vocabulary"]
                .insert()
                .values(
                    id=saved_id,
                    user_id=owner,
                    vocabulary_id=word,
                    mastery_level=0,
                    phase="LEARNING",
                    phase_step=0,
                    level_progress=0,
                    next_review_at=now,
                )
            )
            await connection.execute(
                metadata.tables["curated_user_vocabulary"]
                .update()
                .where(metadata.tables["curated_user_vocabulary"].c.id == saved_id)
                .values(mastery_level=3, phase="REVIEW", level_progress=1)
            )
            await connection.execute(
                metadata.tables["curated_user_vocabulary"]
                .insert()
                .values(
                    id=history_saved,
                    user_id=owner,
                    vocabulary_id=second_word,
                    mastery_level=0,
                    phase="LEARNING",
                    phase_step=0,
                    level_progress=0,
                    next_review_at=now + timedelta(days=7),
                    last_reviewed_at=now - timedelta(days=1),
                    due_review_count=2,
                    failure_count=1,
                    schedule_version=2,
                )
            )
            for n, outcome in enumerate(("PASS", "FAIL")):
                reviewed_at = now - timedelta(days=2 - n)
                await connection.execute(
                    metadata.tables["srs_review_attempts"]
                    .insert()
                    .values(
                        id=uuid4(),
                        user_vocabulary_id=history_saved,
                        mode="DUE",
                        schedule_version=n,
                        target={"applicable_stages": ["HANZI", "PINYIN", "POS"]},
                        state_before={"mastery_level": 0},
                        state_after={"mastery_level": 0},
                        submissions=[{"stage": "POS", "action": "ANSWER", "answer": ["noun"]}],
                        started_at=reviewed_at - timedelta(seconds=45),
                        completed_at=reviewed_at,
                        outcome=outcome,
                        evidence={"legacy_fixture": True},
                        scheduling_applied=True,
                    )
                )
            await connection.execute(
                metadata.tables["srs_review_attempts"]
                .insert()
                .values(
                    id=attempt_id,
                    user_vocabulary_id=saved_id,
                    mode="DUE",
                    schedule_version=0,
                    target={"applicable_stages": ["HANZI", "PINYIN", "POS"]},
                    state_before={"mastery_level": 3},
                    submissions=[{"stage": "POS", "answer": ["verb"], "action": "ANSWER"}],
                    started_at=now,
                )
            )
            before = {
                name: [dict(r) for r in (await connection.execute(select(table))).mappings()]
                for name, table in metadata.tables.items()
                if name != "alembic_version"
            }
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        async with engine.connect() as connection:
            for name, rows in before.items():
                after = [
                    dict(r)
                    for r in (await connection.execute(select(metadata.tables[name]))).mappings()
                ]
                assert sorted(rows, key=repr) == sorted(after, key=repr), name
            assert (
                await connection.scalar(
                    text("SELECT bool_and(learning_activated) FROM curated_user_vocabulary")
                )
                is True
            )
            assert await connection.scalar(text("SELECT count(*) FROM srs_memory")) == 2
            memory = await connection.scalar(
                text("SELECT card FROM srs_memory WHERE user_vocabulary_id=:id"), {"id": saved_id}
            )
            assert memory["due"] == now.isoformat() and memory["last_review"] is None
            reviewed = await connection.scalar(
                text("SELECT card FROM srs_memory WHERE user_vocabulary_id=:id"),
                {"id": history_saved},
            )
            from app.services.fsrs_scheduler import configuration, replay

            expected = replay(
                [("PASS", now - timedelta(days=2)), ("FAIL", now - timedelta(days=1))],
                configuration(),
            )
            expected.update(card_id=history_saved.int, due=(now + timedelta(days=7)).isoformat())
            assert reviewed == expected
            for table in ("srs_daily_plans", "srs_active_time"):
                assert await connection.scalar(text(f"SELECT count(*) FROM {table}")) == 0
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
