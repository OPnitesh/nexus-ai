from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import User


class AuthRepository:
    """
    Handles database operations required for authentication.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Get an active user by email for authentication.
        """

        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
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