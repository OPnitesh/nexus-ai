from redis.asyncio import Redis


class RedisService:
    def __init__(self, client: Redis):
        self.client = client

    async def set(self, key: str, value: str) -> None:
        await self.client.set(key, value)

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)