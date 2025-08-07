from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.config import get_settings
from app.infra.db import engine
from app.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting application in {settings.ENV} environment")

    app.state.db_engine = engine
    logger.info("Database connection initialized")

    try:
        yield
    finally:
        # Clean up resources on shutdown
        if hasattr(app.state, "db_engine") and app.state.db_engine:
            await app.state.db_engine.dispose()
            logger.info("Database connection closed")
