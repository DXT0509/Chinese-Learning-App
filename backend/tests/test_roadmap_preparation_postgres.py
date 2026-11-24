"""Generated content compatibility in rollback-only isolated fixtures, never development."""

from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models.roadmap import (
    ExpGrant,
    NodeProgress,
    Roadmap,
    RoadmapNodeVersion,
    RoadmapVersion,
)
from app.models.srs_v2 import SrsMemory
from app.schemas.roadmap_preparation import PreparationPlan
from app.services.content_files import ContentError
from app.services.content_storage import LocalContentStorage
from app.services.roadmap_authoring import compile_preview, import_draft
from app.services.roadmap_preparation import compile_drafts, load_catalog, load_json
from tests.test_curated_vocabulary import approve, install
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_roadmap_preparation import PLAN, SOURCE

pytestmark = pytest.mark.postgres


async def test_generated_import_preview_is_idempotent_inactive_and_has_no_learner_writes(
    curated_sessions,
    tmp_path,
):
    plan = PreparationPlan.model_validate(load_json(PLAN))
    catalog = load_catalog([SOURCE])
    rows = [catalog[ref.vocabulary_id] for ref in plan.groups[0].vocabulary]
    await install(curated_sessions, rows, batch=f"preparation-synthetic-{uuid4()}")
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert report.payload()["draft_valid"]

    async def learner_counts():
        async with curated_sessions() as session:
            return [
                await session.scalar(select(func.count()).select_from(model))
                for model in (ExpGrant, NodeProgress, SrsMemory)
            ]

    before = await learner_counts()
    async with curated_sessions() as session:
        identifier = await import_draft(session, definition)
        assert await import_draft(session, definition) == identifier
        async with session.begin():
            with pytest.raises(ContentError, match="current reviewed catalog revision"):
                await compile_preview(session, identifier, LocalContentStorage(tmp_path))
    # The explicit fixture approval exists ONLY inside the rolled-back isolated test DB.
    for row in rows:
        await approve(curated_sessions, row)
    async with curated_sessions() as session, session.begin():
        preview, nodes = await compile_preview(session, identifier, LocalContentStorage(tmp_path))
        assert preview == definition and len(nodes) == 4
        version = await session.get(RoadmapVersion, identifier)
        roadmap = await session.get(Roadmap, definition.id)
        assert version.status == "DRAFT" and roadmap.active_version_id is None
        assert (
            await session.scalar(
                select(func.count())
                .select_from(RoadmapNodeVersion)
                .where(RoadmapNodeVersion.roadmap_version_id == identifier)
            )
            == 4
        )
    assert await learner_counts() == before


async def test_prepared_assets_reuse_existing_importer_without_legacy_vocabulary(
    curated_sessions,
    tmp_path,
):
    from app.models import Asset, Vocabulary
    from app.services.content_authoring import import_library
    from app.services.content_files import load_library
    from app.services.roadmap_preparation import generate
    from tests.test_roadmap_preparation import audio_asset

    plan = PreparationPlan.model_validate(load_json(PLAN))
    catalog = load_catalog([SOURCE])
    asset, _ = audio_asset(plan, tmp_path)
    plan.assets = [asset]
    output = tmp_path / "prepared"
    definition, _ = generate(plan, catalog, tmp_path, output)
    library = load_library(output / "asset-library", assets_only=True)
    async with curated_sessions() as session:
        before = await session.scalar(select(func.count()).select_from(Vocabulary))
        await session.rollback()
        await import_library(session, library, LocalContentStorage(output / "objects"))
        await import_library(session, library, LocalContentStorage(output / "objects"))
        stored = await session.get(Asset, definition.nodes[0].lesson.audio.asset_id)
        assert stored.sha256 == asset.sha256 and stored.media_type == "audio/wav"
        assert await session.scalar(select(func.count()).select_from(Vocabulary)) == before
