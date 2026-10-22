from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select

from app.dependencies.authentication import Database, current_user_id
from app.models import Lesson, LessonRun, LessonVersion
from app.schemas.session import CheckpointInput, LessonMetadata, RunInfo, StartRun
from app.services import learning_access

router = APIRouter(tags=["learning"])
Identity = Annotated[UUID, Depends(current_user_id)]


@router.get("/lessons", response_model=list[LessonMetadata])
async def catalog(session: Database, user_id: Identity):
    rows = (
        await session.execute(
            select(Lesson, LessonVersion)
            .join(LessonVersion, LessonVersion.lesson_id == Lesson.id)
            .where(LessonVersion.status == "PUBLISHED")
            .order_by(Lesson.lesson_order, LessonVersion.version)
        )
    ).all()
    return [
        {
            "lesson_id": lesson.id,
            "lesson_version_id": version.id,
            "version": version.version,
            "title": version.title,
            "purpose": "CONTENT_PREVIEW",
            "learning_completion_supported": False,
        }
        for lesson, version in rows
    ]


@router.get("/lesson-versions/{version_id}/bundle", response_model=dict)
async def bundle(
    version_id: UUID, session: Database, user_id: Identity, allow_preview: bool = False
):
    return await learning_access.bundle(session, version_id, allow_preview)


@router.post("/learning-runs", status_code=201, response_model=RunInfo)
async def start(data: StartRun, session: Database, user_id: Identity):
    return await learning_access.start(session, user_id, data)


@router.get("/learning-runs", response_model=list[RunInfo])
async def runs(session: Database, user_id: Identity):
    rows = (
        await session.scalars(
            select(LessonRun)
            .where(LessonRun.user_id == user_id)
            .order_by(LessonRun.created_at.desc())
            .limit(100)
        )
    ).all()
    return [await learning_access.projection(session, run) for run in rows]


@router.get("/learning-runs/{run_id}", response_model=RunInfo)
async def resume(run_id: UUID, session: Database, user_id: Identity):
    return await learning_access.projection(
        session, await learning_access.owned_run(session, user_id, run_id)
    )


@router.put("/learning-runs/{run_id}/scenes/{scene_key}", response_model=RunInfo)
async def checkpoint(
    run_id: UUID, scene_key: UUID, data: CheckpointInput, session: Database, user_id: Identity
):
    return await learning_access.checkpoint(session, user_id, run_id, scene_key, data)


@router.get("/lesson-versions/{version_id}/assets/{asset_id}")
async def media(version_id: UUID, asset_id: UUID, session: Database, user_id: Identity):
    raw, media_type = await learning_access.media(session, version_id, asset_id)
    return Response(raw, media_type=media_type, headers={"Cache-Control": "no-store"})
