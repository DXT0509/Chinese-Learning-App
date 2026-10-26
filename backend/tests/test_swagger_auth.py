"""Swagger login contract checks without connecting to a database or creating sessions."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import authentication
from app.dependencies.database import get_session
from app.main import create_app
from app.schemas.session import Tokens
from app.services.authentication import unauthorized


@pytest.fixture
def swagger_client(monkeypatch):
    authentication.attempts.clear()
    authenticate = AsyncMock(
        return_value=Tokens(access_token="test-access-token", refresh_token="test-refresh-token")
    )
    monkeypatch.setattr(authentication, "authenticate", authenticate)
    app = create_app()
    app.dependency_overrides[get_session] = lambda: object()
    with TestClient(app) as client:
        yield client, authenticate
    authentication.attempts.clear()


def test_authorize_advertises_password_form_and_preserves_json_login(swagger_client):
    client, authenticate = swagger_client
    schema = client.get("/openapi.json").json()
    flow = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]
    assert flow["tokenUrl"] == "api/v1/auth/token"
    assert schema["paths"]["/api/v1/auth/me"]["get"]["security"] == [{"OAuth2PasswordBearer": []}]
    assert (
        "application/x-www-form-urlencoded"
        in schema["paths"]["/api/v1/auth/token"]["post"]["requestBody"]["content"]
    )
    password = "  actual password  "
    response = client.post(
        "/api/v1/auth/token",
        data={"username": " TEST@example.com ", "password": password, "grant_type": "password"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] == "test-access-token"
    assert response.headers["Cache-Control"] == "no-store"
    args, kwargs = authenticate.call_args
    assert args[1].email == "test@example.com"
    assert args[1].password.get_secret_value() == password
    assert kwargs == {"register": False}
    response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": password}
    )
    assert response.status_code == 200
    assert authenticate.await_count == 2


@pytest.mark.parametrize(
    "data",
    [
        {"username": "invalid-email", "password": "secret-password", "grant_type": "password"},
        {"username": "test@example.com", "password": "short", "grant_type": "password"},
        {"username": "test@example.com", "password": "secret-password"},
        {"username": "test@example.com", "password": "secret-password", "grant_type": "other"},
    ],
)
def test_invalid_form_is_rejected_without_echoing_credentials(swagger_client, data):
    client, authenticate = swagger_client
    response = client.post("/api/v1/auth/token", data=data)
    assert response.status_code == 422
    assert data["username"] not in response.text
    assert data["password"] not in response.text
    authenticate.assert_not_awaited()


def test_form_login_keeps_authentication_errors_and_shared_rate_limit(swagger_client):
    client, authenticate = swagger_client
    authenticate.side_effect = unauthorized()
    data = {"username": "test@example.com", "password": "secret-password", "grant_type": "password"}
    response = client.post("/api/v1/auth/token", data=data)
    assert response.status_code == 401
    assert data["password"] not in response.text
    for _ in range(19):
        assert client.post("/api/v1/auth/login", json={}).status_code == 422
    limited = client.post("/api/v1/auth/token", data=data)
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "60"
    authenticate.assert_awaited_once()


def test_missing_and_wrong_authorization_scheme_still_fail_closed(swagger_client):
    client, _ = swagger_client
    for headers in ({}, {"Authorization": "Basic not-a-bearer-token"}):
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"
