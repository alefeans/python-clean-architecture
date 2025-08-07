from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


class InvalidIDError(Exception):
    pass


@dataclass(frozen=True)
class ID:
    """Value object representing a unique identifier (UUID)."""

    value: UUID

    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create an ID from a UUID string.

        Raises:
            InvalidIDError: If the string is not a valid UUID
        """
        try:
            return cls(UUID(value))
        except (ValueError, TypeError) as e:
            raise InvalidIDError(f"Invalid UUID: {value}") from e

    @classmethod
    def generate(cls) -> Self:
        """Generate a new UUID-based ID"""
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)
