from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config.settings import settings


def get_postgres_url() -> str:
    return settings.DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )


def create_checkpointer():
    return AsyncPostgresSaver.from_conn_string(
        get_postgres_url()
    )