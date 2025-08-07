import pytest

from app.core.entities.user import User
from app.core.value_objects.email import Email, InvalidEmailError
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password, InvalidPasswordError


@pytest.fixture
def valid_data():
    return {
        "name": "Test",
        "email": Email("test@gmail.com"),
        "password": Password("password"),
    }


def test_if_generates_unique_id_for_new_users(valid_data):
    user1 = User(**valid_data, id=ID.generate())
    user2 = User(**valid_data, id=ID.generate())
    assert user1.id != user2.id


def test_if_raises_when_password_has_less_than_eight_characters():
    with pytest.raises(InvalidPasswordError):
        Password("small")


def test_if_raises_when_password_has_has_more_than_hundred_characters():
    with pytest.raises(InvalidPasswordError):
        Password("p" * 101)


@pytest.mark.parametrize(
    "invalid_email",
    [
        ("invalid"),
        ("@"),
        ("@.com"),
        ("bla.com"),
        ("@bla.com"),
    ],
)
def test_if_raises_when_email_is_invalid(invalid_email):
    with pytest.raises(InvalidEmailError):
        Email(invalid_email)
