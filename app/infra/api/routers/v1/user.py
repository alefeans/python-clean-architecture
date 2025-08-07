from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.dtos.user import CreateUserRequest, UpdateUser, UserResponse
from app.core.exceptions import InvalidUserError, UserAlreadyExistsError, UserNotFoundError
from app.core.value_objects.id import InvalidIDError
from app.core.value_objects.email import InvalidEmailError
from app.infra.api.dependencies.usecases.user import (
    CreateUser as CreateUserUsecase,
    DeleteUser as DeleteUserUsecase,
    GetUser as GetUserUsecase,
    UpdateUser as UpdateUserUsecase,
)

router = APIRouter()


@router.post(
    "",
    status_code=201,
    summary="Creates new User",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid user data"},
        409: {"description": "User already exists"},
    },
)
async def create(dto: CreateUserRequest, usecase: CreateUserUsecase) -> UserResponse:
    try:
        return await usecase.execute(dto)
    except (InvalidUserError, InvalidEmailError) as e:
        raise HTTPException(400, detail=str(e))
    except UserAlreadyExistsError:
        raise HTTPException(409, detail="User already exists")


@router.get(
    "/{user_id}",
    summary="Gets User information",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get(user_id: UUID, usecase: GetUserUsecase) -> UserResponse:
    try:
        return await usecase.execute(str(user_id))
    except InvalidIDError as e:
        raise HTTPException(status_code=422, detail=f"Invalid user ID: {e}")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Deletes User",
    responses={
        204: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
    },
)
async def delete(user_id: UUID, usecase: DeleteUserUsecase) -> None:
    if not await usecase.execute(str(user_id)):
        raise HTTPException(status_code=404, detail="User not found")


@router.patch(
    "/{user_id}",
    summary="Updates User information",
    responses={
        200: {"description": "User updated"},
        400: {"description": "Invalid user data"},
        404: {"description": "User not found"},
    },
)
async def patch(user_id: UUID, dto: UpdateUser, usecase: UpdateUserUsecase) -> UserResponse:
    try:
        return await usecase.execute(str(user_id), dto)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except (InvalidUserError, InvalidEmailError) as e:
        raise HTTPException(status_code=400, detail=str(e))
