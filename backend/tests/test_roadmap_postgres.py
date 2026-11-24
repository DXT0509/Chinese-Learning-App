import asyncio
import os
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import LessonVersion, User
from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.roadmap import ExpGrant, NodeProgress, RoadmapNodeVersion, RoadmapVersion
from app.models.srs import SrsReviewAttempt
from app.models.srs_v2 import SrsMemory
from app.schemas.roadmap import ActivitySubmission, RoadmapDefinition
from app.services import fsrs_scheduler
from app.services.content_files import ContentError
from app.services.content_storage import LocalContentStorage
from app.services.curated_catalog import CuratedCatalog
from app.services.roadmap import RoadmapService
from app.services.roadmap_authoring import activate, import_draft, publish, version_id
from app.services.srs_state import Outcome
from tests.test_curated_vocabulary import approve, install, record, register
from tests.test_curated_vocabulary import curated_client as curated_client  # noqa: PLC0414
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_roadmap import draft
from tests.test_srs_postgres import NOW

pytestmark = pytest.mark.postgres


async def setup(sessions, tmp_path):
    rows = [
        record(lexical_key=f"{chr(0x4E00 + i)}|xue2", simplified=chr(0x4E00 + i)) for i in range(3)
    ]
    await install(sessions, rows, batch=f"roadmap-{uuid4()}")
    words = [await approve(sessions, row) for row in rows]
    definition = draft([(w, 1) for w in words])
    storage = LocalContentStorage(tmp_path)
    async with sessions() as session:
        identifier = await import_draft(session, definition)
        await publish(session, identifier, storage, "Synthetic test fixture operator")
    owner, other = uuid4(), uuid4()
    async with sessions() as session, session.begin():
        session.add_all(
            [
                User(id=owner, display_name="Roadmap fixture"),
                User(id=other, display_name="Other fixture"),
            ]
        )
    async with sessions() as session:
        nodes = list(
            await session.scalars(
                select(RoadmapNodeVersion)
                .where(RoadmapNodeVersion.roadmap_version_id == identifier)
                .order_by(RoadmapNodeVersion.position)
            )
        )
    return owner, other, definition, nodes, storage


async def call(sessions, method, *args):
    async with sessions() as session:
        return await getattr(RoadmapService(session), method)(*args)


async def evidence(sessions, owner, run, definition, choice=0):
    for activity in definition.lesson.activities:
        submission = ActivitySubmission(
            request_id=uuid4(),
            activity_id=activity.id,
            kind="CHOICE" if activity.kind == "QUIZ" else "ACKNOWLEDGE",
            choice=choice if activity.kind == "QUIZ" else None,
        )
        assert (await call(sessions, "record", owner, run["id"], submission))["accepted"]
        assert (await call(sessions, "record", owner, run["id"], submission))["accepted"]
        with pytest.raises(HTTPException) as exc:
            await call(
                sessions,
                "record",
                owner,
                run["id"],
                submission.model_copy(update={"duration_ms": 1}),
            )
        assert exc.value.detail["code"] == "IDEMPOTENCY_CONFLICT"


