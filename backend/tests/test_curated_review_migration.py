"""Fresh-empty nonempty 0008 -> 0009 rehearsal. Fixtures are retained."""

import asyncio
import os
from uuid import uuid4, uuid5

import pytest
from sqlalchemy import MetaData, insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.services.curated_import import NAMESPACE, approve_record, import_records, record_checksum
from tests.test_content_migration import _alembic
from tests.test_curated_vocabulary import record


@pytest.mark.postgres
async def test_ai_upgrade_preserves_all_existing_rows():
    url = os.environ.get("AI_REVIEW_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set AI_REVIEW_MIGRATION_TEST_DATABASE_URL to a fresh empty database")
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
            ), "Refusing migration rehearsal: database must be fresh and empty"
        await asyncio.to_thread(_alembic, url, "upgrade", "0008_curated_vocabulary")
        from sqlalchemy.ext.asyncio import async_sessionmaker

        async with async_sessionmaker(engine)() as session:
            await import_records(session, "migration-fixture", "a" * 64, [record()])
            await approve_record(
                session,
                uuid5(NAMESPACE, record().lexical_key),
                record_checksum(record()),
                "Synthetic migration fixture",
            )
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            owner = uuid4()
            await connection.execute(
                insert(metadata.tables["users"]), {"id": owner, "display_name": "Preserved user"}
            )
            await connection.execute(
                insert(metadata.tables["curated_user_vocabulary"]),
                {
                    "id": uuid4(),
                    "user_id": owner,
                    "vocabulary_id": uuid5(NAMESPACE, record().lexical_key),
                },
            )
            await connection.execute(
                text("UPDATE curated_user_vocabulary SET mastery_level=4, next_review_at=now()")
            )
            before = {
                name: [dict(row) for row in (await connection.execute(select(table))).mappings()]
                for name, table in metadata.tables.items()
                if name != "alembic_version"
            }
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        async with engine.connect() as connection:
            for name, rows in before.items():
                after = [
                    dict(row)
                    for row in (await connection.execute(select(metadata.tables[name]))).mappings()
                ]
                assert sorted(after, key=repr) == sorted(rows, key=repr), name
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
