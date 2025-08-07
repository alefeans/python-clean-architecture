from dataclasses import dataclass

from app.core.exceptions import InvalidUserError
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password


@dataclass(frozen=True, kw_only=True)
class User:
    id: ID
    name: str
    email: Email
    password: Password

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise InvalidUserError("Name cannot be empty")
