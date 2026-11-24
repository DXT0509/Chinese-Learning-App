"""Local draft/preview/publication operations. No automatic educational approval."""

import hashlib
from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid5

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from starlette.concurrency import run_in_threadpool

from app.models import Asset, Lesson, LessonTemplate, LessonTemplateVersion, LessonVersion
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyRevision
from app.models.roadmap import (
    Roadmap,
    RoadmapNode,
    RoadmapNodeVersion,
    RoadmapVersion,
    RoadmapVocabulary,
)
from app.schemas.roadmap import RoadmapDefinition
from app.services.content_files import ContentError
from app.services.content_storage import verify_object
from app.services.curated_catalog import visible
from app.services.lesson_publication import canonical_bundle

NAMESPACE = UUID("c3bc39e7-ae77-465d-a08a-1f15cced74c9")
TEMPLATE_ID = uuid5(NAMESPACE, "executable-v1")
TEMPLATE_VERSION_ID = uuid5(TEMPLATE_ID, "1")


def version_id(definition):
    return uuid5(definition.id, str(definition.version))


async def lock(session):
    # Shared with the existing content authoring pipeline's lesson-order namespace.
    from app.services.content_authoring import lock_authoring

    await lock_authoring(session)


async def import_draft(session, definition: RoadmapDefinition):
    async with session.begin():
        await lock(session)
        roadmap = await session.get(Roadmap, definition.id)
        if roadmap is None:
            session.add(Roadmap(id=definition.id, code=definition.code))
            await session.flush()
        elif roadmap.code != definition.code:
            raise ContentError("stable roadmap identity cannot change")
        identifier = version_id(definition)
        existing = await session.get(RoadmapVersion, identifier)
        payload = definition.model_dump(mode="json")
        if existing:
            if existing.status == "PUBLISHED" or existing.definition != payload:
                raise ContentError("use a new version for corrections")
            return identifier
        await session.execute(
            insert(LessonTemplate)
            .values(
                id=TEMPLATE_ID,
                code="roadmap-engine-v1",
                description="Executable curated activities",
            )
            .on_conflict_do_nothing()
        )
        await session.execute(
            insert(LessonTemplateVersion)
            .values(id=TEMPLATE_VERSION_ID, template_id=TEMPLATE_ID, version=1)
            .on_conflict_do_nothing()
        )
        session.add(
            RoadmapVersion(
                id=identifier,
                roadmap_id=definition.id,
                version=definition.version,
                title=definition.title,
                definition=payload,
            )
        )
        await session.flush()
        order = (await session.scalar(select(func.max(Lesson.lesson_order)))) or 0
        for offset, node in enumerate(definition.nodes, start=1):
            identity = await session.get(RoadmapNode, node.id)
            word_id = (
                node.lesson.vocabulary[0].vocabulary_id if node.node_type == "NEW_WORD" else None
            )
            if identity is None:
                session.add(
                    RoadmapNode(
                        id=node.id,
                        roadmap_id=definition.id,
                        node_type=node.node_type,
                        vocabulary_id=word_id,
                    )
                )
            elif (identity.roadmap_id, identity.node_type, identity.vocabulary_id) != (
                definition.id,
                node.node_type,
                word_id,
            ):
                raise ContentError("stable node identity cannot be repurposed")
            # Reuse lesson identity and lesson_versions, without inventing legacy TEACHES links.
            if not await session.get(Lesson, node.id):
                session.add(
                    Lesson(
                        id=node.id,
                        code=f"roadmap-{node.id}",
                        title=node.title,
                        lesson_type="VOCABULARY" if word_id else "REVIEW",
                        lesson_order=order + offset,
                    )
                )
            await session.flush()
            lesson_id = uuid5(identifier, f"lesson:{node.id}")
            session.add(
                LessonVersion(
                    id=lesson_id,
                    lesson_id=node.id,
                    version=definition.version,
                    title=node.title,
                    template_version_id=TEMPLATE_VERSION_ID,
                    engine_definition=node.model_dump(mode="json"),
                )
            )
            await session.flush()
            node_version_id = uuid5(identifier, str(node.id))
            session.add(
                RoadmapNodeVersion(
                    id=node_version_id,
                    roadmap_version_id=identifier,
                    node_id=node.id,
                    position=node.position,
                    lesson_version_id=lesson_id,
                )
            )
            await session.flush()
            for ref in node.lesson.vocabulary:
                session.add(RoadmapVocabulary(node_version_id=node_version_id, **ref.model_dump()))
        return identifier


