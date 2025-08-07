"""Core domain exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class UserNotFoundError(DomainException):
    """Raised when a user is not found."""

    pass


class UserAlreadyExistsError(DomainException):
    """Raised when attempting to create a user that already exists."""

    pass


class AuthenticationFailedError(DomainException):
    """Raised when authentication fails."""

    pass


class InvalidUserError(DomainException):
    """Raised when user data is invalid."""

    pass
