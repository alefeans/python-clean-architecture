import pytest

from app.core.value_objects.password import Password, InvalidPasswordError


def test_valid_password():
    password = Password("validpassword")
    assert password.value == "validpassword"


def test_password_minimum_length():
    # 8 characters should be valid
    password = Password("12345678")
    assert password.value == "12345678"


def test_password_maximum_length():
    # 100 characters should be valid
    long_password = "a" * 100
    password = Password(long_password)
    assert password.value == long_password


def test_password_too_short():
    with pytest.raises(InvalidPasswordError) as exc_info:
        Password("short")  # 5 characters

    assert "Password size must be between 8 and 100 characters" in str(exc_info.value)


def test_password_too_long():
    with pytest.raises(InvalidPasswordError) as exc_info:
        Password("a" * 101)  # 101 characters

    assert "Password size must be between 8 and 100 characters" in str(exc_info.value)


def test_password_boundary_values():
    # Test exactly 7 characters (should fail)
    with pytest.raises(InvalidPasswordError):
        Password("1234567")

    # Test exactly 8 characters (should pass)
    Password("12345678")

    # Test exactly 100 characters (should pass)
    Password("a" * 100)

    # Test exactly 101 characters (should fail)
    with pytest.raises(InvalidPasswordError):
        Password("a" * 101)
