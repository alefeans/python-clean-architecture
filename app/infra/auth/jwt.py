from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from app.core.dtos.auth import TokenResponse


class InvalidToken(Exception):
    pass


class JWTProvider:
    def __init__(self, secret_key: str, expire_minutes: int, algorithm: str) -> None:
        self._jwt = jwt
        self.secret_key = secret_key
        self.expire_minutes = expire_minutes
        self.algorithm = algorithm

    def decode(self, token: str) -> Dict[str, Any]:
        try:
            claims: Dict[str, Any] = self._jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return claims
        except JWTError:
            raise InvalidToken

    def create_access_token(self, data: Dict[str, Any]) -> TokenResponse:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        to_encode = {**data.copy(), "exp": expire}
        access_token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return TokenResponse(expire.timestamp(), access_token)

    def get_sub(self, token: str) -> str:
        _, sub = self.decode(token).get("sub", "").split(":")
        if not sub:
            raise InvalidToken
        return str(sub)
