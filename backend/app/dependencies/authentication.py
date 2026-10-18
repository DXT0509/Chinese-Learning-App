from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import digest
from app.dependencies.database import get_session
from app.models import AuthSession
from app.services.authentication import unauthorized

bearer = HTTPBearer(auto_error=False)
Database = Annotated[AsyncSession, Depends(get_session)]


async def current_user_id(
    session: Database, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
):
    if not credentials:
        raise unauthorized()
    now = datetime.now(UTC)
    record = await session.scalar(
        select(AuthSession).where(
            AuthSession.access_hash == digest(credentials.credentials),
            AuthSession.revoked_at.is_(None),
            AuthSession.access_expires_at > now,
            AuthSession.expires_at > now,
        )
    )
    if not record:
        raise unauthorized()
    user_id = record.user_id
    await session.rollback()
    return user_id
