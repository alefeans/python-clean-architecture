from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.core.ports import user
from app.infra.db import async_session
from app.infra.db.repositories.user import UserRepo
from app.infra.db.unit_of_work.user import user_uow_factory


async def get_user_repo() -> AsyncGenerator[user.UserRepo, None]:
    async with async_session() as session:
        yield UserRepo(session)


async def get_user_uow() -> AsyncGenerator[user.UserUnitOfWork, None]:
    async with async_session() as session:
        yield user_uow_factory(session)  # type: ignore[misc]


Repo = Annotated[user.UserRepo, Depends(get_user_repo)]
UnitOfWork = Annotated[user.UserUnitOfWork, Depends(get_user_uow)]
