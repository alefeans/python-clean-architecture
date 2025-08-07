from dataclasses import dataclass

from app.core.dtos.user import UserResponse
from app.core.exceptions import AuthenticationFailedError
from app.core.value_objects.email import Email, InvalidEmailError
from app.core.ports.crypto import Hasher
from app.core.ports.user import UserRepo
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class AuthenticateUserUsecase:
    user_repo: UserRepo
    hasher: Hasher

    async def execute(self, email_str: str, password_str: str) -> UserResponse:
        """Authenticates a user.

        Args:
            email_str: The user's email string.
            password_str: The user's password string.

        Returns:
            UserResponse: The authenticated user data.

        Raises:
            AuthenticationFailedError: If authentication fails.
        """
        try:
            email = Email(email_str)
        except InvalidEmailError:
            raise AuthenticationFailedError("Invalid credentials")

        user = await self.user_repo.get_by_email(email)
        if not user or not self.hasher.verify(password_str, user.password.value):
            raise AuthenticationFailedError("Invalid credentials")

        logger.info(f"User {email_str} authenticated successfully")
        return UserResponse(id=str(user.id), name=user.name, email=user.email.value)
