"""Actual backup/reset/restore rehearsal, exclusively on fresh isolated databases."""

import asyncio
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import MetaData, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.models import SrsState, User, UserVocabulary
from app.schemas.content import content_id
from app.schemas.session import Credentials
from app.services.authentication import authenticate
from app.services.content_authoring import import_library
from app.services.content_files import load_library
from app.services.content_storage import LocalContentStorage
from app.services.dictionary_import import import_dictionary
from app.services.lesson_publication import publish_lesson
from app.services.personal_vocabulary import PersonalVocabularyService
from app.services.vocabulary_reset import execute_reset, inventory, local_identity, prepare
from tests.test_content_migration import _alembic
from tests.test_dictionary import fixture_dataset

pytestmark = pytest.mark.postgres


def test_identity_refuses_remote_production_or_ambiguous_database():
    for url, environment, database in [
        ("postgresql+psycopg://test@remote:5432/test", "development", "test"),
        ("postgresql+psycopg://test@127.0.0.1:5432/test", "production", "test"),
        ("postgresql+psycopg://test@127.0.0.1:5432/test", "development", "wrong"),
    ]:
        with pytest.raises(ValueError):
            local_identity(
                Settings(database_url=url, environment=environment), database, "127.0.0.1", 5432
            )


async def fresh_legacy_database(variable, tmp_path):
    url = os.environ.get(variable)
    if not url:
        pytest.skip(f"Set {variable} to a fresh empty isolated PostgreSQL database")
    engine = create_async_engine(url)
    async with engine.connect() as connection:
        assert (
            await connection.scalar(
                text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
            )
            == 0
        ), "Refusing nonempty test database"
    await asyncio.to_thread(_alembic, url, "upgrade", "0007_personal_vocabulary")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    storage = LocalContentStorage(tmp_path)
    async with sessions() as session:
        await import_library(
            session, load_library(Path(__file__).resolve().parents[1] / "content"), storage
        )
        await publish_lesson(session, content_id("lesson", "lesson-ni"), 2, storage)
        await authenticate(
            session,
            Credentials(email="reset-preserve@example.com", password="test-password"),
            register=True,
        )
        await import_dictionary(session, fixture_dataset(), "synthetic-test-v1")
        owner = await session.scalar(
            select(User.id).where(User.email == "reset-preserve@example.com")
        )
        await session.rollback()
        await PersonalVocabularyService(session).save(owner, fixture_dataset().entries[0].id)
        async with session.begin():
            saved = UserVocabulary(
                id=uuid4(),
                user_id=owner,
                source="catalog",
                vocabulary_id=content_id("vocabulary", "v-ni"),
            )
            session.add(saved)
            await session.flush()
            session.add(
                SrsState(
                    user_vocabulary_id=saved.id,
                    due_at=datetime.now(UTC),
                    review_count=3,
                    algorithm_version="legacy",
                    algorithm_state={"mastery": 3},
                )
            )
    return url, engine


async def all_rows(engine):
    metadata = MetaData()
    async with engine.connect() as connection:
        await connection.run_sync(metadata.reflect)
        return {
            name: sorted(
                [dict(r) for r in (await connection.execute(select(table))).mappings()], key=repr
            )
            for name, table in metadata.tables.items()
            if name != "alembic_version"
        }


async def test_nonempty_curated_upgrade_preserves_all_existing_values(tmp_path):
    url, engine = await fresh_legacy_database("CURATED_MIGRATION_TEST_DATABASE_URL", tmp_path)
    try:
        before = await all_rows(engine)
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        after = await all_rows(engine)
        for name, rows in before.items():
            assert after[name] == rows, name
        assert after["curated_vocabulary"] == after["curated_user_vocabulary"] == []
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()