async def test_progress_skip_replay_rewards_and_intake(curated_sessions, tmp_path):
    sessions = curated_sessions
    owner, other, definition, nodes, _ = await setup(sessions, tmp_path)
    page = await call(sessions, "nodes", owner, definition.id, None, -1, 2)
    assert [n["available"] for n in page["items"]] == [True, False]
    assert page["next_position"] == 1
    next_page = await call(sessions, "nodes", owner, definition.id, None, page["next_position"], 2)
    assert [n["position"] for n in next_page["items"]] == [2, 3]
    assert next_page["next_position"] is None
    with pytest.raises(HTTPException) as exc:
        await call(sessions, "start", owner, nodes[1].id)
    assert exc.value.status_code == 403
    await call(sessions, "skip", owner, nodes[0].id)
    await call(sessions, "skip", owner, nodes[0].id)
    async with sessions() as session:
        assert not await session.scalar(select(Saved.id).where(Saved.user_id == owner))
    # Return to skipped lesson; required evidence cannot be bypassed.
    run = await call(sessions, "start", owner, nodes[0].id)
    assert (await call(sessions, "start", owner, nodes[0].id))["id"] == run["id"]
    with pytest.raises(HTTPException) as exc:
        await call(sessions, "complete", owner, run["id"])
    assert exc.value.detail["code"] == "ACTIVITIES_INCOMPLETE"
    with pytest.raises(HTTPException) as exc:
        await call(sessions, "complete", other, run["id"])
    assert exc.value.status_code == 404
    await evidence(sessions, owner, run, definition.nodes[0])
    assert (await call(sessions, "complete", owner, run["id"]))["exp_awarded"] == 10
    assert (await call(sessions, "complete", owner, run["id"]))["exp_awarded"] == 0
    assert (await call(sessions, "skip", owner, nodes[0].id))["status"] == "COMPLETED"
    for _ in range(2):
        request_id = uuid4()
        replay = await call(sessions, "start", owner, nodes[0].id, True, request_id)
        assert (await call(sessions, "start", owner, nodes[0].id, True, request_id))[
            "id"
        ] == replay["id"]
        await evidence(sessions, owner, replay, definition.nodes[0])
        assert (await call(sessions, "complete", owner, replay["id"]))["exp_awarded"] == 0
    async with sessions() as session:
        saved = (await session.scalars(select(Saved).where(Saved.user_id == owner))).one()
        assert saved.mastery_level == 0 and not saved.learning_activated
        assert not await session.scalar(
            select(SrsMemory.user_vocabulary_id).where(SrsMemory.user_vocabulary_id == saved.id)
        )
        assert (
            await session.scalar(
                select(func.count()).select_from(ExpGrant).where(ExpGrant.user_id == owner)
            )
            == 1
        )
    await call(sessions, "skip", owner, nodes[1].id)
    await call(sessions, "skip", owner, nodes[2].id)
    with pytest.raises(HTTPException) as exc:
        await call(sessions, "skip", owner, nodes[3].id)
    assert exc.value.detail["code"] == "REVIEW_GATE_REQUIRED"
    detail = await call(sessions, "detail", owner, nodes[3].id)
    assert "correct_option" not in detail["definition"]["lesson"]["activities"][0]
    review = await call(sessions, "start", owner, nodes[3].id)
    bad = ActivitySubmission(
        request_id=uuid4(),
        activity_id=definition.nodes[3].lesson.activities[0].id,
        kind="CHOICE",
        choice=1,
    )
    assert not (await call(sessions, "record", owner, review["id"], bad))["accepted"]
    with pytest.raises(HTTPException):
        await call(sessions, "complete", owner, review["id"])
    await evidence(sessions, owner, review, definition.nodes[3])
    assert (await call(sessions, "complete", owner, review["id"]))["exp_awarded"] == 15
    summary = await call(sessions, "summary", owner)
    assert summary == {"total_exp": 25, "completed_nodes": 2, "skipped_nodes": 2}
    assert (await call(sessions, "summary", other))["total_exp"] == 0
    async with sessions() as session:
        saved_after = (await session.scalars(select(Saved).where(Saved.user_id == owner))).one()
        assert saved_after.next_review_at == saved.next_review_at
        assert saved_after.mastery_level == saved.mastery_level
        assert not await session.scalar(
            select(SrsReviewAttempt.id).where(SrsReviewAttempt.user_vocabulary_id == saved.id)
        )


async def test_manually_saved_progress_and_historical_versions(curated_sessions, tmp_path):
    sessions = curated_sessions
    owner, _, definition, nodes, storage = await setup(sessions, tmp_path)
    word_id = definition.nodes[0].lesson.vocabulary[0].vocabulary_id
    async with sessions() as session:
        existing = await CuratedCatalog(session).save(owner, word_id)
    config = fsrs_scheduler.configuration()
    card, _ = fsrs_scheduler.review(None, Outcome.PASS, NOW, config)
    async with sessions() as session, session.begin():
        session.add(
            SrsMemory(
                user_vocabulary_id=existing.id,
                scheduler_version=fsrs_scheduler.VERSION,
                configuration=config,
                card=card,
                adopted_at=NOW,
            )
        )
        await session.execute(
            update(Saved)
            .where(Saved.id == existing.id)
            .values(
                mastery_level=3,
                phase="REVIEW",
                phase_step=0,
                next_review_at=NOW,
                learning_activated=True,
            )
        )
    run = await call(sessions, "start", owner, nodes[0].id)
    data = definition.model_dump(mode="json")
    data["version"] = 2
    data["nodes"][0]["title"] = "Phiên bản mới"
    newer = RoadmapDefinition.model_validate(data)
    async with sessions() as session:
        new_id = await import_draft(session, newer)
        await publish(session, new_id, storage, "Synthetic operator")
    old_detail = await call(sessions, "detail", owner, nodes[0].id)
    assert old_detail["definition"]["title"] == definition.nodes[0].title
    await evidence(sessions, owner, run, definition.nodes[0])
    await call(sessions, "complete", owner, run["id"])
    async with sessions() as session:
        saved = await session.get(Saved, existing.id)
        assert saved.mastery_level == 3 and saved.next_review_at == NOW and saved.learning_activated
        memory = await session.get(SrsMemory, existing.id)
        assert memory.card == card and memory.configuration == config
        progress = await session.get(NodeProgress, (owner, nodes[0].node_id))
        assert progress.first_completed_version_id == nodes[0].id
    async with sessions() as session:
        await activate(session, definition.id, None)
    assert not (await call(sessions, "browse", 0, 100))["items"]
    assert (await call(sessions, "detail", owner, nodes[0].id))["lesson_version_id"] == old_detail[
        "lesson_version_id"
    ]


