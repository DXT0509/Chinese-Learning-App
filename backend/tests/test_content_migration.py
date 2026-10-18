"""Nonempty upgrade rehearsal. Requires a fresh EMPTY, explicitly selected database.

Never clears, resets or downgrades a database. The test intentionally leaves its fixture
rows behind so the upgraded legacy data can be inspected. Use a new name for another run.
"""

import asyncio
import hashlib
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import MetaData, Table, insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.postgres
BACKEND = Path(__file__).resolve().parents[1]
INITIAL_HASH = "c94de95eb3c4640861c8f983c5497e9ef23464930a420040e8d860d9b488b6b6"


def _alembic(url, *arguments):
    environment = {**os.environ, "DATABASE_URL": url}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    # Avoid exposing SQL or environment values on failure.
    assert result.returncode == 0, f"Alembic {' '.join(arguments)} failed; inspect isolated DB"


async def test_nonempty_upgrade_preserves_every_legacy_column_and_reference():
    url = os.environ.get("MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "Set MIGRATION_TEST_DATABASE_URL to a fresh empty dedicated PostgreSQL database"
        )
    initial = BACKEND / "alembic/versions/0001_initial.py"
    assert hashlib.sha256(initial.read_bytes()).hexdigest() == INITIAL_HASH
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            count = await connection.scalar(
                text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
            )
            assert count == 0, (
                "Refusing migration rehearsal: database must be empty; use a new name"
            )
        await asyncio.to_thread(_alembic, url, "upgrade", "0001_initial")
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
            user, character, first_word, second_word, lesson, entry, srs = [
                uuid4() for _ in range(7)
            ]
            now = datetime.now(UTC)
            fixtures = {
                "users": [{"id": user, "display_name": "Legacy", "google_sub": None}],
                "characters": [
                    {
                        "id": character,
                        "hanzi": "妈",
                        "stroke_count": 0,
                        "radical_info": "legacy unreviewed prose",
                        "stroke_order_asset": "legacy/strokes/key",
                    }
                ],
                "vocabulary": [
                    {
                        "id": first_word,
                        "simplified": "妈妈",
                        "pinyin": "māma",
                        "vietnamese_meaning": "mẹ",
                        "audio_reference": "legacy/audio/key",
                    },
                    {
                        "id": second_word,
                        "simplified": "你",
                        "pinyin": "nǐ",
                        "vietnamese_meaning": "bạn",
                        "audio_reference": None,
                    },
                ],
                "lessons": [
                    {
                        "id": lesson,
                        "title": "Legacy multiword",
                        "lesson_order": 0,
                        "lesson_type": "legacy-word-list",
                    }
                ],
                "vocabulary_characters": [
                    {"vocabulary_id": first_word, "position": position, "character_id": character}
                    for position in (0, 1)
                ],
                "lesson_vocabulary": [
                    {"lesson_id": lesson, "vocabulary_id": word, "position": position}
                    for position, word in enumerate((first_word, second_word))
                ],
                "user_lesson_progress": [
                    {
                        "user_id": user,
                        "lesson_id": lesson,
                        "status": "completed",
                        "completed_at": now,
                    }
                ],
                "user_vocabulary": [
                    {
                        "id": entry,
                        "user_id": user,
                        "vocabulary_id": first_word,
                        "source": "catalog",
                        "learned_at": now,
                    }
                ],
                "srs_states": [
                    {
                        "id": srs,
                        "user_vocabulary_id": entry,
                        "due_at": now,
                        "review_count": 7,
                        "algorithm_version": "unimplemented-v0",
                        "algorithm_state": {"legacy": True},
                    }
                ],
            }
            for table_name, rows in fixtures.items():
                await connection.execute(insert(metadata.tables[table_name]), rows)
            before = {}
            for name in fixtures:
                rows = (await connection.execute(select(metadata.tables[name]))).mappings().all()
                before[name] = [dict(row) for row in rows]
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        async with engine.connect() as connection:
            # Old metadata deliberately selects every ORIGINAL column, including values unknown
            # to the new application. Row order is not semantically significant.
            for name, expected in before.items():
                actual = [
                    dict(row)
                    for row in (await connection.execute(select(metadata.tables[name])))
                    .mappings()
                    .all()
                ]
                assert sorted(actual, key=repr) == sorted(expected, key=repr), name
            links = (
                (
                    await connection.execute(
                        text("SELECT id,lesson_version_id,role FROM lesson_vocabulary")
                    )
                )
                .mappings()
                .all()
            )
            assert len({row["id"] for row in links}) == 2
            assert all(row["lesson_version_id"] is None and row["role"] is None for row in links)
            for table in ("lesson_versions", "assets", "lesson_template_versions"):
                reflected = await connection.run_sync(
                    lambda sync, name=table: Table(name, MetaData(), autoload_with=sync)
                )
                assert (await connection.execute(select(reflected))).all() == []
            assert (
                await connection.scalar(
                    text(
                        "SELECT convalidated FROM pg_constraint WHERE conname='ck_lessons_valid_type'"
                    )
                )
                is False
            )
        await asyncio.to_thread(_alembic, url, "check")
        assert hashlib.sha256(initial.read_bytes()).hexdigest() == INITIAL_HASH
    finally:
        await engine.dispose()
