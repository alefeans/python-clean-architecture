from app.core.ports.unit_of_work import UnitOfWork
from app.infra.db import DBSession


class BaseUnitOfWork(UnitOfWork):
    def __init__(self, session: DBSession) -> None:
        self.session = session

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
