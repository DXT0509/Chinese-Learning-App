"""Compile an inspectable preview; never award learning or assert runtime capabilities."""

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid5

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Asset,
    Character,
    Lesson,
    LessonTemplateScene,
    LessonTemplateVersion,
    LessonVersion,
    LessonVocabulary,
    Vocabulary,
    VocabularyCharacter,
)
from app.schemas.content import CONTENT_NAMESPACE, TemplateDefinition, VocabularyDefinition
from app.services.content_authoring import lock_authoring
from app.services.content_files import ContentError
from app.services.content_storage import ContentStorage, verify_object


def canonical_bundle(bundle: dict) -> bytes:
    return json.dumps(
        bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


async def _asset_projection(
    session: AsyncSession, storage: ContentStorage, asset_id: UUID, prefix: str
) -> dict:
    asset = await session.get(Asset, asset_id)
    if not asset or not asset.media_type.startswith(prefix):
        raise ContentError("missing or incompatible required asset")
    verify_object(storage, asset.storage_key, asset.sha256, asset.byte_length)
    return {
        "id": str(asset.id),
        "storage_key": asset.storage_key,
        "sha256": asset.sha256,
        "byte_length": asset.byte_length,
        "media_type": asset.media_type,
        "metadata": asset.asset_metadata,
    }


async def compile_draft(
    session: AsyncSession, version: LessonVersion, storage: ContentStorage
) -> tuple[dict, LessonTemplateVersion]:
    lesson = await session.get(Lesson, version.lesson_id)
    if not lesson or lesson.lesson_type != "VOCABULARY":
        raise ContentError("only VOCABULARY preview publication is supported")
    template = await session.get(
        LessonTemplateVersion, version.template_version_id, with_for_update=True
    )
    if not template:
        raise ContentError("missing exact template version")
    scenes = (
        await session.scalars(
            select(LessonTemplateScene)
            .where(LessonTemplateScene.template_version_id == template.id)
            .order_by(LessonTemplateScene.position)
        )
    ).all()
    memberships = (
        await session.scalars(
            select(LessonVocabulary).where(LessonVocabulary.lesson_version_id == version.id)
        )
    ).all()
    if len(memberships) != 1 or memberships[0].role != "TEACHES":
        raise ContentError("VOCABULARY requires exactly one membership with role TEACHES")
    word = await session.get(Vocabulary, memberships[0].vocabulary_id)
    if not word:
        raise ContentError("missing TEACHES vocabulary")
    occurrences = (
        await session.execute(
            select(VocabularyCharacter, Character)
            .join(Character, Character.id == VocabularyCharacter.character_id)
            .where(VocabularyCharacter.vocabulary_id == word.id)
            .order_by(VocabularyCharacter.position)
        )
    ).all()
    characters = {character.id: character for _, character in occurrences}
    try:
        # Validate database drafts too; a successful file import is not trusted forever.
        TemplateDefinition.model_validate(
            {
                "schema_version": 1,
                "id": str(template.template_id),
                "version": template.version,
                "description": "Content preview",
                "scenes": [
                    {
                        "scene_key": str(scene.scene_key),
                        "position": scene.position,
                        "scene_type": scene.scene_type,
                        "contract_version": scene.contract_version,
                        "required": scene.required,
                        "config": scene.config,
                    }
                    for scene in scenes
                ],
            }
        )
        VocabularyDefinition.model_validate(
            {
                "schema_version": 1,
                "id": str(word.id),
                "simplified": word.simplified,
                "pinyin": word.pinyin,
                "sino_vietnamese": word.sino_vietnamese,
                "vietnamese_meaning": word.vietnamese_meaning,
                "part_of_speech": word.part_of_speech,
                "notes": word.notes,
                "characters": [
                    {"id": str(char.id), "hanzi": char.hanzi, "stroke_count": char.stroke_count}
                    for char in characters.values()
                ],
                "occurrences": [
                    {"position": item.position, "character": str(item.character_id)}
                    for item, _ in occurrences
                ],
            }
        )
    except ValidationError:
        raise ContentError(
            "database draft has invalid scene contracts or character coverage"
        ) from None
    assets = {}
    for asset_id, prefix in [(word.audio_asset_id, "audio/")] + [
        (char.stroke_order_asset_id, "image/") for char in characters.values()
    ]:
        if asset_id:
            assets[str(asset_id)] = await _asset_projection(session, storage, asset_id, prefix)
    resolved_scenes = []
    for scene in scenes:
        config = dict(scene.config)
        # The only supported binding is finite and typed, never a property path or script.
        config["vocabulary_ref"] = {"kind": "VOCABULARY", "id": str(word.id)}
        resolved_scenes.append(
            {
                "scene_key": str(scene.scene_key),
                "position": scene.position,
                "scene_type": scene.scene_type,
                "contract_version": 1,
                "required": scene.required,
                "config": config,
            }
        )
    return {
        "schema_version": 1,
        "purpose": "CONTENT_PREVIEW",
        "learning_completion_supported": False,
        "lesson": {
            "id": str(lesson.id),
            "version_id": str(version.id),
            "version": version.version,
            "title": version.title,
            "lesson_type": "VOCABULARY",
        },
        "template": {"version_id": str(template.id), "version": template.version},
        "vocabulary": {
            "id": str(word.id),
            "simplified": word.simplified,
            "pinyin": word.pinyin,
            "sino_vietnamese": word.sino_vietnamese,
            "vietnamese_meaning": word.vietnamese_meaning,
            "part_of_speech": word.part_of_speech,
            "notes": word.notes,
            "revision": word.revision,
            "audio_asset_id": str(word.audio_asset_id) if word.audio_asset_id else None,
        },
        "characters": [
            {
                "id": str(char.id),
                "hanzi": char.hanzi,
                "stroke_count": char.stroke_count,
                "revision": char.revision,
                "analysis_status": "UNREVIEWED",
                "stroke_order_asset_id": (
                    str(char.stroke_order_asset_id) if char.stroke_order_asset_id else None
                ),
            }
            for char in characters.values()
        ],
        "occurrences": [
            {"position": item.position, "character_id": str(item.character_id)}
            for item, _ in occurrences
        ],
        "scenes": resolved_scenes,
        "assets": list(assets.values()),
    }, template


async def publish_lesson(
    session: AsyncSession, lesson_id: UUID, number: int, storage: ContentStorage
) -> str:
    async with session.begin():
        await lock_authoring(session)
        version = await session.scalar(
            select(LessonVersion)
            .where(LessonVersion.lesson_id == lesson_id, LessonVersion.version == number)
            .with_for_update()
        )
        if not version:
            raise ContentError("lesson version not found; import a draft first")
        if version.status != "DRAFT":
            raise ContentError("version already published; create a new version for corrections")
        bundle, template = await compile_draft(session, version, storage)
        data = canonical_bundle(bundle)
        digest = hashlib.sha256(data).hexdigest()
        key = storage.put_bundle(data)
        asset = await session.scalar(select(Asset).where(Asset.storage_key == key))
        if not asset:
            asset = Asset(
                id=uuid5(CONTENT_NAMESPACE, f"bundle:{digest}"),
                storage_key=key,
                media_type="application/json",
                sha256=digest,
                byte_length=len(data),
                asset_metadata={"format": "lesson-bundle-v1"},
            )
            session.add(asset)
            await session.flush()
        elif (
            asset.sha256 != digest
            or asset.byte_length != len(data)
            or asset.media_type != "application/json"
        ):
            raise ContentError("bundle asset conflicts with stored metadata")
        now = datetime.now(UTC)
        if template.status == "DRAFT":
            template.status, template.published_at = "PUBLISHED", now
            await session.flush()
        elif template.status != "PUBLISHED":
            raise ContentError("template version is unavailable")
        version.bundle_asset_id, version.published_at, version.status = asset.id, now, "PUBLISHED"
        await session.flush()
        return key


async def inspect_bundle(
    session: AsyncSession, lesson_id: UUID, number: int, storage: ContentStorage
) -> bytes:
    asset = await session.scalar(
        select(Asset)
        .join(LessonVersion, LessonVersion.bundle_asset_id == Asset.id)
        .where(
            LessonVersion.lesson_id == lesson_id,
            LessonVersion.version == number,
            LessonVersion.status == "PUBLISHED",
        )
    )
    if not asset:
        raise ContentError("published lesson bundle not found")
    return verify_object(storage, asset.storage_key, asset.sha256, asset.byte_length)
