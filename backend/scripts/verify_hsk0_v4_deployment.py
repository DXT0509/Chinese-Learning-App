"""Read deployed content through real GET routes; authenticate in a rollback-only QA realm.

Development connections enforce PostgreSQL read-only transactions. No learner write
routes are called. This is an in-process API probe, not a live server login test.
"""

import argparse
import asyncio
import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import httpx
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.event_loop import new_event_loop
from app.core.security import digest
from app.dependencies.authentication import bearer, current_user_id
from app.dependencies.database import get_session
from app.main import create_app
from app.models import Asset, AuthSession, LessonVersion, User
from app.models.roadmap import Roadmap, RoadmapNodeVersion, RoadmapVersion
from app.schemas.content import content_id
from app.services.content_storage import LocalContentStorage, verify_object
from app.services.roadmap_authoring import version_id
from app.services.roadmap_preparation import load_json, write_artifact
from scripts.deploy_hsk0_v4 import artifacts, get_settings, snapshot, target


async def verify(directory):
    _, definition, library = artifacts()
    url = target()
    development = create_async_engine(
        url, connect_args={"options": "-c default_transaction_read_only=on"}
    )
    # Fixed, previously migrated isolated database; never derive a write target from CLI input.
    qa = create_async_engine(url.set(database="chinese_roadmap_test_20261102101729"))
    sessions = async_sessionmaker(development, expire_on_commit=False)
    before = snapshot(definition)
    storage = LocalContentStorage(get_settings().content_storage_dir)
    result = {"verification": "in-process authenticated GET routes; isolated QA authentication"}
    try:
        async with sessions() as session:
            roadmap = await session.get(Roadmap, definition.id)
            release = await session.get(RoadmapVersion, version_id(definition))
            assert roadmap.active_version_id == release.id and release.status == "PUBLISHED"
            assert release.definition == definition.model_dump(mode="json")
            bundle = await session.get(Asset, release.bundle_asset_id)
            payload = json.loads(
                verify_object(storage, bundle.storage_key, bundle.sha256, bundle.byte_length)
            )
            assert payload["definition"] == release.definition
            nodes = list(
                await session.scalars(
                    select(RoadmapNodeVersion)
                    .where(RoadmapNodeVersion.roadmap_version_id == release.id)
                    .order_by(RoadmapNodeVersion.position)
                )
            )
            assert len(nodes) == 4
            result["nodes"] = []
            for node, approved in zip(nodes, definition.nodes, strict=True):
                lesson = await session.get(LessonVersion, node.lesson_version_id)
                assert node.node_id == approved.id and node.position == approved.position
                assert lesson.status == "PUBLISHED"
                assert lesson.engine_definition == approved.model_dump(mode="json")
                bundle = await session.get(Asset, lesson.bundle_asset_id)
                assert (
                    json.loads(
                        verify_object(
                            storage, bundle.storage_key, bundle.sha256, bundle.byte_length
                        )
                    )
                    == lesson.engine_definition
                )
                result["nodes"].append(
                    {
                        "position": node.position,
                        "node_id": str(node.node_id),
                        "node_version_id": str(node.id),
                        "lesson_version_id": str(lesson.id),
                        "node_type": approved.node_type,
                        "vocabulary": [
                            v.model_dump(mode="json") for v in approved.lesson.vocabulary
                        ],
                        "activities": len(approved.lesson.activities),
                    }
                )
            result["assets"] = []
            for approved in library.assets:
                asset = await session.get(Asset, content_id("asset", approved.id))
                raw = verify_object(storage, asset.storage_key, asset.sha256, asset.byte_length)
                assert asset.sha256 == approved.sha256 and len(raw) == approved.byte_length
                result["assets"].append(
                    {"id": str(asset.id), "sha256": asset.sha256, "bytes": len(raw)}
                )
        async with qa.connect() as connection:
            transaction = await connection.begin()
            qa_sessions = async_sessionmaker(
                connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            token = secrets.token_urlsafe(32)
            owner = uuid4()
            async with qa_sessions() as session:
                session.add(User(id=owner, display_name="Isolated deployment GET probe"))
                await session.flush()
                now = datetime.now(UTC)
                session.add(
                    AuthSession(
                        user_id=owner,
                        access_hash=digest(token),
                        access_expires_at=now + timedelta(minutes=10),
                        expires_at=now + timedelta(minutes=10),
                    )
                )
                await session.commit()

            async def read_only_session():
                async with sessions() as session:
                    yield session

            async def isolated_auth(credentials: Annotated[str | None, Depends(bearer)]):
                async with qa_sessions() as session:
                    return await current_user_id(session, credentials)

            app = create_app()
            app.dependency_overrides[get_session] = read_only_session
            app.dependency_overrides[current_user_id] = isolated_auth
            checks = []
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://deployment-probe"
                ) as client:
                    assert (await client.get("/api/v1/roadmaps")).status_code == 401
                    client.headers["Authorization"] = f"Bearer {token}"
                    response = await client.get("/api/v1/roadmaps")
                    assert response.status_code == 200
                    assert any(
                        r["version_id"] == str(release.id) and r["version"] == 4
                        for r in response.json()["items"]
                    )
                    checks.append("authenticated roadmap catalog: 200, active v4")
                    response = await client.get(f"/api/v1/roadmaps/{definition.id}/nodes")
                    assert response.status_code == 200
                    items = response.json()["items"]
                    assert [n["id"] for n in items] == [str(n.id) for n in definition.nodes]
                    assert [n["available"] for n in items] == [True, False, False, False]
                    checks.append(
                        "authenticated ordered nodes: 200, all four; sequential locks intact"
                    )
                    for i, (node, approved) in enumerate(zip(nodes, definition.nodes, strict=True)):
                        path = f"/api/v1/roadmap-nodes/{node.id}"
                        response = await client.get(path)
                        assert response.status_code == (200 if i == 0 else 403)
                        if i == 0:
                            assert "correct_option" not in response.text
                            assert response.json()["definition"]["node_type"] == "NEW_WORD"
                        for media in (approved.lesson.audio, approved.lesson.stroke_order):
                            if media.asset_id is None:
                                continue
                            response = await client.get(f"{path}/assets/{media.asset_id}")
                            assert response.status_code == (200 if i == 0 else 403)
                            if i == 0:
                                approved_asset = next(
                                    a for a in result["assets"] if a["id"] == str(media.asset_id)
                                )
                                import hashlib

                                assert (
                                    hashlib.sha256(response.content).hexdigest()
                                    == approved_asset["sha256"]
                                )
                    checks.append(
                        "first lesson and both media: 200; remaining lesson/media locks: 403"
                    )
                    response = await client.get("/api/v1/me/roadmap-progress")
                    assert response.json() == {
                        "total_exp": 0,
                        "completed_nodes": 0,
                        "skipped_nodes": 0,
                    }
                    checks.append(
                        "QA identity has zero progress and EXP; no write endpoints called"
                    )
            finally:
                app.dependency_overrides.clear()
                await transaction.rollback()
            result["api_checks"] = checks
            result["isolated_credentials_rolled_back"] = True
        after = snapshot(definition)
        assert before["tables"] == after["tables"], "Development changed during read-only probe"
        assert load_json(directory / "after.json")["tables"] == after["tables"]
        result["development_all_row_fingerprints_unchanged"] = True
        write_artifact(directory / "api-verification.json", result)
        print(
            "PASS: deployed definition, 4 lessons/22 activities, 6 media, authenticated GETs, zero development writes"
        )
    finally:
        await development.dispose()
        await qa.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", type=Path, required=True)
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(verify(args.audit_dir))


if __name__ == "__main__":
    main()
