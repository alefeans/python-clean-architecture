from dataclasses import dataclass

from app.core.dtos.user import CreateUserRequest, UserResponse
from app.core.entities.user import User
from app.core.exceptions import InvalidUserError, UserAlreadyExistsError
from app.core.ports.crypto import Hasher
from app.core.ports.user import UserUnitOfWork
from app.core.value_objects.email import Email, InvalidEmailError
from app.core.value_objects.id import ID
from app.core.value_objects.password import InvalidPasswordError, Password
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class CreateUserUsecase:
    uow: UserUnitOfWork
    hasher: Hasher

    async def execute(self, dto: CreateUserRequest) -> UserResponse:
        """Creates a new user if the email doesn't already exist.

        Args:
            dto (CreateUserRequest): The data to create the user with.

        Returns:
            UserResponse: The created user.

        Raises:
            InvalidUserError: If the input data to create the user is invalid.
            UserAlreadyExistsError: If a user with the same email already exists.
        """
        try:
            email, password = Email(dto.email), Password(dto.password)
        except (InvalidEmailError, InvalidPasswordError) as e:
            logger.warning(f"Invalid user: {e}")
            raise InvalidUserError(str(e))

        async with self.uow:
            if await self.uow.user_repo.get_by_email(email):
                logger.warning(f"User with email {email.value} already exists")
                raise UserAlreadyExistsError(f"User with email {email.value} already exists")

            hashed_password = self.hasher.hash(password.value)
            user = User(
                id=ID.generate(),
                name=dto.name,
                email=email,
                password=Password(hashed_password),
            )

            await self.uow.user_repo.save(user)
            return UserResponse(id=str(user.id), name=user.name, email=user.email.value)
