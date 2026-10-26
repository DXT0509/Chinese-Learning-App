"""End-to-end operator rehearsal on a fresh, explicitly selected isolated database."""

import asyncio
import json
import os
from argparse import Namespace
from pathlib import Path

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyLocalReview
from app.services.local_codex_review import load_checkpoint
from scripts import local_codex_vocabulary as operator
from tests.test_content_migration import _alembic


@pytest.mark.postgres
async def test_confirmed_atomic_import_receipts_and_replay(tmp_path, monkeypatch):
    value = os.environ.get("LOCAL_CODEX_OPERATOR_TEST_DATABASE_URL")
    if not value:
        pytest.skip("Set LOCAL_CODEX_OPERATOR_TEST_DATABASE_URL to fresh isolated chinese_learning")
    url = make_url(value)
    assert url.host == "127.0.0.1" and url.port == 55442 and url.database == "chinese_learning"
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
            ), "Refusing existing database: rehearsal requires fresh empty isolated DB"
        await asyncio.to_thread(_alembic, value, "upgrade", "head")
        monkeypatch.setenv("LOCAL_CODEX_OPERATOR_TARGET", value)
        monkeypatch.setattr(get_settings(), "environment", "development")
        monkeypatch.setattr(get_settings(), "allow_local_codex_reviewed_vocabulary", True)
        root = Path(__file__).resolve().parents[2] / "docs/datasets/codex-review-4.0.3"
        accepted, _, _ = load_checkpoint(root)
        args = Namespace(
            command="plan",
            checkpoint=root,
            database_env="LOCAL_CODEX_OPERATOR_TARGET",
            output=tmp_path / "plan.json",
            enable_local_codex_review=True,
            operator="Isolated operator rehearsal",
            confirm="",
        )
        await operator.run(args)
        plan = json.loads(args.output.read_text(encoding="utf-8"))
        args.command = "apply"
        with pytest.raises(ValueError, match="confirmation"):
            await operator.run(args)
        args.confirm = plan["confirmation"]
        real_accept = operator.accept_local

        async def fail_after_receipts(*positional, **keywords):
            await real_accept(*positional, **keywords)
            raise RuntimeError("Synthetic interruption after both import and approval")

        monkeypatch.setattr(operator, "accept_local", fail_after_receipts)
        with pytest.raises(RuntimeError, match="Synthetic interruption"):
            await operator.run(args)
        async with engine.connect() as connection:
            assert await connection.scalar(select(func.count()).select_from(CuratedVocabulary)) == 0
            assert (
                await connection.scalar(select(func.count()).select_from(VocabularyLocalReview))
                == 0
            )
        monkeypatch.setattr(operator, "accept_local", real_accept)
        await operator.run(args)
        with pytest.raises(ValueError, match="confirmation"):
            await operator.run(args)  # old pre-import confirmation is stale
        args.command = "plan"
        await operator.run(args)
        args.confirm = json.loads(args.output.read_text(encoding="utf-8"))["confirmation"]
        args.command = "apply"
        await operator.run(args)  # fresh confirmed replay, no duplicate receipts
        async with engine.connect() as connection:
            assert await connection.scalar(
                select(func.count()).select_from(CuratedVocabulary)
            ) == len(accepted)
            assert await connection.scalar(
                select(func.count()).select_from(VocabularyLocalReview)
            ) == len(accepted)
            assert set(await connection.scalars(select(CuratedVocabulary.review_status))) == {
                "LOCAL_CODEX_REVIEWED"
            }
        await asyncio.to_thread(_alembic, value, "check")
    finally:
        await engine.dispose()
