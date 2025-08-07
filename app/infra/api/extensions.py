from typing import Dict

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def adapt_type_error(message: str) -> str:
    return message[message.index("missing") :].replace("positional argument", "field")


def adapt_message(error: Dict[str, str]) -> str:
    msg = error.get("msg", "")
    if msg and error.get("type") == "type_error":
        return adapt_type_error(msg)
    return msg


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        error.update({"msg": adapt_message(error)})
        errors.append(error)
    return JSONResponse({"detail": errors}, status_code=422)
