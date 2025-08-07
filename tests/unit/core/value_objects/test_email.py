import pytest

from app.core.value_objects.email import Email, InvalidEmailError


def test_valid_email():
    email = Email("test@example.com")
    assert email.value == "test@example.com"


@pytest.mark.parametrize(
    "invalid_email",
    [
        "invalid",
        "@",
        "@.com",
        "bla.com",
        "@bla.com",
        "test@",
        "",
    ],
)
def test_invalid_email_raises_error(invalid_email):
    with pytest.raises(InvalidEmailError):
        Email(invalid_email)


def test_email_with_valid_formats():
    valid_emails = [
        "user@example.com",
        "test.email@domain.co.uk",
        "user123@test-domain.org",
        "user+tag@example.com",
        "user_name@example.com",
    ]

    for email_str in valid_emails:
        email = Email(email_str)
        assert email.value == email_str
