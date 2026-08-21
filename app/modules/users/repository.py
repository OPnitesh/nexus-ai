from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import User
from app.shared.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User-specific database operations.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get an active user by email.
        """

        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        """
        Get all active users.
        """

        result = await self.db.execute(
            select(User).where(
                User.deleted_at.is_(None),
            )
        )

        return list(result.scalars().all())

    async def get_active_by_id(self, user_id) -> User | None:
        """
        Get an active user by ID.
        """

        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()