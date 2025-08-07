from dataclasses import dataclass

from app.core.dtos.user import UserResponse
from app.core.exceptions import UserNotFoundError
from app.core.ports.user import UserRepo
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class GetUserUsecase:
    user_repo: UserRepo

    async def execute(self, user_id: str) -> UserResponse:
        """Gets a user by ID.

        Args:
            user_id: The ID of the user to get.

        Returns:
            UserResponse: The user data.

        Raises:
            InvalidIDError: If the user ID format is invalid.
            UserNotFoundError: If the user is not found.
        """
        id_value = ID.from_string(user_id)

        user = await self.user_repo.get_by_id(id_value)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return UserResponse(id=str(user.id), name=user.name, email=user.email.value)
