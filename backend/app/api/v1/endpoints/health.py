from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Application liveness")
async def health() -> HealthResponse:
    """Checks API liveness only; does not assert database readiness or authentication."""
    return HealthResponse(
        status="ok",
        service=get_settings().app_name,
        version="0.1.0",
        timestamp=datetime.now(UTC),
    )
