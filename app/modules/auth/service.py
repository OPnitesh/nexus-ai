from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.users.model import User


class AuthService:
    """
    Handles authentication business logic.
    """

    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate a user using email and password.
        """

        user = await self.repository.get_user_by_email(email)

        if user is None:
            return None

        # Account must be active to log in.
        if not user.is_active:
            return None

        # Verify the plain password against the stored hash.
        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return user

    async def login(
        self,
        email: str,
        password: str,
    ) -> str | None:
        """
        Authenticate user and generate an access token.
        """

        user = await self.authenticate_user(
            email,
            password,
        )

        if user is None:
            return None

        return create_access_token(str(user.id))