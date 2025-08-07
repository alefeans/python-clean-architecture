from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.config import Settings
from app.infra.api.extensions import validation_exception_handler
from app.infra.api.lifespan import lifespan
from app.infra.api.routers import root, v1


def create_instance(settings: Settings) -> FastAPI:
    return FastAPI(
        debug=settings.APP_DEBUG,
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )


def register_routers(app: FastAPI) -> FastAPI:
    app.include_router(root.router)
    app.include_router(v1.router, prefix="/api/v1")
    return app


def register_extensions(app: FastAPI) -> FastAPI:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    return app


def create_app(settings: Settings) -> FastAPI:
    app = create_instance(settings)
    return register_routers(register_extensions(app))
