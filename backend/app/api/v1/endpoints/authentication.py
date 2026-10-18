from collections import OrderedDict
from time import monotonic
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.dependencies.authentication import Database, current_user_id
from app.models import User
from app.schemas.session import Credentials, RefreshInput, Tokens, UserInfo
from app.services.authentication import authenticate, rotate

# Bounded, single-process local-development throttle. Deploy with one worker until
# an ingress/shared limiter is configured. Never trust forwarded client headers.
attempts: OrderedDict[str, tuple[float, int]] = OrderedDict()


async def rate_limit(request: Request):
    now = monotonic()
    key = request.client.host if request.client else "unknown"
    start, count = attempts.pop(key, (now, 0))
    if now - start >= 60:
        start, count = now, 0
    attempts[key] = (start, count + 1)
    if len(attempts) > 10000:
        attempts.popitem(last=False)
    if count >= 20:
        raise HTTPException(429, "Too many attempts", headers={"Retry-After": "60"})


router = APIRouter(prefix="/auth", tags=["authentication"], dependencies=[Depends(rate_limit)])


@router.post("/register", response_model=Tokens, status_code=201)
async def register(data: Credentials, session: Database):
    return await authenticate(session, data, register=True)


@router.post("/login", response_model=Tokens)
async def login(data: Credentials, session: Database):
    return await authenticate(session, data, register=False)


@router.post("/refresh", response_model=Tokens)
async def refresh(data: RefreshInput, session: Database):
    return await rotate(session, data.refresh_token.get_secret_value())


@router.post("/logout", status_code=204)
async def logout(data: RefreshInput, session: Database):
    await rotate(session, data.refresh_token.get_secret_value(), logout=True)
    return Response(status_code=204)


@router.get("/me", response_model=UserInfo)
async def me(session: Database, user_id: Annotated[UUID, Depends(current_user_id)]):
    return await session.get(User, user_id)
