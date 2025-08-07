from typing import Protocol


class Hasher(Protocol):
    """Protocol for password hashing operations."""

    def hash(self, value: str) -> str:
        """Hash a plain text value.

        Args:
            value: Plain text to hash

        Returns:
            Hashed value
        """
        ...

    def verify(self, value: str, hashed: str) -> bool:
        """Verify a plain text value against a hash.

        Args:
            value: Plain text to verify
            hashed: Hashed value to compare against

        Returns:
            True if the value matches the hash, False otherwise
        """
        ...
