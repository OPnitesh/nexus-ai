from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.engine import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)