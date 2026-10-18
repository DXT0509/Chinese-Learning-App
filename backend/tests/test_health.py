from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.parametrize("path", ["/health", "/api/v1/health"])
async def test_health_contract(path):
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        response = await client.get(path)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Chinese Learning API"
    assert body["version"] == "0.1.0"
    assert datetime.fromisoformat(body["timestamp"]).utcoffset().total_seconds() == 0


async def test_unexpected_error_is_redacted(caplog):
    app = create_app()

    @app.get("/broken")
    async def broken():
        raise RuntimeError("sensitive-token-value")

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test"
    ) as client:
        response = await client.get("/broken")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "sensitive-token-value" not in response.text


async def test_unknown_routes_and_cors_are_closed():
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        assert (await client.get("/api/v1/users/me/progress")).status_code == 404
        response = await client.options(
            "/api/v1/health",
            headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"},
        )
    assert "access-control-allow-origin" not in response.headers
