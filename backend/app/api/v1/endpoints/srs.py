from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.authentication import Database, current_user_id
from app.schemas.review_engine import (
    ActiveTimeReceipt,
    DailyPlanRequest,
    FinalizedResponse,
    FinalizeReview,
    StageResponse,
    StageSubmission,
)
from app.schemas.srs import Dashboard, DueQueue, InitializeReview, ProgressDetail, ReviewSession
from app.services.review_engine import ReviewEngine
from app.services.srs import SrsService

router = APIRouter(prefix="/me/srs", tags=["SRS"])
Owner = Annotated[UUID, Depends(current_user_id)]


@router.get("/dashboard", response_model=Dashboard)
async def dashboard(owner: Owner, session: Database, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return await SrsService(session).dashboard(owner)


@router.get("/due", response_model=DueQueue)
async def due(
    owner: Owner,
    session: Database,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    response.headers["Cache-Control"] = "no-store"
    return await SrsService(session).due(owner, limit)


@router.get("/progress/{saved_id}", response_model=ProgressDetail)
async def progress(saved_id: UUID, owner: Owner, session: Database, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return await SrsService(session).progress(owner, saved_id)


@router.post("/sessions", response_model=ReviewSession, status_code=201)
async def initialize(body: InitializeReview, owner: Owner, session: Database, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return await SrsService(session).initialize(owner, body.saved_id, body.request_id)


@router.get(
    "/sessions/{attempt_id}/question",
    response_model=StageResponse,
    response_model_exclude_none=True,
)
async def question(attempt_id: UUID, owner: Owner, session: Database, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return await ReviewEngine(session).question(owner, attempt_id)


@router.post(
    "/sessions/{attempt_id}/submissions",
    response_model=StageResponse,
    response_model_exclude_none=True,
)
async def submit(
    attempt_id: UUID,
    body: StageSubmission,
    owner: Owner,
    session: Database,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"
    return await ReviewEngine(session).submit(owner, attempt_id, body)


@router.post("/sessions/{attempt_id}/finalize", response_model=FinalizedResponse)
async def finalize(
    attempt_id: UUID,
    body: FinalizeReview,
    owner: Owner,
    session: Database,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"
    return await ReviewEngine(session).finalize(owner, attempt_id)


@router.get("/review-targets")
async def review_targets(
    owner: Owner,
    session: Database,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    response.headers["Cache-Control"] = "no-store"
    return await ReviewEngine(session).targets_report(owner, limit, offset)


@router.post("/daily-plans")
async def daily_plan(body: DailyPlanRequest, owner: Owner, session: Database, response: Response):

    engine = ReviewEngine(session)
    response.headers["Cache-Control"] = "no-store"
    return await engine.planner().create(owner, body.request_id, body.continue_beyond_target)


@router.post("/sessions/{attempt_id}/active-time")
async def active_time(
    attempt_id: UUID, body: ActiveTimeReceipt, owner: Owner, session: Database, response: Response
):
    engine = ReviewEngine(session)
    response.headers["Cache-Control"] = "no-store"
    async with session.begin():
        attempt = await engine._locked(owner, attempt_id)
        if attempt.completed_at is None:
            engine._active(attempt)
        return await engine.planner().receipt(owner, attempt, body.active_ms)


@router.post("/sessions/{attempt_id}/defer")
async def defer_review(attempt_id: UUID, owner: Owner, session: Database, response: Response):
    engine = ReviewEngine(session)
    response.headers["Cache-Control"] = "no-store"
    async with session.begin():
        attempt = await engine._locked(owner, attempt_id)
        await engine.planner().defer(attempt)
    return {"deferred": True}
