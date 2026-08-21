from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.dependencies import get_db
from app.modules.auth.dependencies import get_verification_service
from app.modules.auth.verification_service import VerificationService
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """
    Provide the user repository.
    """

    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    verification_service: VerificationService = Depends(
        get_verification_service
    ),
) -> UserService:
    """
    Provide the user service.
    """

    return UserService(
        repository=repository,
        verification_service=verification_service,
    )