import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.models import Asset, LessonRun, LessonVersion, SceneCheckpoint
from app.services.content_files import ContentError
from app.services.content_storage import LocalContentStorage, verify_object


async def bundle(session, version_id: UUID, allow_preview: bool):
    version = await session.get(LessonVersion, version_id)
    if not version or version.status != "PUBLISHED":
        raise HTTPException(404, "Lesson unavailable")
    asset = await session.get(Asset, version.bundle_asset_id)
    settings = get_settings()
    try:
        raw = await run_in_threadpool(
            verify_object,
            LocalContentStorage(settings.content_storage_dir),
            asset.storage_key,
            asset.sha256,
            asset.byte_length,
        )
        result = json.loads(raw)
    except (ContentError, ValueError):
        raise HTTPException(503, "Lesson temporarily unavailable") from None
    if result["purpose"] == "CONTENT_PREVIEW" and not (
        settings.allow_content_preview and allow_preview
    ):
        raise HTTPException(403, "Preview access requires explicit opt-in")
    return result


async def owned_run(session, user_id, run_id):
    run = await session.scalar(
        select(LessonRun).where(LessonRun.id == run_id, LessonRun.user_id == user_id)
    )
    if not run:
        raise HTTPException(404, "Run unavailable")
    return run


async def projection(session, run):
    checkpoints = (
        await session.scalars(select(SceneCheckpoint).where(SceneCheckpoint.run_id == run.id))
    ).all()
    return {
        "id": run.id,
        "lesson_version_id": run.lesson_version_id,
        "learning_completion_supported": False,
        "checkpoints": [{"scene_key": item.scene_key, "page": item.page} for item in checkpoints],
    }


async def start(session, user_id, data):
    async with session.begin():
        await bundle(session, data.lesson_version_id, data.allow_preview)
        await session.execute(
            insert(LessonRun)
            .values(
                user_id=user_id,
                request_id=data.request_id,
                lesson_version_id=data.lesson_version_id,
            )
            .on_conflict_do_nothing(index_elements=["user_id", "request_id"])
        )
        run = await session.scalar(
            select(LessonRun).where(
                LessonRun.user_id == user_id, LessonRun.request_id == data.request_id
            )
        )
        if run.lesson_version_id != data.lesson_version_id:
            raise HTTPException(409, "Request identifier already used")
        return await projection(session, run)


async def checkpoint(session, user_id, run_id, scene_key, data):
    async with session.begin():
        run = await owned_run(session, user_id, run_id)
        content = await bundle(session, run.lesson_version_id, True)
        if str(scene_key) not in {s["scene_key"] for s in content["scenes"]}:
            raise HTTPException(404, "Scene unavailable")
        await session.execute(
            insert(SceneCheckpoint)
            .values(run_id=run.id, scene_key=scene_key, page=data.page)
            .on_conflict_do_update(index_elements=["run_id", "scene_key"], set_={"page": data.page})
        )
        return await projection(session, run)
