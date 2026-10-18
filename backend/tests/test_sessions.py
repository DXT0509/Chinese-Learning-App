"""Authentication and ownership tests against real migrated PostgreSQL."""

import os
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.endpoints.authentication import attempts
from app.core.config import get_settings
from app.core.security import digest, password_hasher, verify_password
from app.dependencies.database import get_session
from app.main import create_app
from app.models import AuthSession, LessonVersion, PasswordCredential, RefreshCredential
from app.schemas.content import version_id
from app.schemas.session import Credentials
from app.services.content_authoring import import_library
from app.services.content_files import load_library
from app.services.content_storage import LocalContentStorage
from app.services.lesson_publication import publish_lesson

PASSWORD = "local-test-password-123"


@pytest.mark.parametrize("length,accepted", [(5, False), (6, True), (128, True), (129, False)])
def test_password_boundaries(length, accepted):
    if accepted:
        assert (
            Credentials(
                email="boundary@example.com", password="a" * length
            ).password.get_secret_value()
            == "a" * length
        )
    else:
        with pytest.raises(ValidationError):
            Credentials(email="boundary@example.com", password="a" * length)


@pytest.mark.parametrize("length,expected", [(5, 422), (6, 201), (128, 201), (129, 422)])
async def test_registration_password_boundaries_against_database(api, length, expected):
    client, _, _ = api
    password = "a" * length
    response = await client.post(
        "/api/v1/auth/register", json={"email": "boundary@example.com", "password": password}
    )
    assert response.status_code == expected
    if expected == 201:
        login = await client.post(
            "/api/v1/auth/login", json={"email": "boundary@example.com", "password": password}
        )
        assert login.status_code == 200
        assert (await client.get("/api/v1/auth/me", headers=auth(login.json()))).status_code == 200


def test_argon2id_and_no_plaintext():
    encoded = password_hasher.hash(PASSWORD)
    assert encoded.startswith("$argon2id$")
    assert PASSWORD not in encoded
    assert verify_password(encoded, PASSWORD)
    assert not verify_password(encoded, "wrong")


def test_validation_does_not_echo_credentials_and_unauthorized_routes():
    attempts.clear()
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/auth/register", json={"email": "invalid", "password": PASSWORD}
        )
        assert response.status_code == 422
        assert PASSWORD not in response.text
        for path in ("/auth/me", "/lessons", "/learning-runs", f"/learning-runs/{uuid4()}"):
            assert client.get("/api/v1" + path).status_code == 401


def test_auth_rate_limit():
    attempts.clear()
    with TestClient(create_app()) as client:
        for _ in range(20):
            assert client.post("/api/v1/auth/login", json={}).status_code == 422
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 429
        assert response.headers["Retry-After"] == "60"
    attempts.clear()


