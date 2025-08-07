from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.config import get_settings
from app.core.dtos.user import UserResponse
from app.infra.api.dependencies.usecases.user import GetUser as GetUserUsecase
from app.infra.auth.jwt import InvalidToken, JWTProvider

CredentialsException = HTTPException(
    status_code=401,
    detail="Invalid Token",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_token_provider() -> JWTProvider:
    settings = get_settings()
    return JWTProvider(
        settings.JWT_SECRET_KEY,
        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        settings.JWT_ALGORITHM,
    )


TokenProvider = Annotated[JWTProvider, Depends(get_token_provider)]
Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
Oauth2Token = Annotated[str, Depends(Oauth2_scheme)]
Oauth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(
    usecase: GetUserUsecase, token: Oauth2Token, token_provider: TokenProvider
) -> UserResponse:
    try:
        _id = token_provider.get_sub(token)
    except InvalidToken:
        raise CredentialsException

    user = await usecase.execute(_id)
    if user is None:
        raise CredentialsException
    return user


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
