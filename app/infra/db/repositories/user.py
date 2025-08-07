from typing import Optional
from uuid import uuid4

from sqlmodel import select

from app.core.dtos.user import UserResponse
from app.core.entities.user import User
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password
from app.infra.db import DBSession
from app.infra.db.models.user import User as DBUser


class UserRepo:
    def __init__(self, session: DBSession) -> None:
        self.session = session

    def new_id(self) -> str:
        """Generate a new UUID string for user ID."""
        return str(uuid4())

    async def create(self, user: User) -> UserResponse:
        """Create a new user and return the response."""
        db_user = DBUser(
            id=user.id.value,
            name=user.name,
            email=user.email.value,
            password_hash=user.password.value,
        )
        self.session.add(db_user)
        return UserResponse(id=str(user.id), name=user.name, email=user.email.value)

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email address."""
        result = await self.session.exec(select(DBUser).where(DBUser.email == email.value))
        db_user = result.first()
        if not db_user:
            return None

        return User(
            id=ID.from_string(str(db_user.id)),
            name=db_user.name,
            email=Email(db_user.email),
            password=Password(db_user.password_hash),
        )

    async def save(self, user: User) -> None:
        """Save user (for backward compatibility)."""
        db_user = DBUser(
            id=user.id.value,
            name=user.name,
            email=user.email.value,
            password_hash=user.password.value,
        )
        self.session.add(db_user)

    async def get_by_id(self, _id: ID) -> Optional[User]:
        """Get user by ID."""
        db_user = await self.session.get(DBUser, _id.value)
        if not db_user:
            return None

        return User(
            id=ID.from_string(str(db_user.id)),
            name=db_user.name,
            email=Email(db_user.email),
            password=Password(db_user.password_hash),
        )

    async def delete(self, _id: ID) -> bool:
        """Delete user by ID."""
        db_user = await self.session.get(DBUser, _id.value)
        if not db_user:
            return False
        await self.session.delete(db_user)
        return True

    async def update(self, user: User) -> Optional[User]:
        """Update existing user."""
        to_update = await self.session.get(DBUser, user.id.value)
        if not to_update:
            return None

        to_update.name = user.name
        to_update.email = user.email.value
        self.session.add(to_update)
        return user
