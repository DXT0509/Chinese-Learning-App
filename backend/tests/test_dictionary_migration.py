"""A fresh database only; keep all fixture data for post-upgrade inspection."""

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import MetaData, Table, func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import LessonRun, SceneCheckpoint, User
from app.schemas.content import content_id, version_id
from app.schemas.session import Credentials
from app.services.authentication import authenticate
from app.services.content_authoring import import_library
from app.services.content_files import load_library
from app.services.content_storage import LocalContentStorage
from app.services.lesson_publication import publish_lesson
from tests.test_content_migration import _alembic

pytestmark = pytest.mark.postgres


async def test_dictionary_upgrade_preserves_catalog_sessions_runs_and_all_columns(tmp_path):
    url = os.environ.get("DICTIONARY_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set DICTIONARY_MIGRATION_TEST_DATABASE_URL to a fresh empty PostgreSQL DB")
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
        await asyncio.to_thread(_alembic, url, "upgrade", "0004_vocabulary_player")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        storage = LocalContentStorage(tmp_path)
        library = load_library(Path(__file__).resolve().parents[1] / "content")
        async with sessions() as session:
            await import_library(session, library, storage)
            await publish_lesson(session, content_id("lesson", "lesson-ni"), 2, storage)
            await authenticate(
                session,
                Credentials(
                    email="migration-dictionary@example.com", password="test-migration-password"
                ),
                register=True,
            )
            user_id = await session.scalar(select(User.id))
            await session.rollback()
            async with session.begin():
                run_id, scene_key = uuid4(), uuid4()
                session.add(
                    LessonRun(
                        id=run_id,
                        user_id=user_id,
                        request_id=uuid4(),
                        lesson_version_id=version_id("lesson", "lesson-ni", 2),
                        current_scene_key=scene_key,
                    )
                )
                await session.flush()
                session.add(SceneCheckpoint(run_id=run_id, scene_key=scene_key, page=2))
        # Include the complete auth/session/catalog rows, not selected columns only.
        metadata = MetaData()
        async with engine.connect() as connection:
            await connection.run_sync(metadata.reflect)
            before = {
                name: [dict(row) for row in (await connection.execute(select(table))).mappings()]
                for name, table in metadata.tables.items()
                if name != "alembic_version"
            }
        assert before["auth_sessions"] and before["refresh_credentials"]
        assert before["lesson_runs"] and before["lesson_scene_progress"] and before["assets"]
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        async with engine.connect() as connection:
            for name, rows in before.items():
                after = [
                    dict(row)
                    for row in (await connection.execute(select(metadata.tables[name]))).mappings()
                ]
                assert sorted(after, key=repr) == sorted(rows, key=repr), name
            for name in ("dictionary_imports", "dictionary_entries"):
                table = await connection.run_sync(
                    lambda sync, table_name=name: Table(table_name, MetaData(), autoload_with=sync)
                )
                assert await connection.scalar(select(func.count()).select_from(table)) == 0
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
