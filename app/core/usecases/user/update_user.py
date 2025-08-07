from dataclasses import dataclass

from app.core.dtos.user import UpdateUser, UserResponse
from app.core.entities.user import User
from app.core.exceptions import UserNotFoundError
from app.core.ports.user import UserUnitOfWork
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class UpdateUserUsecase:
    uow: UserUnitOfWork

    async def execute(self, user_id: str, dto: UpdateUser) -> UserResponse:
        """Updates a user.

        Args:
            user_id: The ID of the user to update.
            dto: The data to update the user with.

        Returns:
            UserResponse: The updated user data.

        Raises:
            InvalidIDError: If the user ID format is invalid.
            InvalidEmailError: If the email format is invalid.
            UserNotFoundError: If the user is not found.
        """
        id_value = ID.from_string(user_id)

        async with self.uow:
            existing_user = await self.uow.user_repo.get_by_id(id_value)
            if not existing_user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            updated_user = await self.uow.user_repo.update(
                User(
                    id=existing_user.id,
                    name=dto.name or existing_user.name,
                    email=Email(dto.email) if dto.email else existing_user.email,
                    password=existing_user.password,
                )
            )

            if not updated_user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            logger.info(f"User {user_id} updated successfully")
            return UserResponse(
                id=str(updated_user.id),
                name=updated_user.name,
                email=updated_user.email.value,
            )
