"""Rollback-only technical publication rehearsal; never educational approval of the pack."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select

from app.models.roadmap import Roadmap, RoadmapNodeVersion
from app.models.srs import SrsReviewAttempt
from app.models.srs_v2 import SrsMemory
from app.services.content_authoring import import_library
from app.services.content_files import load_library
from app.services.content_storage import LocalContentStorage
from app.services.roadmap_authoring import activate, import_draft, publish
from app.services.roadmap_preparation import generate, load_catalog, load_json
from scripts.prepare_hsk0_pack import CATALOG, PACK, build_plan
from tests.test_curated_vocabulary import approve, install, register
from tests.test_curated_vocabulary import curated_client as curated_client  # noqa: PLC0414
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414

pytestmark = pytest.mark.postgres


@pytest.mark.parametrize("proposal", ["v3", "v4", "signed-v4"])
async def test_real_pack_isolated_import_publish_activation_api_and_fsrs_preservation(
    curated_sessions,
    curated_client,
    tmp_path,
    monkeypatch,
    proposal,
):
    from app.core import config

    settings = config.get_settings()
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: settings.model_copy(update={"content_storage_dir": tmp_path / "objects"}),
    )
    from scripts.finalize_hsk0_review import bind_pending_reviews, corrected_plan

    if proposal == "signed-v4":
        from app.schemas.roadmap_preparation import PreparationPlan

        plan = PreparationPlan.model_validate(load_json(PACK / "signed-complete-v4/plan.json"))
    else:
        plan = bind_pending_reviews(corrected_plan()) if proposal == "v4" else build_plan()
    catalog = load_catalog([CATALOG])
    rows = [catalog[r.vocabulary_id] for r in plan.groups[0].vocabulary]
    await install(curated_sessions, rows, batch=f"isolated-hsk0-{uuid4()}")
    # Existing synthetic catalog approval fixture, isolated transaction only. No source review fields change.
    for row in rows:
        await approve(curated_sessions, row)
    definition, quality = generate(
        plan, catalog, PACK, tmp_path, operator_preview=proposal != "signed-v4"
    )
    if proposal == "signed-v4":
        assert quality.payload()["draft_valid"] and quality.payload()["counts"]["ERROR"] == 0
    storage = LocalContentStorage(tmp_path / "objects")
    async with curated_sessions() as session:
        await import_library(
            session, load_library(tmp_path / "asset-library", assets_only=True), storage
        )
        identifier = await import_draft(session, definition)
        await publish(
            session, identifier, storage, "ISOLATED TECHNICAL TEST; not human educational approval"
        )
        await activate(session, definition.id, None)
        await activate(session, definition.id, identifier)
        async with session.begin():
            assert (await session.get(Roadmap, definition.id)).active_version_id == identifier
            nodes = list(
                await session.scalars(
                    select(RoadmapNodeVersion)
                    .where(RoadmapNodeVersion.roadmap_version_id == identifier)
                    .order_by(RoadmapNodeVersion.position)
                )
            )

    async def fsrs_counts():
        async with curated_sessions() as session:
            return [
                await session.scalar(select(func.count()).select_from(m))
                for m in (SrsMemory, SrsReviewAttempt)
            ]

    before = await fsrs_counts()
    headers = await register(curated_client, f"isolated-hsk0-{uuid4()}")
    owner = UUID((await curated_client.get("/api/v1/auth/me", headers=headers)).json()["id"])
    total_exp = 0
    for node, membership in zip(definition.nodes, nodes, strict=True):
        detail = await curated_client.get(f"/api/v1/roadmap-nodes/{membership.id}", headers=headers)
        assert detail.status_code == 200 and "correct_option" not in detail.text
        assert detail.json()["definition"]["node_type"] == node.node_type
        if node.node_type == "NEW_WORD":
            for enrichment, media_type in (
                (node.lesson.audio, "audio/ogg"),
                (node.lesson.stroke_order, "image/gif"),
            ):
                asset = await curated_client.get(
                    f"/api/v1/roadmap-nodes/{membership.id}/assets/{enrichment.asset_id}",
                    headers=headers,
                )
                assert asset.status_code == 200 and asset.headers["content-type"].startswith(
                    media_type
                )
        started = await curated_client.post(
            f"/api/v1/roadmap-nodes/{membership.id}/start", json={}, headers=headers
        )
        assert started.status_code == 200
        run_id = started.json()["id"]
        for activity in node.lesson.activities:
            if not activity.required:
                continue
            for repetition in range(activity.repetitions):
                body = {
                    "request_id": str(uuid4()),
                    "activity_id": str(activity.id),
                    "kind": "ACKNOWLEDGE",
                    "repetition": repetition,
                }
                if activity.kind == "QUIZ":
                    body.update(kind="CHOICE", choice=activity.correct_option)
                elif activity.kind == "HANDWRITING":
                    body.update(
                        kind="FREEHAND",
                        duration_ms=1200,
                        strokes=[[{"x": 0.1, "y": 0.2}, {"x": 0.6, "y": 0.8}]],
                    )
                elif activity.kind == "PRONUNCIATION":
                    body.update(kind="SPEAKING", duration_ms=1200)
                receipt = await curated_client.post(
                    f"/api/v1/roadmap-runs/{run_id}/activities", json=body, headers=headers
                )
                assert receipt.status_code == 200 and receipt.json()["accepted"]
        completion = await curated_client.post(
            f"/api/v1/roadmap-runs/{run_id}/complete", headers=headers
        )
        assert completion.status_code == 200
        total_exp += completion.json()["exp_awarded"]
        repeated = await curated_client.post(
            f"/api/v1/roadmap-runs/{run_id}/complete", headers=headers
        )
        assert repeated.json()["exp_awarded"] == 0
    assert total_exp == 45
    assert await fsrs_counts() == before
    progress = await curated_client.get("/api/v1/me/roadmap-progress", headers=headers)
    assert progress.json() == {"total_exp": 45, "completed_nodes": 4, "skipped_nodes": 0}
    from app.models.curated_vocabulary import CuratedUserVocabulary
    from app.models.roadmap import ExpGrant, NodeProgress

    async with curated_sessions() as session:
        saves = list(
            await session.scalars(
                select(CuratedUserVocabulary).where(CuratedUserVocabulary.user_id == owner)
            )
        )
        assert {s.vocabulary_id for s in saves} == {
            r.vocabulary_id for r in plan.groups[0].vocabulary
        }
        assert len(saves) == 3 and all(
            s.mastery_level == 0 and not s.learning_activated for s in saves
        )
        assert (
            await session.scalar(
                select(func.count()).select_from(NodeProgress).where(NodeProgress.user_id == owner)
            )
            == 4
        )
        assert (
            await session.scalar(
                select(func.count()).select_from(ExpGrant).where(ExpGrant.user_id == owner)
            )
            == 4
        )
