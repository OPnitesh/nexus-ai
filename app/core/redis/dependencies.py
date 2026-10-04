from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.redis.client import redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:
    yield redis_client