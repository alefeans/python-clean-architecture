from dataclasses import dataclass


class InvalidPasswordError(Exception):
    pass


@dataclass(frozen=True)
class Password:
    """Value object representing a password with length validation."""

    value: str
    _MIN_PASSWORD_LENGTH = 8
    _MAX_PASSWORD_LENGTH = 100

    def __post_init__(self):
        if not (self._MIN_PASSWORD_LENGTH <= len(self.value) <= self._MAX_PASSWORD_LENGTH):
            raise InvalidPasswordError(
                f"Password size must be between {self._MIN_PASSWORD_LENGTH} and {self._MAX_PASSWORD_LENGTH} characters"
            )