async def compile_preview(session, identifier, storage):
    version = await session.get(RoadmapVersion, identifier, with_for_update=True)
    if version is None:
        raise ContentError("roadmap version not found")
    definition = RoadmapDefinition.model_validate(version.definition)
    rows = (
        await session.execute(
            select(RoadmapNodeVersion, LessonVersion)
            .join(LessonVersion, LessonVersion.id == RoadmapNodeVersion.lesson_version_id)
            .where(RoadmapNodeVersion.roadmap_version_id == identifier)
            .order_by(RoadmapNodeVersion.position)
        )
    ).all()
    if len(rows) != len(definition.nodes):
        raise ContentError("incomplete node membership")
    for node, (membership, lesson) in zip(definition.nodes, rows, strict=True):
        if (
            membership.node_id != node.id
            or membership.position != node.position
            or lesson.engine_definition != node.model_dump(mode="json")
        ):
            raise ContentError("lesson definition differs from roadmap")
        refs = (
            await session.execute(
                select(RoadmapVocabulary.vocabulary_id, RoadmapVocabulary.content_version).where(
                    RoadmapVocabulary.node_version_id == membership.id
                )
            )
        ).all()
        if set(refs) != {(r.vocabulary_id, r.content_version) for r in node.lesson.vocabulary}:
            raise ContentError("vocabulary membership differs from definition")
        for ref in node.lesson.vocabulary:
            word = await session.scalar(
                select(CuratedVocabulary)
                .where(CuratedVocabulary.id == ref.vocabulary_id, visible())
                .with_for_update(read=True)
            )
            revision = await session.get(
                VocabularyRevision,
                (ref.vocabulary_id, ref.content_version),
                with_for_update={"read": True},
            )
            if (
                not word
                or not revision
                or word.content_version != ref.content_version
                or word.checksum != revision.checksum
            ):
                raise ContentError("publication requires current reviewed catalog revision")
            for component in node.lesson.components:
                if component.character_position >= len(word.simplified):
                    raise ContentError("component character position outside word")
        enrichments = [
            node.lesson.audio,
            node.lesson.examples,
            node.lesson.notes,
            node.lesson.stroke_order,
            *[c.explanation for c in node.lesson.components],
        ]
        if any(e.status == "UNREVIEWED" for e in enrichments):
            raise ContentError("unreviewed enrichment cannot be published")
        for enrichment in enrichments:
            if enrichment.asset_id:
                asset = await session.get(Asset, enrichment.asset_id)
                if not asset:
                    raise ContentError("missing asset")
                if enrichment is node.lesson.audio and not asset.media_type.startswith("audio/"):
                    raise ContentError("pronunciation asset must be audio")
                await run_in_threadpool(
                    verify_object, storage, asset.storage_key, asset.sha256, asset.byte_length
                )
        kinds = {a.kind for a in node.lesson.activities}
        if "COMPONENTS" in kinds and not node.lesson.components:
            raise ContentError("component activity requires reviewed components")
        if "STROKE_ORDER" in kinds and node.lesson.stroke_order.status != "AVAILABLE":
            raise ContentError("stroke-order activity requires reviewed reference")
    return definition, rows


async def store_bundle(session, storage, payload):
    data = canonical_bundle(payload)
    key = await run_in_threadpool(storage.put_bundle, data)
    asset = await session.scalar(select(Asset).where(Asset.storage_key == key))
    if asset is None:
        asset = Asset(
            id=uuid4(),
            storage_key=key,
            media_type="application/json",
            sha256=hashlib.sha256(data).hexdigest(),
            byte_length=len(data),
            asset_metadata={"purpose": "ROADMAP_ENGINE"},
        )
        session.add(asset)
        await session.flush()
    return asset.id


async def publish(session, identifier, storage, reviewed_by):
    if not reviewed_by.strip():
        raise ContentError("explicit operator review attestation is required")
    async with session.begin():
        await lock(session)
        version = await session.get(RoadmapVersion, identifier, with_for_update=True)
        if not version or version.status != "DRAFT":
            raise ContentError("only a draft can be published")
        definition, rows = await compile_preview(session, identifier, storage)
        template = await session.get(LessonTemplateVersion, TEMPLATE_VERSION_ID)
        if template.status == "DRAFT":
            template.status, template.published_at = "PUBLISHED", datetime.now(UTC)
            await session.flush()
        for _, lesson in rows:
            lesson.bundle_asset_id = await store_bundle(session, storage, lesson.engine_definition)
            lesson.status, lesson.published_at = "PUBLISHED", datetime.now(UTC)
        await session.flush()
        version.bundle_asset_id = await store_bundle(
            session,
            storage,
            {
                "purpose": "ROADMAP_ENGINE",
                "definition": definition.model_dump(mode="json"),
                "operator_attestation": reviewed_by,
            },
        )
        version.status, version.published_at = "PUBLISHED", datetime.now(UTC)
        await session.flush()
        roadmap = await session.get(Roadmap, version.roadmap_id, with_for_update=True)
        roadmap.active_version_id = version.id


async def activate(session, roadmap_id, identifier):
    """None depublishes discovery; old published runs remain accessible and immutable."""
    async with session.begin():
        await lock(session)
        roadmap = await session.get(Roadmap, roadmap_id, with_for_update=True)
        version = await session.get(RoadmapVersion, identifier) if identifier else None
        if not roadmap or (
            identifier
            and (not version or version.roadmap_id != roadmap_id or version.status != "PUBLISHED")
        ):
            raise ContentError("invalid activation target")
        roadmap.active_version_id = identifier
