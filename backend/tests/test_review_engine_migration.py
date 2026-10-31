"""Fresh-empty nonempty 0011 -> 0012 rehearsal, retaining all fixtures."""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import MetaData, insert, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from scripts.review_preservation import inventory
from tests.test_content_migration import _alembic
from tests.test_srs_postgres import NOW, setup_word


@pytest.mark.postgres
async def test_upgrade_preserves_progress_and_existing_attempt_history():
    url = os.environ.get("REVIEW_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set REVIEW_MIGRATION_TEST_DATABASE_URL to a fresh empty isolated database")
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
            ), "Refusing rehearsal: database must be fresh and empty"
        await asyncio.to_thread(_alembic, url, "upgrade", "0011_srs_foundation")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        _owner, saved, _word = await setup_word(sessions)
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            attempts = metadata.tables["srs_review_attempts"]
            for completed in (False, True):
                values = {
                    "id": uuid4(),
                    "user_vocabulary_id": saved,
                    "mode": "DUE",
                    "schedule_version": 0,
                    "target": {"legacy_fixture": True},
                    "state_before": {"preserve": True},
                    "started_at": NOW,
                }
                if completed:
                    values.update(
                        completed_at=NOW,
                        outcome="FAIL",
                        evidence={"stages": []},
                        state_after={"preserve": True},
                        scheduling_applied=False,
                    )
                await connection.execute(insert(attempts), values)
            before = {
                name: [dict(r) for r in (await connection.execute(select(table))).mappings()]
                for name, table in metadata.tables.items()
                if name != "alembic_version"
            }
            fingerprints = await inventory(connection)
        await asyncio.to_thread(_alembic, url, "upgrade", "0012_srs_review_engine")
        async with engine.connect() as connection:
            assert await inventory(connection) == fingerprints
            for name, rows in before.items():
                after = [
                    dict(r)
                    for r in (await connection.execute(select(metadata.tables[name]))).mappings()
                ]
                assert sorted(rows, key=repr) == sorted(after, key=repr), name
            assert list(
                (
                    await connection.execute(text("SELECT submissions FROM srs_review_attempts"))
                ).scalars()
            ) == [[], []]
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
