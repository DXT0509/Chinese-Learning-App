"""Controlled draft import. This service owns its transaction and preserves legacy links."""

from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.schemas.content import content_id, version_id
from app.services.content_files import ContentError, ContentLibrary
from app.services.content_storage import ContentStorage, verify_object


async def lock_authoring(session: AsyncSession):
    # All local authoring commands share one short, transaction-scoped catalog lock.
    await session.execute(text("SELECT pg_advisory_xact_lock(807201, 1)"))


def _assign(row, values: dict, *, frozen: bool = False) -> bool:
    changed = any(getattr(row, key) != value for key, value in values.items())
    if changed and frozen:
        raise ContentError("published content is immutable; create a new version")
    if changed:
        for key, value in values.items():
            setattr(row, key, value)
    return changed


async def _has_publication(session: AsyncSession, word_id: UUID) -> bool:
    return bool(
        await session.scalar(
            select(LessonVocabulary.id)
            .join(LessonVersion, LessonVocabulary.lesson_version_id == LessonVersion.id)
            .where(LessonVocabulary.vocabulary_id == word_id, LessonVersion.status == "PUBLISHED")
            .limit(1)
        )
    )


async def import_library(
    session: AsyncSession, library: ContentLibrary, storage: ContentStorage
) -> None:
    """Atomic across all files. Published definitions may be repeated only identically."""
    async with session.begin():
        await lock_authoring(session)
        for definition in library.assets:
            verify_object(
                storage, definition.storage_key, definition.sha256, definition.byte_length
            )
            values = {
                "storage_key": definition.storage_key,
                "media_type": definition.media_type,
                "sha256": definition.sha256,
                "byte_length": definition.byte_length,
                "asset_metadata": definition.metadata.model_dump(exclude_none=True),
            }
            asset_id = content_id("asset", definition.id)
            existing = await session.get(Asset, asset_id)
            if existing:
                _assign(existing, values, frozen=True)
            else:
                session.add(Asset(id=asset_id, **values))
        await session.flush()

        for definition in library.vocabulary:
            for character in definition.characters:
                char_id = content_id("character", character.id)
                row = await session.get(Character, char_id)
                values = {
                    "hanzi": character.hanzi,
                    "stroke_count": character.stroke_count,
                    "stroke_order_asset_id": content_id("asset", character.stroke_order_asset)
                    if character.stroke_order_asset
                    else None,
                }
                if row:
                    if row.hanzi != character.hanzi:
                        raise ContentError("character identity cannot be relabeled")
                    if _assign(row, values):
                        row.revision += 1
                else:
                    if await session.scalar(
                        select(Character.id).where(Character.hanzi == character.hanzi)
                    ):
                        raise ContentError("character already exists; adopt its explicit UUID")
                    session.add(Character(id=char_id, **values))
            await session.flush()
            word_id = content_id("vocabulary", definition.id)
            values = {
                key: getattr(definition, key)
                for key in (
                    "simplified",
                    "pinyin",
                    "sino_vietnamese",
                    "vietnamese_meaning",
                    "notes",
                    "part_of_speech",
                )
            }
            values["audio_asset_id"] = (
                content_id("asset", definition.audio_asset) if definition.audio_asset else None
            )
            row = await session.get(Vocabulary, word_id)
            if row:
                if any(
                    getattr(row, key) != values[key]
                    for key in ("simplified", "pinyin", "vietnamese_meaning")
                ):
                    raise ContentError(
                        "lexical identity cannot be relabeled; use a new vocabulary ID"
                    )
                if _assign(row, values):
                    row.revision += 1
            else:
                if await session.scalar(
                    select(Vocabulary.id).where(
                        Vocabulary.simplified == definition.simplified,
                        Vocabulary.pinyin == definition.pinyin,
                        Vocabulary.vietnamese_meaning == definition.vietnamese_meaning,
                    )
                ):
                    raise ContentError("vocabulary already exists; adopt its explicit UUID")
                session.add(Vocabulary(id=word_id, **values))
            await session.flush()
            existing = {
                item.position: item
                for item in (
                    await session.scalars(
                        select(VocabularyCharacter).where(
                            VocabularyCharacter.vocabulary_id == word_id
                        )
                    )
                ).all()
            }
            desired = {
                item.position: content_id("character", item.character)
                for item in definition.occurrences
            }
            if set(existing) - set(desired):
                raise ContentError("existing character occurrences need a reviewed reconciliation")
            frozen = await _has_publication(session, word_id)
            for position, char_id in desired.items():
                if position in existing:
                    _assign(existing[position], {"character_id": char_id}, frozen=frozen)
                elif frozen:
                    raise ContentError("published character occurrences are immutable")
                else:
                    session.add(
                        VocabularyCharacter(
                            vocabulary_id=word_id, position=position, character_id=char_id
                        )
                    )

        for definition in library.templates:
            template_id = content_id("template", definition.id)
            template = await session.get(LessonTemplate, template_id)
            if template:
                if template.code != definition.id:
                    raise ContentError("template identity/code does not match")
                _assign(template, {"description": definition.description})
            else:
                session.add(
                    LessonTemplate(
                        id=template_id, code=definition.id, description=definition.description
                    )
                )
            await session.flush()
            template_version_id = version_id("template", definition.id, definition.version)
            version = await session.get(LessonTemplateVersion, template_version_id)
            if not version:
                version = LessonTemplateVersion(
                    id=template_version_id,
                    template_id=template_id,
                    version=definition.version,
                    status="DRAFT",
                )
                session.add(version)
                await session.flush()
            frozen = version.status == "PUBLISHED"
            existing = {
                item.scene_key: item
                for item in (
                    await session.scalars(
                        select(LessonTemplateScene).where(
                            LessonTemplateScene.template_version_id == template_version_id
                        )
                    )
                ).all()
            }
            desired = {content_id("scene", item.scene_key) for item in definition.scenes}
            if set(existing) - desired:
                raise ContentError("scene removal requires a new template version")
            for scene in definition.scenes:
                scene_id = content_id("scene", scene.scene_key)
                values = scene.model_dump(exclude={"scene_key", "config"})
                values["config"] = scene.config.model_dump()
                if scene_id in existing:
                    _assign(existing[scene_id], values, frozen=frozen)
                elif frozen:
                    raise ContentError("published template is immutable; create a new version")
                else:
                    session.add(
                        LessonTemplateScene(
                            template_version_id=template_version_id, scene_key=scene_id, **values
                        )
                    )
            await session.flush()

        for definition in library.lessons:
            lesson_id = content_id("lesson", definition.id)
            lesson = await session.get(Lesson, lesson_id)
            if lesson:
                if lesson.lesson_type != definition.lesson_type:
                    raise ContentError("legacy lesson type requires reviewed reconciliation")
                if lesson.code is None:
                    lesson.code = definition.id
                elif lesson.code != definition.id:
                    raise ContentError("lesson identity/code does not match")
            else:
                next_order = await session.scalar(select(func.max(Lesson.lesson_order)))
                session.add(
                    Lesson(
                        id=lesson_id,
                        code=definition.id,
                        title=definition.title,
                        lesson_type=definition.lesson_type,
                        lesson_order=0 if next_order is None else next_order + 1,
                    )
                )
            await session.flush()
            lesson_version_id = version_id("lesson", definition.id, definition.version)
            values = {
                "title": definition.title,
                "template_version_id": version_id(
                    "template", definition.template.id, definition.template.version
                ),
            }
            version = await session.get(LessonVersion, lesson_version_id)
            if version:
                _assign(version, values, frozen=version.status == "PUBLISHED")
            else:
                version = LessonVersion(
                    id=lesson_version_id,
                    lesson_id=lesson_id,
                    version=definition.version,
                    status="DRAFT",
                    **values,
                )
                session.add(version)
                await session.flush()
            target = definition.vocabulary[0]
            existing = (
                await session.scalars(
                    select(LessonVocabulary).where(
                        LessonVocabulary.lesson_version_id == lesson_version_id
                    )
                )
            ).all()
            values = {
                "vocabulary_id": content_id("vocabulary", target.vocabulary),
                "position": target.position,
                "role": target.role,
            }
            if len(existing) > 1:
                raise ContentError("draft has multiple targets; reconcile memberships explicitly")
            if existing:
                _assign(existing[0], values, frozen=version.status == "PUBLISHED")
            elif version.status == "PUBLISHED":
                raise ContentError("published membership is incomplete")
            else:
                session.add(
                    LessonVocabulary(
                        lesson_id=lesson_id, lesson_version_id=lesson_version_id, **values
                    )
                )
        await session.flush()
