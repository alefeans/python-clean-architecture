from dataclasses import dataclass

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@dataclass
class HealthCheck:
    title: str
    description: str
    version: str
    status: str


@router.get(
    "/health-check",
    status_code=200,
    tags=["Health Check"],
    summary="Performs API health check",
)
def health_check() -> HealthCheck:
    settings = get_settings()
    return HealthCheck(
        settings.APP_TITLE, settings.APP_DESCRIPTION, settings.APP_VERSION, "I'm ok!"
    )
