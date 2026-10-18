from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Services own explicit transaction boundaries; closing rolls back uncommitted work."""
    async with session_factory() as session:
        yield session
