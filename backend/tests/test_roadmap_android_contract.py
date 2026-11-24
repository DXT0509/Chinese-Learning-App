"""Additive Android recovery and media contracts; no development data is used."""

import hashlib
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.schemas.roadmap import ActivitySubmission, RunView
from app.services.content_storage import LocalContentStorage
from app.services.roadmap import RoadmapService
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_roadmap import draft
from tests.test_roadmap_postgres import call, setup


async def test_accepted_repetitions_are_distinct_sorted_and_preserve_activity_scope():
    activity, other = uuid4(), uuid4()
    rows = [
        (activity, {"repetition": 2}),
        (activity, {"repetition": 0}),
        (activity, {"repetition": 2}),
        (other, {"repetition": 1}),
    ]
    session = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(all=lambda: rows)))
    assert await RoadmapService(session).accepted_repetitions(uuid4()) == {
        str(activity): [0, 2],
        str(other): [1],
    }


def test_run_view_addition_is_backward_compatible():
    result = RunView(
        id=uuid4(),
        node_version_id=uuid4(),
        replay=False,
        completed_at=None,
        accepted_activity_ids=[],
    )
    assert result.accepted_repetitions == {}


async def test_media_requires_exact_reviewed_reference_and_verified_object(tmp_path, monkeypatch):
    from app.core import config

    storage = LocalContentStorage(tmp_path)
    raw = b"synthetic transport bytes; not educational audio"
    key = storage.put_bundle(raw)
    asset_id = uuid4()
    definition = draft().nodes[0]
    definition.lesson.audio.status = "AVAILABLE"
    definition.lesson.audio.asset_id = asset_id
    asset = SimpleNamespace(
        storage_key=key,
        sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
        media_type="audio/mpeg",
    )
    session = SimpleNamespace(get=AsyncMock(return_value=asset))
    service = RoadmapService(session)
    service.context = AsyncMock(
        return_value=(
            None,
            SimpleNamespace(engine_definition=definition.model_dump(mode="json")),
            None,
            None,
        )
    )
    monkeypatch.setattr(
        config, "get_settings", lambda: SimpleNamespace(content_storage_dir=tmp_path)
    )
    owner, node = uuid4(), uuid4()
    assert await service.media(owner, node, asset_id) == (raw, "audio/mpeg")
    service.context.assert_awaited_with(owner, node)
    with pytest.raises(HTTPException) as failure:
        await service.media(owner, node, uuid4())
    assert failure.value.status_code == 404
    asset.sha256 = "0" * 64
    with pytest.raises(HTTPException) as failure:
        await service.media(owner, node, asset_id)
    assert failure.value.status_code == 503


@pytest.mark.postgres
async def test_pagination_anchor_sections_and_owned_resume_receipts(curated_sessions, tmp_path):
    owner, other, definition, nodes, _ = await setup(curated_sessions, tmp_path)
    page = await call(curated_sessions, "nodes", owner, definition.id, None, -1, 2)
    assert page["current_position"] == 0
    assert page["section_positions"] == {"hsk-0": 0}
    run = await call(curated_sessions, "start", owner, nodes[0].id)
    activity = definition.nodes[0].lesson.activities[0]
    body = ActivitySubmission(request_id=uuid4(), activity_id=activity.id, kind="ACKNOWLEDGE")
    await call(curated_sessions, "record", owner, run["id"], body)
    await call(curated_sessions, "record", owner, run["id"], body)
    resumed = await call(curated_sessions, "start", owner, nodes[0].id)
    assert resumed["id"] == run["id"]
    assert resumed["accepted_repetitions"] == {str(activity.id): [0]}
    other_run = await call(curated_sessions, "start", other, nodes[0].id)
    assert other_run["accepted_repetitions"] == {}
    with pytest.raises(HTTPException) as failure:
        await call(curated_sessions, "media", owner, nodes[1].id, uuid4())
    assert failure.value.status_code == 403
    with pytest.raises(HTTPException) as failure:
        await call(curated_sessions, "media", owner, nodes[0].id, uuid4())
    assert failure.value.status_code == 404
