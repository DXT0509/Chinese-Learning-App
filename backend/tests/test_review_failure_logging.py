"""SRS diagnostics expose categories and route templates, never error payloads or IDs."""

import logging
from uuid import uuid4

import httpx
from sqlalchemy.exc import DBAPIError

from app.core.config import get_settings
from app.dependencies.authentication import current_user_id
from app.main import create_app, logger
from app.services.review_engine import ReviewEngine


async def test_database_failure_logs_safe_category_and_template_only(monkeypatch, caplog):
    async def fail(*args, **kwargs):
        raise DBAPIError(
            "SELECT sensitive-sql",
            {"token": "sensitive-token"},
            RuntimeError("sensitive-driver-message"),
            connection_invalidated=True,
        )

    monkeypatch.setattr(ReviewEngine, "question", fail)
    settings = get_settings().model_copy(update={"environment": "development"})
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    caplog.set_level(logging.INFO, logger="chinese_learning")
    app = create_app()
    app.dependency_overrides[current_user_id] = lambda: uuid4()
    attempt = str(uuid4())
    logger.addHandler(caplog.handler)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app, raise_app_exceptions=False), base_url="http://test"
        ) as client:
            result = await client.get(
                f"/api/v1/me/srs/sessions/{attempt}/question",
                headers={"Authorization": "Bearer sensitive-token"},
            )
        assert result.status_code == 500
        assert result.json() == {"detail": "Internal server error"}
        messages = "\n".join(record.getMessage() for record in caplog.records)
        assert "server_failure_database_connection" in messages
        assert "{attempt_id}" in messages
        assert "sensitive" not in messages and attempt not in messages
    finally:
        logger.removeHandler(caplog.handler)
