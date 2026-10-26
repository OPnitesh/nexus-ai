
import hashlib
import json

from redis.asyncio import Redis


# Provides namespaced, expiring Redis storage for reusable AI responses.
class RedisCache:
    def __init__(self, client: Redis, namespace: str = "nexus:llm:cache"):
        self.client = client
        self.namespace = namespace

    def build_key(self, payload: dict) -> str:
        serialized_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        payload_hash = hashlib.sha256(
            serialized_payload.encode("utf-8")
        ).hexdigest()

        return f"{self.namespace}:{payload_hash}"

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        if ttl <= 0:
            raise ValueError("Cache TTL must be greater than zero")

        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
