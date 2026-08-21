from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.dependencies import get_db
from app.core.security.jwt import decode_access_token
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService
from app.modules.auth.verification_repository import (
    VerificationTokenRepository,
)
from app.modules.auth.verification_service import VerificationService
from app.modules.users.model import User, UserRole
from app.modules.users.repository import UserRepository


bearer_scheme = HTTPBearer()


def get_auth_repository(
    db: AsyncSession = Depends(get_db),
) -> AuthRepository:
    return AuthRepository(db)


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the currently authenticated user from the JWT.
    """

    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repository = AuthRepository(db)

    user = await repository.get_user_by_id(user_uuid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(required_role: UserRole):
    """
    Require the current user to have a specific role.
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker


async def require_user_or_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow access if the current user is the requested user
    or an ADMIN.
    """

    if (
        current_user.id != user_id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user.",
        )

    return current_user


def get_verification_repository(
    db: AsyncSession = Depends(get_db),
) -> VerificationTokenRepository:
    """
    Provide the verification token repository.
    """

    return VerificationTokenRepository(db)


def get_verification_service(
    verification_repository: VerificationTokenRepository = Depends(
        get_verification_repository
    ),
    db: AsyncSession = Depends(get_db),
) -> VerificationService:
    """
    Provide the verification service.
    """

    user_repository = UserRepository(db)

    return VerificationService(
        verification_repository=verification_repository,
        user_repository=user_repository,
    )