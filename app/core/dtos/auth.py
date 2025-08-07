from dataclasses import dataclass


@dataclass(frozen=True)
class TokenResponse:
    expire: float
    access_token: str
    token_type: str = "bearer"
