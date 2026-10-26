from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import digest
from app.dependencies.database import get_session
from app.models import AuthSession
from app.services.authentication import unauthorized

bearer = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token",
    auto_error=False,
    description="Sign in with your account email in the username field and your password.",
)
Database = Annotated[AsyncSession, Depends(get_session)]


async def current_user_id(session: Database, credentials: Annotated[str | None, Depends(bearer)]):
    if not credentials:
        raise unauthorized()
    now = datetime.now(UTC)
    record = await session.scalar(
        select(AuthSession).where(
            AuthSession.access_hash == digest(credentials),
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
