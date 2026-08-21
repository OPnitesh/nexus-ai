from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_verification_service,
)
from app.modules.auth.schema import (
    LoginRequest,
    ResendVerificationRequest,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.auth.verification_service import VerificationService
from app.modules.users.model import User
from app.modules.users.schema import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    token = await service.login(
        email=data.email,
        password=data.password,
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    token: str = Query(...),
    service: VerificationService = Depends(
        get_verification_service
    ),
):
    verified = await service.verify_email(token)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used verification token.",
        )

    return {
        "message": "Email verified successfully."
    }


@router.post(
    "/verify/resend",
    status_code=status.HTTP_200_OK,
)
async def resend_verification(
    data: ResendVerificationRequest,
    service: VerificationService = Depends(
        get_verification_service
    ),
):
    token = await service.resend_verification_by_email(
        data.email
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resend verification token.",
        )

    return {
        "message": "Verification token generated successfully."
    }