@pytest.fixture
async def api(tmp_path, monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    engine = create_async_engine(url)
    monkeypatch.setenv("ALLOW_CONTENT_PREVIEW", "true")
    monkeypatch.setenv("CONTENT_STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()
    attempts.clear()
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            factory = async_sessionmaker(
                bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )

            async def database():
                async with factory() as session:
                    yield session

            app = create_app()
            app.dependency_overrides[get_session] = database
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                yield client, factory, tmp_path
            await transaction.rollback()
    finally:
        get_settings.cache_clear()
        attempts.clear()
        await engine.dispose()


async def register(client, email="test@example.com"):
    response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth(tokens):
    return {"Authorization": "Bearer " + tokens["access_token"]}


async def test_register_normalize_duplicate_login_and_hash_storage(api):
    client, factory, _ = api
    tokens = await register(client, " Test@EXAMPLE.COM ")
    response = await client.get("/api/v1/auth/me", headers=auth(tokens))
    assert response.json()["email"] == "test@example.com"
    assert response.json()["email_verified"] is False
    assert "password_hash" not in response.text
    duplicate = await client.post(
        "/api/v1/auth/register", json={"email": "TEST@example.com", "password": PASSWORD}
    )
    assert duplicate.status_code == 409
    login = await client.post(
        "/api/v1/auth/login", json={"email": "TEST@example.com", "password": PASSWORD}
    )
    assert login.status_code == 200
    assert (await client.get("/api/v1/auth/me", headers=auth(login.json()))).json()[
        "id"
    ] == response.json()["id"]
    async with factory() as session:
        credential = await session.scalar(select(PasswordCredential))
        assert credential.password_hash.startswith("$argon2id$")
        assert await session.get(RefreshCredential, digest(tokens["refresh_token"]))
        assert not await session.get(RefreshCredential, tokens["refresh_token"])


@pytest.mark.parametrize("email", ["test@example.com", "missing@example.com"])
async def test_invalid_credentials_same_error(api, email):
    client, _, _ = api
    await register(client)
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "incorrect-password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


async def test_access_expiry_rotation_and_logout(api):
    client, factory, _ = api
    tokens = await register(client)
    async with factory() as session, session.begin():
        await session.execute(
            update(AuthSession).values(access_expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
    assert (await client.get("/api/v1/auth/me", headers=auth(tokens))).status_code == 401
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    renewed = response.json()
    assert renewed["refresh_token"] != tokens["refresh_token"]
    assert (await client.get("/api/v1/auth/me", headers=auth(renewed))).status_code == 200
    assert (
        await client.post("/api/v1/auth/logout", json={"refresh_token": renewed["refresh_token"]})
    ).status_code == 204
    assert (await client.get("/api/v1/auth/me", headers=auth(renewed))).status_code == 401
    assert (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": renewed["refresh_token"]})
    ).status_code == 401


async def test_refresh_replay_revokes_entire_family(api):
    client, _, _ = api
    tokens = await register(client)
    newer = (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    ).json()
    assert (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    ).status_code == 401
    assert (await client.get("/api/v1/auth/me", headers=auth(newer))).status_code == 401
    assert (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": newer["refresh_token"]})
    ).status_code == 401


async def test_expired_and_unknown_refresh(api):
    client, factory, _ = api
    tokens = await register(client)
    async with factory() as session, session.begin():
        await session.execute(
            update(AuthSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
    for raw in (tokens["refresh_token"], "x" * 43):
        assert (
            await client.post("/api/v1/auth/refresh", json={"refresh_token": raw})
        ).status_code == 401


async def test_pinned_idempotent_runs_checkpoints_and_ownership(api):
    client, factory, root = api
    storage = LocalContentStorage(root)
    async with factory() as session:
        await import_library(
            session, load_library(Path(__file__).resolve().parents[1] / "content"), storage
        )
    lesson_id = None
    pinned = version_id("lesson", "lesson-ni", 1)
    async with factory() as session:
        lesson_id = (await session.get(LessonVersion, pinned)).lesson_id
    async with factory() as session:
        await publish_lesson(session, lesson_id, 1, storage)
    owner, other = await register(client), await register(client, "other@example.com")
    headers = auth(owner)
    assert (await client.get("/api/v1/lessons", headers=headers)).json()[0][
        "lesson_version_id"
    ] == str(pinned)
    bundle_path = f"/api/v1/lesson-versions/{pinned}/bundle"
    assert (await client.get(bundle_path, headers=headers)).status_code == 403
    bundle = (await client.get(bundle_path + "?allow_preview=true", headers=headers)).json()
    data = {"lesson_version_id": str(pinned), "request_id": str(uuid4()), "allow_preview": True}
    first = await client.post("/api/v1/learning-runs", headers=headers, json=data)
    assert first.status_code == 201, first.text
    run = first.json()
    assert (await client.post("/api/v1/learning-runs", headers=headers, json=data)).json() == run
    run_path = "/api/v1/learning-runs/" + run["id"]
    scene_path = run_path + "/scenes/" + bundle["scenes"][0]["scene_key"]
    assert (await client.get(run_path, headers=auth(other))).status_code == 404
    assert (await client.put(scene_path, headers=auth(other), json={"page": 1})).status_code == 404
    for _ in range(2):
        saved = await client.put(scene_path, headers=headers, json={"page": 3})
        assert saved.status_code == 200
        assert saved.json()["checkpoints"][0]["page"] == 3
    assert (
        await client.put(run_path + f"/scenes/{uuid4()}", headers=headers, json={"page": 1})
    ).status_code == 404
    assert (
        await client.put(scene_path, headers=headers, json={"page": 1, "completed": True})
    ).status_code == 422
    restored = (await client.get(run_path, headers=headers)).json()
    assert restored["lesson_version_id"] == str(pinned)
    assert restored["learning_completion_supported"] is False
    assert len((await client.get("/api/v1/learning-runs", headers=auth(other))).json()) == 0
    # A newer publication must not move an existing run or its bundle/checkpoints.
    library = load_library(Path(__file__).resolve().parents[1] / "content")
    second = replace(library, lessons=[library.lessons[0].model_copy(update={"version": 2})])
    async with factory() as session:
        await import_library(session, second, storage)
    async with factory() as session:
        await publish_lesson(session, lesson_id, 2, storage)
    assert (await client.get(run_path, headers=headers)).json() == restored
    assert (await client.get(bundle_path + "?allow_preview=true", headers=headers)).json() == bundle
    conflict = await client.post(
        "/api/v1/learning-runs",
        headers=headers,
        json={**data, "lesson_version_id": str(version_id("lesson", "lesson-ni", 2))},
    )
    assert conflict.status_code == 409


async def test_preview_requires_server_gate_and_drafts_are_unavailable(api, monkeypatch):
    client, factory, root = api
    storage = LocalContentStorage(root)
    library = load_library(Path(__file__).resolve().parents[1] / "content")
    async with factory() as session:
        await import_library(session, library, storage)
    pinned = version_id("lesson", "lesson-ni", 1)
    tokens = await register(client)
    path = f"/api/v1/lesson-versions/{pinned}/bundle?allow_preview=true"
    assert (await client.get(path, headers=auth(tokens))).status_code == 404
    async with factory() as session:
        lesson_id = (await session.get(LessonVersion, pinned)).lesson_id
    async with factory() as session:
        await publish_lesson(session, lesson_id, 1, storage)
    monkeypatch.setenv("ALLOW_CONTENT_PREVIEW", "false")
    get_settings.cache_clear()
    assert (await client.get(path, headers=auth(tokens))).status_code == 403
