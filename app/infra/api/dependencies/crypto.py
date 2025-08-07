from typing import Annotated

from fastapi import Depends

from app.core.ports.crypto import Hasher as HasherProtocol
from app.infra.security import crypto


def get_hasher() -> crypto.Hasher:
    return crypto.Hasher()


Hasher = Annotated[HasherProtocol, Depends(get_hasher)]
