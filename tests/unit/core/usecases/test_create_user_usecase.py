from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from app.core.dtos.user import CreateUserRequest, UserResponse
from app.core.entities.user import User
from app.core.exceptions import InvalidUserError, UserAlreadyExistsError
from app.core.usecases.user.create_user import CreateUserUsecase
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password


@pytest.fixture
def mock_repo():
    """Create a mock user repository."""
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_uow(mock_repo):
    """Create a mock unit of work."""
    uow = MagicMock()
    uow.user_repo = mock_repo
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_hasher():
    """Create a mock hasher."""
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    return hasher


@pytest.fixture
def use_case(mock_uow, mock_hasher):
    return CreateUserUsecase(uow=mock_uow, hasher=mock_hasher)


@pytest.fixture
def valid_dto():
    return CreateUserRequest(
        name="John Doe", email="john@example.com", password="validpassword123"
    )


async def test_create_user_success(use_case, valid_dto, mock_uow, mock_hasher):
    """Test successful user creation."""
    result = await use_case.execute(valid_dto)

    assert isinstance(result, UserResponse)
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert isinstance(result.id, str)
    assert uuid.UUID(result.id)  # Verify it's a valid UUID string

    mock_hasher.hash.assert_called_once_with("validpassword123")
    mock_uow.user_repo.save.assert_called_once()

    # Verify the saved user has correct attributes
    saved_user = mock_uow.user_repo.save.call_args[0][0]
    assert isinstance(saved_user, User)
    assert saved_user.name == "John Doe"
    assert saved_user.email.value == "john@example.com"
    assert saved_user.password.value == "hashed_password"


async def test_create_user_invalid_email(use_case):
    """Test user creation with invalid email."""
    invalid_dto = CreateUserRequest(
        name="John Doe", email="invalid-email", password="validpassword123"
    )

    with pytest.raises(InvalidUserError, match="Invalid email"):
        await use_case.execute(invalid_dto)


async def test_create_user_invalid_password(use_case):
    """Test user creation with invalid password."""
    invalid_dto = CreateUserRequest(
        name="John Doe", email="john@example.com", password="short"
    )

    with pytest.raises(InvalidUserError, match="Password size must be between"):
        await use_case.execute(invalid_dto)


async def test_create_user_already_exists(use_case, valid_dto, mock_uow):
    """Test user creation when email already exists."""
    # Mock that a user with this email already exists
    existing_user = User(
        id=ID.generate(),
        name="Existing User",
        email=Email("john@example.com"),
        password=Password("hashedpassword"),
    )
    mock_uow.user_repo.get_by_email.return_value = existing_user

    with pytest.raises(
        UserAlreadyExistsError, match="User with email john@example.com already exists"
    ):
        await use_case.execute(valid_dto)

    mock_uow.user_repo.save.assert_not_called()


async def test_create_user_empty_name(use_case):
    """Test user creation with empty name."""
    invalid_dto = CreateUserRequest(
        name="", email="john@example.com", password="validpassword123"
    )

    # This should raise InvalidUserError when User entity validates the name
    with pytest.raises(InvalidUserError):
        await use_case.execute(invalid_dto)


async def test_create_user_empty_password(use_case):
    """Test user creation with empty password."""
    invalid_dto = CreateUserRequest(name="John Doe", email="john@example.com", password="")

    with pytest.raises(
        InvalidUserError, match="Password size must be between 8 and 100 characters"
    ):
        await use_case.execute(invalid_dto)


async def test_create_user_repository_called_correctly(
    use_case, valid_dto, mock_uow, mock_hasher
):
    """Test that repository methods are called with correct parameters."""
    await use_case.execute(valid_dto)

    # Verify repository interactions
    mock_uow.user_repo.get_by_email.assert_called_once()
    email_arg = mock_uow.user_repo.get_by_email.call_args[0][0]
    assert isinstance(email_arg, Email)
    assert email_arg.value == "john@example.com"

    mock_uow.user_repo.save.assert_called_once()
    saved_user = mock_uow.user_repo.save.call_args[0][0]
    assert isinstance(saved_user, User)
    assert saved_user.name == "John Doe"
    assert saved_user.email.value == "john@example.com"
    assert saved_user.password.value == "hashed_password"
    assert isinstance(saved_user.id.value, uuid.UUID)
