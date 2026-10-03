import hashlib
import json

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, client: Redis):
        self.client = client

    @staticmethod
    def build_key(namespace: str, payload: dict) -> str:
        serialized_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        payload_hash = hashlib.sha256(
            serialized_payload.encode()
        ).hexdigest()

        return f"{namespace}:{payload_hash}"

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: int,
    ) -> None:
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)