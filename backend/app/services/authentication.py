from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.security import digest, dummy_hash, password_hasher, token, verify_password
from app.models import AuthSession, PasswordCredential, RefreshCredential, User
from app.schemas.session import Credentials, Tokens


def unauthorized():
    return HTTPException(401, "Invalid or expired session", headers={"WWW-Authenticate": "Bearer"})


async def issue(session: AsyncSession, record: AuthSession) -> Tokens:
    access, refresh = token(), token()
    record.access_hash = digest(access)
    record.access_expires_at = datetime.now(UTC) + timedelta(minutes=10)
    session.add(record)
    await session.flush()
    session.add(RefreshCredential(token_hash=digest(refresh), session_id=record.id))
    return Tokens(access_token=access, refresh_token=refresh)


async def authenticate(session: AsyncSession, data: Credentials, register: bool) -> Tokens:
    async with session.begin():
        if register:
            encoded = await run_in_threadpool(
                password_hasher.hash, data.password.get_secret_value()
            )
            user = User(display_name=data.email.split("@")[0], email=str(data.email))
            session.add(user)
            await session.flush()
            session.add(
                PasswordCredential(user_id=user.id, email=str(data.email), password_hash=encoded)
            )
            try:
                await session.flush()
            except IntegrityError:
                raise HTTPException(409, "Registration unavailable for these details") from None
        else:
            credential = await session.scalar(
                select(PasswordCredential).where(PasswordCredential.email == str(data.email))
            )
            valid = await run_in_threadpool(
                verify_password,
                credential.password_hash if credential else dummy_hash,
                data.password.get_secret_value(),
            )
            if not credential or not valid:
                raise HTTPException(401, "Invalid email or password")
            user = await session.get(User, credential.user_id)
            if password_hasher.check_needs_rehash(credential.password_hash):
                credential.password_hash = await run_in_threadpool(
                    password_hasher.hash, data.password.get_secret_value()
                )
        return await issue(
            session, AuthSession(user_id=user.id, expires_at=datetime.now(UTC) + timedelta(days=30))
        )


async def rotate(session: AsyncSession, raw: str, logout: bool = False):
    invalid = False
    result = None
    async with session.begin():
        record = await session.scalar(
            select(AuthSession)
            .join(RefreshCredential, RefreshCredential.session_id == AuthSession.id)
            .where(RefreshCredential.token_hash == digest(raw))
            .with_for_update(of=AuthSession)
        )
        if not record:
            invalid = True
        else:
            credential = await session.get(RefreshCredential, digest(raw), populate_existing=True)
            now = datetime.now(UTC)
            if (
                logout
                or credential.used_at is not None
                or record.revoked_at
                or record.expires_at <= now
            ):
                record.revoked_at = now
                invalid = not logout
            else:
                credential.used_at = now
                result = await issue(session, record)
    # Replay revocation must commit before returning 401.
    if invalid:
        raise unauthorized()
    return result
