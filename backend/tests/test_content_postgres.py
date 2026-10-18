"""Real PostgreSQL behavior, rolled back outside service-owned savepoints."""

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import (
    Asset,
    Character,
    Lesson,
    LessonTemplate,
    LessonTemplateScene,
    LessonTemplateVersion,
    LessonVersion,
    LessonVocabulary,
    Vocabulary,
    VocabularyCharacter,
)
from app.schemas.content import TemplateDefinition, VocabularyDefinition, content_id, version_id
from app.services.content_authoring import import_library
from app.services.content_files import ContentError, load_library
from app.services.content_storage import LocalContentStorage
from app.services.lesson_publication import compile_draft, inspect_bundle, publish_lesson

pytestmark = pytest.mark.postgres
CONTENT = Path(__file__).resolve().parents[1] / "content"


@pytest.fixture
async def pg_sessions():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a dedicated migrated PostgreSQL database")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            yield async_sessionmaker(
                bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            await transaction.rollback()
    finally:
        await engine.dispose()


async def imported(pg_sessions, tmp_path, library=None):
    library = library or load_library(CONTENT)
    storage = LocalContentStorage(tmp_path)
    async with pg_sessions() as session:
        await import_library(session, library, storage)
    return library, storage


async def test_import_is_idempotent_and_draft_validates(pg_sessions, tmp_path):
    library, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session:
        await import_library(session, library, storage)
    async with pg_sessions() as session:
        for model in (
            Vocabulary,
            Character,
            Lesson,
            LessonVersion,
            LessonTemplateVersion,
            LessonVocabulary,
            VocabularyCharacter,
        ):
            assert await session.scalar(select(func.count()).select_from(model)) == 1
        version = await session.get(LessonVersion, version_id("lesson", "lesson-ni", 1))
        assert version.status == "DRAFT" and version.bundle_asset_id is None
        bundle, template = await compile_draft(session, version, storage)
        assert template.status == "DRAFT"
        assert bundle["purpose"] == "CONTENT_PREVIEW"
        assert bundle["learning_completion_supported"] is False
        assert bundle["scenes"][0]["config"]["vocabulary_ref"] == {
            "kind": "VOCABULARY",
            "id": str(content_id("vocabulary", "v-ni")),
        }


async def test_publish_freezes_bundle_and_definitions_then_new_draft(pg_sessions, tmp_path):
    library, storage = await imported(pg_sessions, tmp_path)
    lesson_id = content_id("lesson", "lesson-ni")
    async with pg_sessions() as session:
        key = await publish_lesson(session, lesson_id, 1, storage)
    first_bytes = storage.read(key)
    async with pg_sessions() as session:
        asset = await session.scalar(select(Asset).where(Asset.storage_key == key))
        assert asset.sha256 == hashlib.sha256(first_bytes).hexdigest()
        assert await inspect_bundle(session, lesson_id, 1, storage) == first_bytes
        version = await session.get(LessonVersion, version_id("lesson", "lesson-ni", 1))
        assert version.published_at.tzinfo is not None
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="already published"):
            await publish_lesson(session, lesson_id, 1, storage)
    # Identical replay does not issue updates to protected definitions.
    async with pg_sessions() as session:
        await import_library(session, library, storage)
    changed = replace(library, lessons=[library.lessons[0].model_copy(update={"title": "changed"})])
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="immutable"):
            await import_library(session, changed, storage)
    second = replace(
        library,
        lessons=[
            library.lessons[0].model_copy(update={"version": 2, "title": "Bản xem trước mới"})
        ],
    )
    async with pg_sessions() as session:
        await import_library(session, second, storage)
    async with pg_sessions() as session:
        assert await inspect_bundle(session, lesson_id, 1, storage) == first_bytes
        second_draft = await session.get(LessonVersion, version_id("lesson", "lesson-ni", 2))
        assert second_draft.status == "DRAFT"
    async with pg_sessions() as session:
        second_key = await publish_lesson(session, lesson_id, 2, storage)
    assert second_key != key and storage.read(key) == first_bytes


async def test_database_immutability_guards(pg_sessions, tmp_path):
    _, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session:
        await publish_lesson(session, content_id("lesson", "lesson-ni"), 1, storage)
    statements = [
        update(LessonVersion).values(title="tampered"),
        update(LessonTemplateVersion).values(status="DRAFT", published_at=None),
        update(LessonTemplateScene).values(required=False),
        update(LessonVocabulary).values(role="CONTEXT"),
        update(Asset).values(media_type="text/plain"),
        text("DELETE FROM lesson_template_scenes"),
        text("DELETE FROM lesson_vocabulary"),
        update(Lesson).values(lesson_type="TOPIC"),
        update(Lesson).values(code="repurposed"),
        update(LessonTemplate).values(code="repurposed"),
    ]
    for statement in statements:
        async with pg_sessions() as session:
            with pytest.raises(IntegrityError):
                async with session.begin():
                    await session.execute(statement)


