"""Fresh-empty 0010 -> 0011 rehearsal; refuses tables and retains fixtures."""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4, uuid5

import pytest
from sqlalchemy import MetaData, insert, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.curated_import import NAMESPACE, approve_record, import_records, record_checksum
from tests.test_content_migration import _alembic
from tests.test_curated_vocabulary import record


@pytest.mark.postgres
async def test_nonempty_srs_upgrade_preserves_every_original_column():
    url = os.environ.get("SRS_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SRS_MIGRATION_TEST_DATABASE_URL to a fresh empty isolated database")
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
        await asyncio.to_thread(_alembic, url, "upgrade", "0010_local_codex_review")
        words = [record(lexical_key=f"{h}|xue2", simplified=h) for h in "学人大小天地"]
        async with async_sessionmaker(engine)() as session:
            await import_records(session, "srs-migration", "a" * 64, words)
            for word in words:
                await approve_record(
                    session,
                    uuid5(NAMESPACE, word.lexical_key),
                    record_checksum(word),
                    "Synthetic reviewer",
                )
        metadata = MetaData()
        now = datetime(2026, 1, 1, tzinfo=UTC)
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            owner = uuid4()
            await connection.execute(
                insert(metadata.tables["users"]), {"id": owner, "display_name": "Preserved user"}
            )
            for level, word in enumerate(words):
                identifier = uuid4()
                await connection.execute(
                    insert(metadata.tables["curated_user_vocabulary"]),
                    {
                        "id": identifier,
                        "user_id": owner,
                        "vocabulary_id": uuid5(NAMESPACE, word.lexical_key),
                        "saved_at": now,
                    },
                )
                await connection.execute(
                    text("""UPDATE curated_user_vocabulary SET
                    mastery_level=:level, next_review_at=:due, last_reviewed_at=:last,
                    is_active=:active WHERE id=:id"""),
                    {
                        "id": identifier,
                        "level": level,
                        "due": now + timedelta(days=level) if level else None,
                        "last": now - timedelta(days=1) if level else None,
                        "active": level != 4,
                    },
                )
            legacy_id, state_id = uuid4(), uuid4()
            await connection.execute(
                insert(metadata.tables["user_vocabulary"]),
                {
                    "id": legacy_id,
                    "user_id": owner,
                    "source": "custom",
                    "custom_simplified": "学",
                    "custom_pinyin": "xue2",
                    "custom_meaning": "hoc",
                },
            )
            await connection.execute(
                insert(metadata.tables["srs_states"]),
                {
                    "id": state_id,
                    "user_vocabulary_id": legacy_id,
                    "due_at": now,
                    "review_count": 17,
                    "algorithm_version": "legacy-unknown",
                    "algorithm_state": {"preserve": True},
                },
            )
            # Include a held vocabulary without changing its saved identity or history.
            await connection.execute(
                text("UPDATE curated_vocabulary SET review_status='NEEDS_REVIEW' WHERE id=:id"),
                {"id": uuid5(NAMESPACE, words[3].lexical_key)},
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
                expected = rows
                if name == "curated_user_vocabulary":
                    expected = [
                        {**r, "next_review_at": r["next_review_at"] or r["saved_at"]} for r in rows
                    ]
                assert sorted(after, key=repr) == sorted(expected, key=repr), name
            rows = (
                (await connection.execute(text("SELECT * FROM curated_user_vocabulary")))
                .mappings()
                .all()
            )
            assert len(rows) == 6
            for row in rows:
                assert row["phase"] == ("LEARNING" if row["mastery_level"] == 0 else "REVIEW")
                assert row["level_progress"] == row["phase_step"] == row["due_review_count"] == 0
                assert row["legacy_srs_snapshot"]["mastery_level"] == row["mastery_level"]
                if row["mastery_level"] == 0:
                    assert row["legacy_srs_snapshot"]["next_review_at"] is None
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
