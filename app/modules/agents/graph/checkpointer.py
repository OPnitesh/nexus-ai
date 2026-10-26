from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config.settings import settings


# Creates and manages the PostgreSQL checkpointer for LangGraph.
@asynccontextmanager
async def create_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    postgres_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )

    async with AsyncPostgresSaver.from_conn_string(postgres_url) as checkpointer:
        await checkpointer.setup()
        yield checkpointer