async def test_postgres_uniqueness_fks_and_scene_constraints(pg_sessions, tmp_path):
    await imported(pg_sessions, tmp_path)
    template_id = version_id("template", "vocabulary-preview", 1)
    scene_values = {
        "template_version_id": template_id,
        "scene_key": uuid4(),
        "position": 20,
        "scene_type": "VOCABULARY_INFORMATION",
        "contract_version": 1,
        "required": True,
        "config": {},
    }
    statements = [
        insert(LessonTemplateScene).values(**scene_values),  # duplicate position
        insert(LessonTemplateScene).values(
            **{**scene_values, "position": 40, "scene_type": "UNKNOWN"}
        ),
        insert(LessonTemplateScene).values(
            **{**scene_values, "position": 40, "contract_version": 2}
        ),
        insert(LessonTemplateScene).values(**{**scene_values, "position": 40, "config": []}),
        insert(Lesson).values(id=uuid4(), title="Invalid", lesson_type="UNKNOWN", lesson_order=5),
        insert(LessonVocabulary).values(
            lesson_id=content_id("lesson", "lesson-ni"),
            lesson_version_id=version_id("lesson", "lesson-ni", 1),
            vocabulary_id=uuid4(),
            position=1,
            role="TEACHES",
        ),
        insert(VocabularyCharacter).values(
            vocabulary_id=content_id("vocabulary", "v-ni"),
            character_id=content_id("character", "character-ni"),
            position=0,
        ),
        insert(VocabularyCharacter).values(
            vocabulary_id=content_id("vocabulary", "v-ni"),
            character_id=content_id("character", "character-ni"),
            position=-1,
        ),
    ]
    for statement in statements:
        async with pg_sessions() as session:
            with pytest.raises(IntegrityError):
                async with session.begin():
                    await session.execute(statement)


async def test_membership_cannot_point_to_another_lessons_version(pg_sessions, tmp_path):
    await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session, session.begin():
        other_id = uuid4()
        session.add(Lesson(id=other_id, title="Other", lesson_type="VOCABULARY", lesson_order=3))
        other_word = uuid4()
        session.add(
            Vocabulary(id=other_word, simplified="我", pinyin="wǒ", vietnamese_meaning="tôi")
        )
    async with pg_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(
                    insert(LessonVocabulary).values(
                        lesson_id=other_id,
                        lesson_version_id=version_id("lesson", "lesson-ni", 1),
                        vocabulary_id=other_word,
                        position=1,
                        role="TEACHES",
                    )
                )


async def test_repeated_occurrences_survive_import(pg_sessions, tmp_path):
    library = load_library(CONTENT)
    word = library.vocabulary[0].model_dump()
    word["simplified"] = "你你"
    word["occurrences"].append({"position": 1, "character": "character-ni"})
    library = replace(library, vocabulary=[VocabularyDefinition.model_validate(word)])
    await imported(pg_sessions, tmp_path, library)
    async with pg_sessions() as session:
        rows = (
            await session.scalars(
                select(VocabularyCharacter).order_by(VocabularyCharacter.position)
            )
        ).all()
        assert [item.position for item in rows] == [0, 1]
        assert rows[0].character_id == rows[1].character_id


async def test_invalid_database_draft_blocks_publication(pg_sessions, tmp_path):
    _, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session, session.begin():
        await session.execute(update(LessonTemplateScene).values(config={"script": "bad"}))
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="invalid scene contracts"):
            await publish_lesson(session, content_id("lesson", "lesson-ni"), 1, storage)
    assert not list(tmp_path.rglob("*.json"))
    async with pg_sessions() as session:
        version = await session.get(LessonVersion, version_id("lesson", "lesson-ni", 1))
        assert version.status == "DRAFT"


async def test_missing_asset_rolls_back_import(pg_sessions, tmp_path):
    library = load_library(CONTENT)
    # A schema-valid graph with a declared object still needs real object bytes.
    from app.schemas.content import AssetDefinition

    asset = AssetDefinition.model_validate(
        {
            "schema_version": 1,
            "id": "audio-ni",
            "storage_key": f"sha256/{'a' * 64}.mp3",
            "sha256": "a" * 64,
            "byte_length": 100,
            "media_type": "audio/mpeg",
            "metadata": {},
        }
    )
    library = replace(library, assets=[asset])
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="missing"):
            await import_library(session, library, LocalContentStorage(tmp_path))
    async with pg_sessions() as session:
        assert await session.scalar(select(func.count()).select_from(Vocabulary)) == 0


