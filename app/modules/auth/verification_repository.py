from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.verification_model import EmailVerificationToken


class VerificationTokenRepository:
    """
    Handles database operations for email verification tokens.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        verification_token: EmailVerificationToken,
    ) -> EmailVerificationToken:
        """
        Create a verification token.
        """

        self.db.add(verification_token)

        await self.db.commit()
        await self.db.refresh(verification_token)

        return verification_token

    async def get_by_token(
        self,
        token: str,
    ) -> EmailVerificationToken | None:
        """
        Get a verification token by its token value.
        """

        result = await self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token == token,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> EmailVerificationToken | None:
        """
        Get the latest verification token for a user.
        """

        result = await self.db.execute(
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
            )
            .order_by(
                EmailVerificationToken.created_at.desc(),
            )
        )

        return result.scalars().first()

    async def invalidate_user_tokens(
        self,
        user_id: UUID,
    ) -> None:
        """
        Invalidate all unused verification tokens
        belonging to a user.
        """

        result = await self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
        )

        tokens = result.scalars().all()

        for token in tokens:
            token.used_at = datetime.now(timezone.utc)

        await self.db.commit()

    async def update(
        self,
        verification_token: EmailVerificationToken,
    ) -> EmailVerificationToken:
        """
        Update a verification token.
        """

        await self.db.commit()
        await self.db.refresh(verification_token)

        return verification_token