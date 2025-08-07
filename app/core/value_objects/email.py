import re
from dataclasses import dataclass
from typing import ClassVar


class InvalidEmailError(Exception):
    pass


@dataclass(frozen=True)
class Email:
    """Value object representing a validated email address."""

    value: str
    _EMAIL_PATTERN: ClassVar = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __post_init__(self):
        if not re.match(self._EMAIL_PATTERN, self.value):
            raise InvalidEmailError(f"Invalid email address {self.value}")
