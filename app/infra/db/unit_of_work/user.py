from app.infra.db import DBSession
from app.infra.db.repositories.user import UserRepo
from app.infra.db.unit_of_work.base import BaseUnitOfWork


class UserUnitOfWork(BaseUnitOfWork):
    def __init__(self, session: DBSession) -> None:
        super().__init__(session)
        self.user_repo = UserRepo(session)


def user_uow_factory(session: DBSession) -> UserUnitOfWork:
    return UserUnitOfWork(session)
