
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.semantic_cache_model import SemanticCacheEntry


# Finds and stores cached responses using embedding similarity.
class SemanticCacheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_similar(
        self,
        embedding: list[float],
        model_name: str,
        context_hash: str,
        max_distance: float = 0.15,
    ) -> SemanticCacheEntry | None:
        distance = SemanticCacheEntry.embedding.cosine_distance(embedding)

        statement = (
            select(SemanticCacheEntry)
            .where(
                SemanticCacheEntry.model_name == model_name,
                SemanticCacheEntry.context_hash == context_hash,
                distance <= max_distance,
            )
            .order_by(distance)
            .limit(1)
        )

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def save(
        self,
        question: str,
        embedding: list[float],
        response: str,
        model_name: str,
        context_hash: str,
    ) -> SemanticCacheEntry:
        entry = SemanticCacheEntry(
            question=question,
            embedding=embedding,
            response=response,
            model_name=model_name,
            context_hash=context_hash,
        )

        self.session.add(entry)
        await self.session.flush()
        return entry
