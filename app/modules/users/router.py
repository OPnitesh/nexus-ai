from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import (
    require_role,
    require_user_or_admin,
)
from app.modules.users.dependencies import get_user_service
from app.modules.users.model import User, UserRole
from app.modules.users.schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()


@router.get(
    "/admin-only",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def admin_only(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(
        require_user_or_admin
    ),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: User = Depends(
        require_user_or_admin
    ),
    service: UserService = Depends(get_user_service),
):
    user = await service.update_user(
        user_id,
        data,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(
        require_user_or_admin
    ),
    service: UserService = Depends(get_user_service),
):
    user = await service.delete_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )