from typing import Protocol


class UnitOfWork(Protocol):
    """Protocol for Unit of Work pattern implementation.

    Manages database transactions, ensuring all operations
    within a unit either complete successfully or roll back.
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self): ...

    async def rollback(self): ...
