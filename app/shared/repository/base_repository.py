from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic repository for common database operations.
    """

    def __init__(
        self,
        db: AsyncSession,
        model: type[ModelType],
    ):
        self.db = db
        self.model = model

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new database record.
        """

        self.db.add(obj)

        await self.db.commit()

        await self.db.refresh(obj)

        return obj

    async def get_by_id(self, id):
        """
        Get a record by its primary key.
        """

        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )

        return result.scalar_one_or_none()

    
    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing database record.
        """

        await self.db.commit()

        await self.db.refresh(obj)

        return obj
    
    async def delete(self, obj: ModelType) -> None:
        """
        Delete an existing database record.
        """

        await self.db.delete(obj)

        await self.db.commit()