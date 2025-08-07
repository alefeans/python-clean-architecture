from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class CreateUserRequest:
    name: str
    email: str
    password: str


@dataclass(frozen=True, kw_only=True)
class UserResponse:
    id: str
    name: str
    email: str


@dataclass(frozen=True)
class UpdateUser:
    name: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        if not self.name and not self.email:
            raise ValueError("At least one field must be provided")