async def test_publication_and_database_guards(curated_sessions, tmp_path):
    sessions = curated_sessions
    _owner, _, definition, nodes, storage = await setup(sessions, tmp_path)
    for model, identifier, changes in [
        (RoadmapVersion, version_id(definition), {"title": "tamper"}),
        (LessonVersion, nodes[0].lesson_version_id, {"engine_definition": {}}),
    ]:
        async with sessions() as session:
            with pytest.raises(IntegrityError):
                async with session.begin():
                    await session.execute(
                        update(model).where(model.id == identifier).values(**changes)
                    )
    invalid = draft([(definition.nodes[0].lesson.vocabulary[0].vocabulary_id, 1)])
    invalid.nodes[0].lesson.notes.status = "UNREVIEWED"
    async with sessions() as session:
        identifier = await import_draft(session, invalid)
        with pytest.raises(ContentError, match="unreviewed"):
            await publish(session, identifier, storage, "Synthetic operator")
    async with sessions() as session:
        assert (await session.get(RoadmapVersion, identifier)).status == "DRAFT"
    # Reusing a stable node for a different identity is rejected before any publication.
    data = definition.model_dump(mode="json")
    data["version"] = 3
    data["nodes"][0]["id"] = data["nodes"][1]["id"]
    data["nodes"][1]["id"] = str(uuid4())
    async with sessions() as session:
        with pytest.raises(ContentError, match="repurposed"):
            await import_draft(session, RoadmapDefinition.model_validate(data))


async def test_concurrent_completion(tmp_path):
    url = os.environ.get("ROADMAP_CONCURRENCY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ROADMAP_CONCURRENCY_TEST_DATABASE_URL to a dedicated migrated database")
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        owner, _, definition, nodes, _ = await setup(sessions, tmp_path)
        run = await call(sessions, "start", owner, nodes[0].id)
        await evidence(sessions, owner, run, definition.nodes[0])
        results = await asyncio.gather(
            *[call(sessions, "complete", owner, run["id"]) for _ in range(6)]
        )
        assert sum(r["exp_awarded"] for r in results) == 10
        async with sessions() as session:
            assert (
                await session.scalar(
                    select(func.count()).select_from(ExpGrant).where(ExpGrant.user_id == owner)
                )
                == 1
            )
            assert (
                await session.scalar(
                    select(func.count()).select_from(Saved).where(Saved.user_id == owner)
                )
                == 1
            )
    finally:
        await engine.dispose()


async def test_authenticated_http_flow_and_hidden_answers(
    curated_sessions, curated_client, tmp_path
):
    _owner, _, definition, nodes, _ = await setup(curated_sessions, tmp_path)
    client = curated_client
    headers = await register(client, "roadmap-http")
    second = await register(client, "roadmap-other-http")
    base = "/api/v1"
    response = await client.get(f"{base}/roadmaps/{definition.id}/nodes", headers=headers)
    assert response.status_code == 200 and response.json()["items"][0]["available"]
    response = await client.get(f"{base}/roadmap-nodes/{nodes[0].id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["vocabulary"][0]["content_version"] == 1
    assert response.json()["vocabulary"][0]["vietnamese_meanings"]
    response = await client.post(
        f"{base}/roadmap-nodes/{nodes[0].id}/start", json={}, headers=headers
    )
    assert response.status_code == 200
    run_id = response.json()["id"]
    response = await client.post(f"{base}/roadmap-runs/{run_id}/complete", headers=second)
    assert response.status_code == 404
    response = await client.post(
        f"{base}/roadmap-runs/{run_id}/activities",
        headers=headers,
        json={
            "request_id": str(uuid4()),
            "activity_id": str(definition.nodes[0].lesson.activities[0].id),
            "kind": "ACKNOWLEDGE",
        },
    )
    assert response.status_code == 200 and response.json()["accepted"]
    response = await client.post(f"{base}/roadmap-runs/{run_id}/complete", headers=headers)
    assert response.status_code == 200 and response.json()["exp_awarded"] == 10
    response = await client.get(f"{base}/me/roadmap-progress", headers=headers)
    assert response.status_code == 200 and response.json()["total_exp"] == 10
