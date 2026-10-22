"""Nonempty 0005 -> 0006 rehearsal. Fresh database only; never resets or downgrades."""

import asyncio
import os
from dataclasses import asdict
from uuid import uuid4, uuid5

import pytest
from sqlalchemy import MetaData, insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.services.cedict import NAMESPACE, SOURCE
from tests.test_content_migration import _alembic
from tests.test_dictionary import fixture_dataset

pytestmark = pytest.mark.postgres


async def test_enrichment_upgrade_preserves_dictionary_and_curriculum_columns():
    url = os.environ.get("ENRICHMENT_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ENRICHMENT_MIGRATION_TEST_DATABASE_URL to a fresh empty PostgreSQL DB")
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
            ), "Refusing migration rehearsal: use a fresh empty database"
        await asyncio.to_thread(_alembic, url, "upgrade", "0005_dictionary_foundation")
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            dataset = fixture_dataset()
            import_id = uuid5(NAMESPACE, f"{SOURCE}:revision:your-actual-source-release")
            await connection.execute(
                insert(metadata.tables["dictionary_imports"]),
                {
                    "id": import_id,
                    "source": SOURCE,
                    "revision": "your-actual-source-release",
                    "sha256": dataset.sha256,
                    "source_url": "https://www.mdbg.net/",
                    "license": "CC-BY-SA-4.0",
                    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                    "attribution": "TEST PRESERVE ATTRIBUTION",
                    "changes": "TEST PRESERVE CHANGES",
                    "entry_count": len(dataset.entries),
                },
            )
            await connection.execute(
                insert(metadata.tables["dictionary_entries"]),
                [
                    dict(asdict(row), source=SOURCE, import_id=import_id, active=True)
                    for row in dataset.entries
                ],
            )
            user_id, vocabulary_id = uuid4(), uuid4()
            await connection.execute(
                insert(metadata.tables["users"]), {"id": user_id, "display_name": "TEST PRESERVE"}
            )
            await connection.execute(
                insert(metadata.tables["vocabulary"]),
                {
                    "id": vocabulary_id,
                    "simplified": "测试",
                    "pinyin": "cè shì",
                    "vietnamese_meaning": "TEST PRESERVE",
                },
            )
            await connection.execute(
                insert(metadata.tables["user_vocabulary"]),
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "vocabulary_id": vocabulary_id,
                    "source": "catalog",
                },
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
            assert (
                await connection.scalar(text("SELECT revision_correction FROM dictionary_imports"))
                is None
            )
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
