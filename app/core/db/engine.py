from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config.settings import settings

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)