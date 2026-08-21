from datetime import datetime, timezone

from app.core.exceptions import EmailAlreadyExistsError
from app.core.security.password import hash_password
from app.modules.auth.verification_service import VerificationService
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserUpdate


class UserService:
    """
    Handles user business logic.
    """

    def __init__(
        self,
        repository: UserRepository,
        verification_service: VerificationService,
    ):
        self.repository = repository
        self.verification_service = verification_service

    async def create_user(self, data: UserCreate) -> User:
        """
        Create a new user and generate an email verification token.
        """

        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise EmailAlreadyExistsError(
                "A user with this email already exists."
            )

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )

        user = await self.repository.create(user)

        await self.verification_service.create_verification_token(user)

        return user

    async def get_user_by_id(
        self,
        user_id,
    ) -> User | None:
        """
        Get an active user by ID.
        """

        return await self.repository.get_active_by_id(user_id)

    async def get_all_users(self) -> list[User]:
        """
        Get all active users.
        """

        return await self.repository.get_all()

    async def update_user(
        self,
        user_id,
        data: UserUpdate,
    ) -> User | None:
        """
        Update an existing user.
        """

        user = await self.repository.get_active_by_id(user_id)

        if user is None:
            return None

        if data.email is not None and data.email != user.email:
            existing_user = await self.repository.get_by_email(data.email)

            if existing_user:
                raise EmailAlreadyExistsError(
                    "A user with this email already exists."
                )

        if data.first_name is not None:
            user.first_name = data.first_name

        if data.last_name is not None:
            user.last_name = data.last_name

        if data.email is not None:
            user.email = data.email

        return await self.repository.update(user)

    async def delete_user(
        self,
        user_id,
    ) -> User | None:
        """
        Soft delete a user.
        """

        user = await self.repository.get_active_by_id(user_id)

        if user is None:
            return None

        user.deleted_at = datetime.now(timezone.utc)

        return await self.repository.update(user)