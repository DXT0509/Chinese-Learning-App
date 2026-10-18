"""Real PostgreSQL constraints; requires an isolated database migrated to head."""

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import Character, SrsState, User, UserVocabulary, Vocabulary, VocabularyCharacter


@pytest.mark.postgres
async def test_schema_constraints_in_postgres():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                user_id, vocabulary_id, character_id, entry_id = (uuid4() for _ in range(4))
                await connection.execute(insert(User).values(id=user_id, display_name="Test"))
                await connection.execute(
                    insert(Vocabulary).values(
                        id=vocabulary_id,
                        simplified=str(uuid4()),
                        pinyin="ma ma",
                        vietnamese_meaning="mẹ",
                    )
                )
                await connection.execute(
                    insert(Character).values(
                        id=character_id, hanzi="媽" + uuid4().hex[:5], stroke_count=13
                    )
                )
                # Repeating a character at distinct positions must be accepted.
                await connection.execute(
                    insert(VocabularyCharacter),
                    [
                        {
                            "vocabulary_id": vocabulary_id,
                            "character_id": character_id,
                            "position": 0,
                        },
                        {
                            "vocabulary_id": vocabulary_id,
                            "character_id": character_id,
                            "position": 1,
                        },
                    ],
                )
                await connection.execute(
                    insert(UserVocabulary).values(
                        id=entry_id, user_id=user_id, vocabulary_id=vocabulary_id, source="catalog"
                    )
                )
                async with connection.begin_nested() as savepoint:
                    with pytest.raises(IntegrityError):
                        await connection.execute(
                            insert(UserVocabulary).values(
                                id=uuid4(),
                                user_id=user_id,
                                vocabulary_id=vocabulary_id,
                                source="catalog",
                            )
                        )
                    await savepoint.rollback()
                async with connection.begin_nested() as savepoint:
                    with pytest.raises(IntegrityError):
                        await connection.execute(
                            insert(UserVocabulary).values(
                                id=uuid4(), user_id=user_id, source="custom"
                            )
                        )
                    await savepoint.rollback()
                # Multiple independent custom entries are allowed despite the nullable unique key.
                for _ in range(2):
                    await connection.execute(
                        insert(UserVocabulary).values(
                            id=uuid4(),
                            user_id=user_id,
                            source="custom",
                            custom_simplified="你好",
                            custom_meaning="xin chào",
                        )
                    )
                await connection.execute(
                    insert(SrsState).values(
                        id=uuid4(),
                        user_vocabulary_id=entry_id,
                        due_at=datetime.now(UTC),
                        algorithm_version="unimplemented-v0",
                    )
                )
                async with connection.begin_nested() as savepoint:
                    with pytest.raises(IntegrityError):
                        await connection.execute(
                            insert(SrsState).values(
                                id=uuid4(),
                                user_vocabulary_id=entry_id,
                                due_at=datetime.now(UTC),
                                algorithm_version="unimplemented-v0",
                            )
                        )
                    await savepoint.rollback()
                created_at = await connection.scalar(
                    select(User.created_at).where(User.id == user_id)
                )
                assert created_at.tzinfo is not None
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()
