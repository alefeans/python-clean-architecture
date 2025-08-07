from dataclasses import dataclass

from app.core.ports.user import UserRepo
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class DeleteUserUsecase:
    user_repo: UserRepo

    async def execute(self, user_id: str) -> bool:
        """Deletes a user.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if the user was deleted, False otherwise.

        Raises:
            InvalidIDError: If the user ID format is invalid.
        """
        id_value = ID.from_string(user_id)

        result = await self.user_repo.delete(id_value)
        if result:
            logger.info(f"User {user_id} deleted successfully")
        return result
