from datetime import datetime, timedelta, timezone

from app.core.security.verification import generate_verification_token
from app.modules.auth.verification_model import EmailVerificationToken
from app.modules.auth.verification_repository import (
    VerificationTokenRepository,
)
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


class VerificationService:
    """
    Handles email verification business logic.
    """

    def __init__(
        self,
        verification_repository: VerificationTokenRepository,
        user_repository: UserRepository,
    ):
        self.verification_repository = verification_repository
        self.user_repository = user_repository

    async def create_verification_token(
        self,
        user: User,
    ) -> EmailVerificationToken:
        """
        Create a new verification token for a user.

        Any previously unused verification tokens are
        invalidated before creating the new token.
        """

        await self.verification_repository.invalidate_user_tokens(
            user.id
        )

        token = generate_verification_token()

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=30
        )

        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        # Temporary development logging.
        # Remove this when email delivery is implemented.
        print(f"EMAIL VERIFICATION TOKEN: {token}")

        return await self.verification_repository.create(
            verification_token
        )

    async def verify_email(
        self,
        token: str,
    ) -> bool:
        """
        Verify a user's email using a verification token.
        """

        verification_token = (
            await self.verification_repository.get_by_token(token)
        )

        if verification_token is None:
            return False

        if verification_token.used_at is not None:
            return False

        if verification_token.expires_at <= datetime.now(timezone.utc):
            return False

        user = await self.user_repository.get_by_id(
            verification_token.user_id
        )

        if user is None:
            return False

        user.is_verified = True

        verification_token.used_at = datetime.now(timezone.utc)

        await self.user_repository.update(user)

        await self.verification_repository.update(
            verification_token
        )

        return True

    async def resend_verification_token(
        self,
        user: User,
    ) -> EmailVerificationToken | None:
        """
        Create a new verification token for an unverified user.
        """

        if user.is_verified:
            return None

        return await self.create_verification_token(user)

    async def resend_verification_by_email(
        self,
        email: str,
    ) -> EmailVerificationToken | None:
        """
        Find a user by email and create a new verification
        token if the user is not verified.
        """

        user = await self.user_repository.get_by_email(email)

        if user is None:
            return None

        if user.is_verified:
            return None

        return await self.create_verification_token(user)