from typing import Optional, Protocol

from app.core.entities.user import User
from app.core.value_objects.email import Email
from app.core.ports.unit_of_work import UnitOfWork
from app.core.value_objects.id import ID


class UserRepo(Protocol):
    """Protocol for user repository operations."""

    async def save(self, user: User) -> None:
        """Save a new user.

        Args:
            user: User entity to save
        """
        ...

    async def get_by_id(self, _id: ID) -> Optional[User]:
        """Get a user by ID.

        Args:
            _id: User ID

        Returns:
            User if found, None otherwise
        """
        ...

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get a user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        ...

    async def delete(self, _id: ID) -> bool:
        """Delete a user by ID.

        Args:
            _id: User ID

        Returns:
            True if deleted, False if not found
        """
        ...

    async def update(self, user: User) -> Optional[User]:
        """Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user if successful, None if not found
        """
        ...


class UserUnitOfWork(UnitOfWork, Protocol):
    """Unit of Work protocol for user operations."""

    user_repo: UserRepo
