from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.authentication import Database, current_user_id
from app.schemas.roadmap import (
    ActivitySubmission,
    CompletionResult,
    NodeDetail,
    NodePage,
    ProgressSummary,
    ReceiptResult,
    RoadmapPage,
    RunView,
    StartRequest,
)
from app.services.roadmap import RoadmapService

router = APIRouter(tags=["Roadmaps"])
Owner = Annotated[UUID, Depends(current_user_id)]
Limit = Annotated[int, Query(ge=1, le=100)]


@router.get("/roadmaps", response_model=RoadmapPage)
async def browse(
    owner: Owner, session: Database, limit: Limit = 20, offset: Annotated[int, Query(ge=0)] = 0
):
    return await RoadmapService(session).browse(offset, limit)


@router.get("/roadmaps/{roadmap_id}/nodes", response_model=NodePage)
async def nodes(
    roadmap_id: UUID,
    owner: Owner,
    session: Database,
    limit: Limit = 50,
    after: Annotated[int, Query(ge=-1)] = -1,
    version_id: UUID | None = None,
):
    return await RoadmapService(session).nodes(owner, roadmap_id, version_id, after, limit)


@router.get("/roadmap-nodes/{node_version_id}", response_model=NodeDetail)
async def detail(node_version_id: UUID, owner: Owner, session: Database):
    return await RoadmapService(session).detail(owner, node_version_id)


@router.post("/roadmap-nodes/{node_version_id}/start", response_model=RunView)
async def start(node_version_id: UUID, body: StartRequest, owner: Owner, session: Database):
    return await RoadmapService(session).start(owner, node_version_id, body.replay, body.request_id)


@router.get("/roadmap-nodes/{node_version_id}/assets/{asset_id}")
async def media(node_version_id: UUID, asset_id: UUID, owner: Owner, session: Database):
    raw, media_type = await RoadmapService(session).media(owner, node_version_id, asset_id)
    return Response(raw, media_type=media_type, headers={"Cache-Control": "no-store"})


@router.post("/roadmap-nodes/{node_version_id}/skip", response_model=CompletionResult)
async def skip(node_version_id: UUID, owner: Owner, session: Database):
    return await RoadmapService(session).skip(owner, node_version_id)


@router.post("/roadmap-runs/{run_id}/activities", response_model=ReceiptResult)
async def activity(run_id: UUID, body: ActivitySubmission, owner: Owner, session: Database):
    return await RoadmapService(session).record(owner, run_id, body)


@router.post("/roadmap-runs/{run_id}/complete", response_model=CompletionResult)
async def complete(run_id: UUID, owner: Owner, session: Database):
    return await RoadmapService(session).complete(owner, run_id)


@router.get("/me/roadmap-progress", response_model=ProgressSummary)
async def summary(owner: Owner, session: Database):
    return await RoadmapService(session).summary(owner)
