import asyncio
from typing import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
import httpx
from httpx import AsyncClient

from app.config import Settings, get_settings
from app.infra.api.app import create_app


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    return f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"


@pytest.fixture(scope="session")
async def client(app: FastAPI, base_url: str) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url=base_url
        ) as async_client:
            yield async_client