async def test_backup_confirmation_reset_preservation_and_repeat_safety(tmp_path):
    url, engine = await fresh_legacy_database(
        "VOCABULARY_RESET_TEST_DATABASE_URL", tmp_path / "content"
    )
    await asyncio.to_thread(_alembic, url, "upgrade", "head")
    settings = Settings(database_url=url, environment="development")
    parsed = make_url(url)
    identity = local_identity(settings, parsed.database, parsed.host, parsed.port)
    pg_dump = os.environ.get("TEST_PG_DUMP", "pg_dump")
    try:
        async with engine.begin() as connection:
            report = await prepare(connection, settings, identity, tmp_path / "backup", pg_dump)
        assert report["inventory"]["published_vocabulary_links_removed"] == 1
        assert report["inventory"]["clear"]["dictionary_entries"] == 10
        assert report["inventory"]["preserve"]["users"] == 1
        assert Path(report["backup"]["path"]).stat().st_size > 0
        async with engine.begin() as connection:
            with pytest.raises(ValueError, match="Confirmation"):
                await execute_reset(connection, report, "wrong", identity)
        # Same-count updates to data being cleared also invalidate the backup approval.
        async with engine.begin() as connection:
            original_attribution = await connection.scalar(
                text("SELECT attribution FROM dictionary_imports")
            )
            await connection.execute(
                text("UPDATE dictionary_imports SET attribution='synthetic changed metadata'")
            )
        async with engine.begin() as connection:
            with pytest.raises(ValueError, match="changed"):
                await execute_reset(connection, report, report["confirmation"], identity)
        async with engine.begin() as connection:
            await connection.execute(
                text("UPDATE dictionary_imports SET attribution=:value"),
                {"value": original_attribution},
            )
        # A new dependency cannot silently expand deletion scope.
        async with engine.begin() as connection:
            await connection.execute(
                text("CREATE TABLE reset_dependency_probe (id uuid REFERENCES vocabulary(id))")
            )
            with pytest.raises(ValueError, match="dependency"):
                await inventory(connection)
            await connection.execute(text("DROP TABLE reset_dependency_probe"))
        async with engine.begin() as connection:
            result = await execute_reset(connection, report, report["confirmation"], identity)
        assert result["deleted"]["srs_states"] == 1
        async with engine.begin() as connection:
            after = await inventory(connection)
            assert not any(after["clear"].values())
            assert after["preserved_checksums"] == report["inventory"]["preserved_checksums"]
            assert (
                await connection.scalar(
                    text(
                        "SELECT tgenabled FROM pg_trigger WHERE tgname='lesson_vocabulary_immutable'"
                    )
                )
                == "O"
            )
            assert (
                await connection.scalar(text("SELECT count(*) FROM curated_user_vocabulary")) == 0
            )
        # Stale report is refused; a new empty report makes another apply a no-op.
        async with engine.begin() as connection:
            with pytest.raises(ValueError, match="changed"):
                await execute_reset(connection, report, report["confirmation"], identity)
        async with engine.begin() as connection:
            empty_report = await prepare(
                connection, settings, identity, tmp_path / "backup", pg_dump
            )
        async with engine.begin() as connection:
            assert (
                await execute_reset(
                    connection, empty_report, empty_report["confirmation"], identity
                )
            )["already_empty"]
        # Retain an actual dry-run artifact for the final report, without credentials.
        artifact = Path(".vocabulary-backups/isolated-rehearsal-report.json")
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_text(json.dumps(report, indent=2), encoding="utf-8")
        restore_url = os.environ.get("VOCABULARY_RESTORE_TEST_DATABASE_URL")
        if restore_url:
            restore_engine = create_async_engine(restore_url)
            try:
                async with restore_engine.connect() as connection:
                    assert (
                        await connection.scalar(
                            text(
                                "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
                            )
                        )
                        == 0
                    )
                restore = make_url(restore_url)
                environment = {
                    **os.environ,
                    "PGHOST": restore.host,
                    "PGPORT": str(restore.port),
                    "PGDATABASE": restore.database,
                    "PGUSER": restore.username,
                    "PGPASSWORD": restore.password or "",
                }
                executable = (
                    str(Path(pg_dump).with_name("pg_restore.exe"))
                    if Path(pg_dump).is_absolute()
                    else "pg_restore"
                )
                completed = await asyncio.to_thread(
                    subprocess.run,
                    [
                        executable,
                        "--no-password",
                        "--exit-on-error",
                        "--dbname=" + restore.database,
                        report["backup"]["path"],
                    ],
                    env=environment,
                    capture_output=True,
                    check=False,
                    timeout=60,
                )
                assert completed.returncode == 0, "Restore rehearsal failed"
                async with restore_engine.begin() as connection:
                    restored = await inventory(connection)
                assert restored["clear"] == report["inventory"]["clear"]
                assert restored["preserved_checksums"] == report["inventory"]["preserved_checksums"]
            finally:
                await restore_engine.dispose()
    finally:
        await engine.dispose()
