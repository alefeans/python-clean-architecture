from typing import Annotated

from fastapi import Depends

from app.core.usecases.user import (
    AuthenticateUserUsecase,
    CreateUserUsecase,
    DeleteUserUsecase,
    GetUserUsecase,
    UpdateUserUsecase,
)
from app.infra.api.dependencies.crypto import Hasher
from app.infra.api.dependencies.user import UnitOfWork, Repo


def get_create_user_usecase(uow: UnitOfWork, hasher: Hasher) -> CreateUserUsecase:
    return CreateUserUsecase(uow, hasher)


def get_get_user_usecase(repo: Repo) -> GetUserUsecase:
    return GetUserUsecase(repo)


def get_update_user_usecase(uow: UnitOfWork) -> UpdateUserUsecase:
    return UpdateUserUsecase(uow)


def get_delete_user_usecase(repo: Repo) -> DeleteUserUsecase:
    return DeleteUserUsecase(repo)


def get_authenticate_user_usecase(repo: Repo, hasher: Hasher) -> AuthenticateUserUsecase:
    return AuthenticateUserUsecase(repo, hasher)


CreateUser = Annotated[CreateUserUsecase, Depends(get_create_user_usecase)]
GetUser = Annotated[GetUserUsecase, Depends(get_get_user_usecase)]
UpdateUser = Annotated[UpdateUserUsecase, Depends(get_update_user_usecase)]
DeleteUser = Annotated[DeleteUserUsecase, Depends(get_delete_user_usecase)]
AuthenticateUser = Annotated[AuthenticateUserUsecase, Depends(get_authenticate_user_usecase)]
