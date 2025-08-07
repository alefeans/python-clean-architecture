from typing import List, Optional

from passlib.context import CryptContext


class Hasher:
    def __init__(self, schemes: Optional[List[str]] = None) -> None:
        if not schemes:
            schemes = ["bcrypt"]
        self.context = CryptContext(schemes=schemes, deprecated=["auto"])

    def hash(self, value: str) -> str:
        hashed: str = self.context.hash(value)
        return hashed

    def verify(self, value: str, hashed: str) -> bool:
        result: bool = self.context.verify(value, hashed)
        return result
