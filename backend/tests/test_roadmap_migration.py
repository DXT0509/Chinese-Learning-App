import asyncio
import os
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import MetaData, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import User
from app.models.curated_vocabulary import CuratedUserVocabulary
from app.models.srs_v2 import SrsMemory
from app.services import fsrs_scheduler
from app.services.curated_catalog import CuratedCatalog
from app.services.srs_state import Outcome
from scripts import roadmap_preflight
from tests.test_content_migration import _alembic
from tests.test_curated_vocabulary import approve, install
from tests.test_srs_postgres import NOW


@pytest.mark.postgres
async def test_nonempty_0014_upgrade_preserves_every_existing_row(monkeypatch):
    url = os.environ.get("ROADMAP_MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ROADMAP_MIGRATION_TEST_DATABASE_URL to a fresh empty isolated database")
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
        await asyncio.to_thread(_alembic, url, "upgrade", "0014_fsrs_only")
        metadata = MetaData()
        async with engine.begin() as connection:
            await connection.run_sync(metadata.reflect)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        owner = uuid4()
        async with sessions() as session, session.begin():
            session.add(User(id=owner, display_name="Migration synthetic fixture"))
        await install(sessions)
        word = await approve(sessions)
        async with sessions() as session:
            saved = await CuratedCatalog(session).save(owner, word)
        config = fsrs_scheduler.configuration()
        card, _ = fsrs_scheduler.review(None, Outcome.PASS, NOW, config)
        async with sessions() as session, session.begin():
            await session.execute(
                CuratedUserVocabulary.__table__.update()
                .where(CuratedUserVocabulary.id == saved.id)
                .values(learning_activated=True, next_review_at=NOW)
            )
            session.add(
                SrsMemory(
                    user_vocabulary_id=saved.id,
                    scheduler_version=fsrs_scheduler.VERSION,
                    configuration=config,
                    card=card,
                    adopted_at=NOW,
                )
            )

        async def snapshot():
            async with engine.connect() as connection:
                return {
                    name: [
                        dict(row) for row in (await connection.execute(select(table))).mappings()
                    ]
                    for name, table in metadata.tables.items()
                    if name != "alembic_version"
                }

        before = await snapshot()
        monkeypatch.setattr(
            roadmap_preflight, "get_settings", lambda: SimpleNamespace(database_url=url)
        )
        preflight = await asyncio.to_thread(roadmap_preflight.inspect_database)
        await asyncio.to_thread(_alembic, url, "upgrade", "head")
        assert await snapshot() == before
        verified = await asyncio.to_thread(roadmap_preflight.inspect_database, preflight)
        assert verified["tables"] == preflight["tables"]
        await asyncio.to_thread(_alembic, url, "check")
    finally:
        await engine.dispose()
