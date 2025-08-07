from fastapi import APIRouter, HTTPException

from app.core.dtos.auth import TokenResponse
from app.core.dtos.user import UserResponse
from app.core.usecases.user.authenticate_user import AuthenticationFailedError
from app.infra.api.dependencies.auth import CurrentUser, Oauth2Form, TokenProvider
from app.infra.api.dependencies.usecases.user import (
    AuthenticateUser as AuthenticateUserUsecase,
)

router = APIRouter()


@router.post(
    "/token",
    summary="Creates access Token",
    responses={
        200: {"description": "User authenticated"},
        401: {"description": "User unauthorized"},
    },
    operation_id="Credentials",
)
async def token(
    usecase: AuthenticateUserUsecase, form_data: Oauth2Form, token_provider: TokenProvider
) -> TokenResponse:
    try:
        user = await usecase.execute(form_data.username, form_data.password)
        return token_provider.create_access_token({"sub": f"user_id:{user.id}"})
    except AuthenticationFailedError:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    summary="Gets authenticated User information",
    responses={
        200: {"description": "User info"},
        401: {"description": "User unauthorized"},
    },
)
async def get_current_user(current_user: CurrentUser) -> UserResponse:
    return current_user
