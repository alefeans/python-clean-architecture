from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.dtos.user import CreateUserRequest, UpdateUser
from app.core.entities.user import User
from app.core.exceptions import (
    AuthenticationFailedError,
    InvalidUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.usecases.user import (
    AuthenticateUserUsecase,
    CreateUserUsecase,
    DeleteUserUsecase,
    GetUserUsecase,
    UpdateUserUsecase,
)
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password


@pytest.fixture
def create_user_dto():
    return CreateUserRequest(name="Test", email="test@test.com", password="password")


@pytest.fixture
def mock_user():
    """Create a mock user entity."""
    return User(
        id=ID.generate(),
        name="Test",
        email=Email("test@test.com"),
        password=Password("hashed_password"),
    )


@pytest.fixture
def mock_hasher():
    """Create a mock hasher."""
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    return hasher


@pytest.fixture
def mock_user_repo():
    """Create a mock user repository."""
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.delete = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_user_uow(mock_user_repo):
    """Create a mock unit of work."""
    uow = MagicMock()
    uow.user_repo = mock_user_repo
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


async def test_if_creates_user(mock_user_uow, mock_hasher, create_user_dto):
    mock_user_uow.user_repo.get_by_email.return_value = None

    use_case = CreateUserUsecase(uow=mock_user_uow, hasher=mock_hasher)
    result = await use_case.execute(create_user_dto)

    assert result.name == create_user_dto.name
    assert result.email == create_user_dto.email
    assert isinstance(result.id, str)

    mock_hasher.hash.assert_called_once_with("password")
    mock_user_uow.user_repo.save.assert_called_once()
    mock_user_uow.user_repo.get_by_email.assert_called_once()


async def test_if_validates_password_before_hashing(mock_user_uow, mock_hasher):
    user_small_password = CreateUserRequest(
        name="Test", email="test@test.com", password="small"
    )
    use_case = CreateUserUsecase(uow=mock_user_uow, hasher=mock_hasher)

    with pytest.raises(InvalidUserError):
        await use_case.execute(user_small_password)

    user_big_password = CreateUserRequest(
        name="Test", email="test@test.com", password="p" * 101
    )
    with pytest.raises(InvalidUserError):
        await use_case.execute(user_big_password)

    mock_hasher.hash.assert_not_called()


async def test_if_raises_when_creating_duplicated_user(
    mock_user_uow, mock_hasher, create_user_dto, mock_user
):
    mock_user_uow.user_repo.get_by_email.return_value = mock_user

    use_case = CreateUserUsecase(uow=mock_user_uow, hasher=mock_hasher)

    with pytest.raises(
        UserAlreadyExistsError, match=f"User with email {create_user_dto.email} already exists"
    ):
        await use_case.execute(create_user_dto)

    mock_user_uow.user_repo.save.assert_not_called()


async def test_if_get_user_by_id(mock_user_repo, mock_user):
    mock_user_repo.get_by_id.return_value = mock_user

    use_case = GetUserUsecase(user_repo=mock_user_repo)
    result = await use_case.execute(str(mock_user.id))

    assert result.id == str(mock_user.id)
    assert result.name == mock_user.name
    assert result.email == mock_user.email.value
    mock_user_repo.get_by_id.assert_called_once()


async def test_if_returns_none_when_getting_nonexisting_user(mock_user_repo):
    mock_user_repo.get_by_id.return_value = None

    use_case = GetUserUsecase(user_repo=mock_user_repo)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(str(uuid4()))

    mock_user_repo.get_by_id.assert_called_once()


async def test_if_returns_false_when_deleting_nonexisting_user(mock_user_repo):
    mock_user_repo.delete.return_value = False

    use_case = DeleteUserUsecase(user_repo=mock_user_repo)
    result = await use_case.execute(str(uuid4()))

    assert result is False
    mock_user_repo.delete.assert_called_once()


async def test_if_returns_true_when_deleting_existing_user(mock_user_repo):
    mock_user_repo.delete.return_value = True

    use_case = DeleteUserUsecase(user_repo=mock_user_repo)
    result = await use_case.execute(str(uuid4()))

    assert result is True
    mock_user_repo.delete.assert_called_once()


async def test_if_updates_user_name(mock_user_uow, mock_user):
    updated_user = User(
        id=mock_user.id,
        name="changed",
        email=mock_user.email,
        password=mock_user.password,
    )

    mock_user_uow.user_repo.get_by_id.return_value = mock_user
    mock_user_uow.user_repo.update.return_value = updated_user

    use_case = UpdateUserUsecase(uow=mock_user_uow)
    to_update = UpdateUser("changed")
    result = await use_case.execute(str(mock_user.id), to_update)

    assert result.name == "changed"
    assert result.id == str(mock_user.id)
    assert result.email == mock_user.email.value
    mock_user_uow.user_repo.update.assert_called_once()


async def test_if_updates_user_email(mock_user_uow, mock_user):
    updated_user = User(
        id=mock_user.id,
        name=mock_user.name,
        email=Email("changed@mail.com"),
        password=mock_user.password,
    )

    mock_user_uow.user_repo.get_by_id.return_value = mock_user
    mock_user_uow.user_repo.update.return_value = updated_user

    use_case = UpdateUserUsecase(uow=mock_user_uow)
    to_update = UpdateUser(email="changed@mail.com")
    result = await use_case.execute(str(mock_user.id), to_update)

    assert result.email == "changed@mail.com"
    assert result.id == str(mock_user.id)
    assert result.name == mock_user.name
    mock_user_uow.user_repo.update.assert_called_once()


async def test_if_fully_updates_user(mock_user_uow, mock_user):
    updated_user = User(
        id=mock_user.id,
        name="changed",
        email=Email("changed@mail.com"),
        password=mock_user.password,
    )

    mock_user_uow.user_repo.get_by_id.return_value = mock_user
    mock_user_uow.user_repo.update.return_value = updated_user

    use_case = UpdateUserUsecase(uow=mock_user_uow)
    to_update = UpdateUser("changed", email="changed@mail.com")
    result = await use_case.execute(str(mock_user.id), to_update)

    assert result.name == "changed"
    assert result.email == "changed@mail.com"
    assert result.id == str(mock_user.id)
    mock_user_uow.user_repo.update.assert_called_once()


async def test_if_keeps_password_unchanged_when_updating(mock_user_uow, mock_user):
    updated_user = User(
        id=mock_user.id,
        name="changed",
        email=mock_user.email,
        password=mock_user.password,
    )

    mock_user_uow.user_repo.get_by_id.return_value = mock_user
    mock_user_uow.user_repo.update.return_value = updated_user

    use_case = UpdateUserUsecase(uow=mock_user_uow)
    await use_case.execute(str(mock_user.id), UpdateUser("changed"))

    # Verify the update was called with the same password
    called_user = mock_user_uow.user_repo.update.call_args[0][0]
    assert called_user.password == mock_user.password


async def test_if_returns_none_when_updating_nonexisting_user(mock_user_uow):
    mock_user_uow.user_repo.get_by_id.return_value = None

    to_update = UpdateUser("changed", email="changed@mail.com")
    use_case = UpdateUserUsecase(uow=mock_user_uow)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(str(uuid4()), to_update)

    mock_user_uow.user_repo.update.assert_not_called()


async def test_if_authenticates_user(mock_user_repo, mock_hasher, mock_user):
    mock_user_repo.get_by_email.return_value = mock_user
    mock_hasher.verify.return_value = True

    use_case = AuthenticateUserUsecase(user_repo=mock_user_repo, hasher=mock_hasher)
    result = await use_case.execute("test@test.com", "password")

    assert result is not None
    assert result.id == str(mock_user.id)
    assert result.email == mock_user.email.value
    mock_hasher.verify.assert_called_once_with("password", mock_user.password.value)


async def test_if_returns_none_when_authenticating_nonexisting_user(
    mock_user_repo, mock_hasher
):
    mock_user_repo.get_by_email.return_value = None

    use_case = AuthenticateUserUsecase(user_repo=mock_user_repo, hasher=mock_hasher)

    with pytest.raises(AuthenticationFailedError):
        await use_case.execute("test@test.com", "password")

    mock_hasher.verify.assert_not_called()


async def test_if_returns_none_when_authenticating_with_invalid_password(
    mock_user_repo, mock_hasher, mock_user
):
    mock_user_repo.get_by_email.return_value = mock_user
    mock_hasher.verify.return_value = False

    use_case = AuthenticateUserUsecase(user_repo=mock_user_repo, hasher=mock_hasher)

    with pytest.raises(AuthenticationFailedError):
        await use_case.execute("test@test.com", "invalid_password")

    mock_hasher.verify.assert_called_once_with("invalid_password", mock_user.password.value)