async def test_published_template_edit_rejected(pg_sessions, tmp_path):
    library, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session:
        await publish_lesson(session, content_id("lesson", "lesson-ni"), 1, storage)
    changed = library.templates[0].model_dump()
    changed["scenes"][0]["config"]["fields"] = ["MEANING"]
    library = replace(library, templates=[TemplateDefinition.model_validate(changed)])
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="immutable"):
            await import_library(session, library, storage)


async def test_catalog_prose_changes_only_new_bundle(pg_sessions, tmp_path):
    library, storage = await imported(pg_sessions, tmp_path)
    lesson_id = content_id("lesson", "lesson-ni")
    async with pg_sessions() as session:
        first_key = await publish_lesson(session, lesson_id, 1, storage)
    data = storage.read(first_key)
    changed = replace(
        library,
        vocabulary=[
            library.vocabulary[0].model_copy(update={"notes": "Thông tin bổ sung đã duyệt."})
        ],
        lessons=[library.lessons[0].model_copy(update={"version": 2})],
    )
    async with pg_sessions() as session:
        await import_library(session, changed, storage)
    async with pg_sessions() as session:
        second_key = await publish_lesson(session, lesson_id, 2, storage)
    assert storage.read(first_key) == data
    assert json.loads(storage.read(second_key))["vocabulary"]["revision"] == 2


@pytest.mark.parametrize("target_count", [0, 2])
async def test_publication_rejects_zero_and_multiple_targets(pg_sessions, tmp_path, target_count):
    _, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session, session.begin():
        if target_count == 0:
            # Simulate an incomplete draft created outside the authoring importer.
            await session.execute(text("DELETE FROM lesson_vocabulary"))
        else:
            extra_word = uuid4()
            session.add(
                Vocabulary(id=extra_word, simplified="我", pinyin="wǒ", vietnamese_meaning="tôi")
            )
            await session.flush()
            session.add(
                LessonVocabulary(
                    lesson_id=content_id("lesson", "lesson-ni"),
                    lesson_version_id=version_id("lesson", "lesson-ni", 1),
                    vocabulary_id=extra_word,
                    position=1,
                    role="TEACHES",
                )
            )
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="exactly one"):
            await publish_lesson(session, content_id("lesson", "lesson-ni"), 1, storage)
    assert not list(tmp_path.rglob("*.json"))


async def test_missing_referenced_object_blocks_publication(pg_sessions, tmp_path):
    _, storage = await imported(pg_sessions, tmp_path)
    async with pg_sessions() as session, session.begin():
        asset_id = uuid4()
        session.add(
            Asset(
                id=asset_id,
                storage_key=f"sha256/{'a' * 64}.mp3",
                sha256="a" * 64,
                byte_length=10,
                media_type="audio/mpeg",
                asset_metadata={},
            )
        )
        await session.flush()
        await session.execute(update(Vocabulary).values(audio_asset_id=asset_id))
    async with pg_sessions() as session:
        with pytest.raises(ContentError, match="missing"):
            await publish_lesson(session, content_id("lesson", "lesson-ni"), 1, storage)
    async with pg_sessions() as session:
        version = await session.get(LessonVersion, version_id("lesson", "lesson-ni", 1))
        assert version.status == "DRAFT" and version.bundle_asset_id is None


async def test_legacy_membership_is_kept_when_adopting_existing_ids(pg_sessions, tmp_path):
    library = load_library(CONTENT)
    word_id, char_id, lesson_id = uuid4(), uuid4(), uuid4()
    async with pg_sessions() as session, session.begin():
        session.add(Character(id=char_id, hanzi="你", stroke_count=None))
        session.add(Vocabulary(id=word_id, simplified="你", pinyin="nǐ", vietnamese_meaning="bạn"))
        session.add(
            Lesson(id=lesson_id, title="Legacy title", lesson_type="VOCABULARY", lesson_order=2)
        )
        await session.flush()
        session.add(LessonVocabulary(lesson_id=lesson_id, vocabulary_id=word_id, position=0))
    word = library.vocabulary[0].model_dump()
    word["id"], word["characters"][0]["id"] = str(word_id), str(char_id)
    word["occurrences"][0]["character"] = str(char_id)
    lesson = library.lessons[0].model_dump()
    lesson["id"], lesson["vocabulary"][0]["vocabulary"] = str(lesson_id), str(word_id)
    from app.schemas.content import LessonDefinition

    library = replace(
        library,
        vocabulary=[VocabularyDefinition.model_validate(word)],
        lessons=[LessonDefinition.model_validate(lesson)],
    )
    await imported(pg_sessions, tmp_path, library)
    async with pg_sessions() as session:
        memberships = (await session.scalars(select(LessonVocabulary))).all()
        assert len(memberships) == 2
        legacy = next(item for item in memberships if item.lesson_version_id is None)
        assert legacy.role is None and legacy.vocabulary_id == word_id
        assert (await session.get(Lesson, lesson_id)).title == "Legacy title"
