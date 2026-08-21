from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates one database session per request
    and automatically closes it after the request finishes.
    """

    async with AsyncSessionLocal() as session:
        yield session