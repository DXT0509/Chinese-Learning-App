"""Authoritative availability, evidence and exactly-once completion transactions."""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import exists, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import load_only

from app.models import LessonVersion, User
from app.models.curated_vocabulary import VocabularyRevision
from app.models.roadmap import (
    ActivityReceipt,
    ExpGrant,
    NodeProgress,
    NodeRun,
    Roadmap,
    RoadmapVersion,
    RoadmapVocabulary,
)
from app.models.roadmap import (
    RoadmapNodeVersion as Node,
)
from app.schemas.roadmap import ActivitySubmission, NodeDefinition, Rewards
from app.services.curated_catalog import CuratedCatalog


def fail(code, detail, status=409):
    raise HTTPException(status, {"code": code, "message": detail})


def evaluate(activity, evidence):
    """Explicit participation checks; no claims about handwriting/pronunciation quality."""
    if evidence.repetition >= activity.repetitions:
        return False
    if activity.kind == "QUIZ":
        return (
            evidence.kind == "CHOICE"
            and not evidence.strokes
            and evidence.choice == activity.correct_option
        )
    if activity.kind == "HANDWRITING":
        return (
            evidence.kind == "FREEHAND"
            and bool(evidence.strokes)
            and evidence.choice is None
            and evidence.duration_ms >= 1000
        )
    if activity.kind == "PRONUNCIATION":
        return (
            evidence.kind == "SPEAKING"
            and not evidence.strokes
            and evidence.choice is None
            and evidence.duration_ms >= 1000
        )
    return evidence.kind == "ACKNOWLEDGE" and evidence.choice is None and not evidence.strokes


class RoadmapService:
    def __init__(self, session):
        self.session = session

    async def serialize_owner(self, owner):
        # Same lock order as the daily review planner. Serializes absent progress rows too.
        if not await self.session.scalar(select(User.id).where(User.id == owner).with_for_update()):
            fail("NOT_FOUND", "User not found", 404)

    async def browse(self, offset, limit):
        rows = (
            await self.session.execute(
                select(Roadmap, RoadmapVersion)
                .options(load_only(RoadmapVersion.id, RoadmapVersion.title, RoadmapVersion.version))
                .join(RoadmapVersion, RoadmapVersion.id == Roadmap.active_version_id)
                .where(RoadmapVersion.status == "PUBLISHED")
                .order_by(Roadmap.code, Roadmap.id)
                .offset(offset)
                .limit(limit + 1)
            )
        ).all()
        return {
            "items": [
                {
                    "id": r.id,
                    "code": r.code,
                    "version_id": v.id,
                    "title": v.title,
                    "version": v.version,
                }
                for r, v in rows[:limit]
            ],
            "next_offset": offset + limit if len(rows) > limit else None,
        }

    def blocking(self, owner, version_id, position=None):
        progressed = exists(
            select(NodeProgress.node_id).where(
                NodeProgress.user_id == owner,
                NodeProgress.node_id == Node.node_id,
                NodeProgress.status.in_(["COMPLETED", "SKIPPED"]),
            )
        )
        query = select(func.min(Node.position)).where(
            Node.roadmap_version_id == version_id, ~progressed
        )
        if position is not None:
            query = query.where(Node.position < position)
        return query

    async def nodes(self, owner, roadmap_id, version_id, after, limit):
        roadmap = await self.session.get(Roadmap, roadmap_id)
        identifier = version_id or (roadmap.active_version_id if roadmap else None)
        published = (
            await self.session.scalar(
                select(RoadmapVersion.id).where(
                    RoadmapVersion.id == identifier,
                    RoadmapVersion.roadmap_id == roadmap_id,
                    RoadmapVersion.status == "PUBLISHED",
                )
            )
            if identifier
            else None
        )
        if not published:
            fail("NOT_FOUND", "Roadmap not found", 404)
        boundary = await self.session.scalar(self.blocking(owner, identifier))
        content = LessonVersion.engine_definition
        rows = (
            await self.session.execute(
                select(
                    Node,
                    NodeProgress.status,
                    content["node_type"].astext,
                    content["title"].astext,
                    content["section"].astext,
                    content["visual"],
                )
                .join(LessonVersion, LessonVersion.id == Node.lesson_version_id)
                .outerjoin(
                    NodeProgress,
                    (NodeProgress.node_id == Node.node_id) & (NodeProgress.user_id == owner),
                )
                .where(Node.roadmap_version_id == identifier, Node.position > after)
                .order_by(Node.position)
                .limit(limit + 1)
            )
        ).all()
        return {
            "roadmap_version_id": identifier,
            "current_position": boundary,
            "section_positions": dict(
                (
                    await self.session.execute(
                        select(content["section"].astext.label("section"), func.min(Node.position))
                        .join(LessonVersion, LessonVersion.id == Node.lesson_version_id)
                        .where(Node.roadmap_version_id == identifier)
                        .group_by("section")
                    )
                ).all()
            ),
            "items": [
                {
                    "id": n.node_id,
                    "node_version_id": n.id,
                    "position": n.position,
                    "node_type": kind,
                    "title": title,
                    "section": section,
                    "visual": visual,
                    "status": status or "NOT_STARTED",
                    "available": boundary is None
                    or n.position <= boundary
                    or status in ("COMPLETED", "SKIPPED"),
                }
                for n, status, kind, title, section, visual in rows[:limit]
            ],
            "next_position": rows[limit - 1][0].position if len(rows) > limit else None,
        }

    async def context(self, owner, identifier, require_available=True):
        row = (
            await self.session.execute(
                select(
                    Node,
                    LessonVersion,
                    RoadmapVersion,
                    Roadmap,
                    RoadmapVersion.definition["rewards"],
                    RoadmapVersion.definition["allow_review_skip"],
                )
                .options(
                    load_only(RoadmapVersion.id, RoadmapVersion.roadmap_id, RoadmapVersion.status)
                )
                .join(LessonVersion, LessonVersion.id == Node.lesson_version_id)
                .join(RoadmapVersion, RoadmapVersion.id == Node.roadmap_version_id)
                .join(Roadmap, Roadmap.id == RoadmapVersion.roadmap_id)
                .where(
                    Node.id == identifier,
                    RoadmapVersion.status == "PUBLISHED",
                    LessonVersion.status == "PUBLISHED",
                )
            )
        ).first()
        if not row:
            fail("NOT_FOUND", "Node not found", 404)
        node, lesson, version, roadmap, rewards, allow_review_skip = row
        progress = await self.session.get(NodeProgress, (owner, node.node_id))
        historical_run = await self.session.scalar(
            select(NodeRun.id)
            .where(NodeRun.user_id == owner, NodeRun.node_version_id == identifier)
            .limit(1)
        )
        if roadmap.active_version_id != version.id and not historical_run:
            fail("VERSION_UNAVAILABLE", "Start nodes from the active roadmap")
        if (
            require_available
            and not historical_run
            and not (progress and progress.status in ("COMPLETED", "SKIPPED"))
            and await self.session.scalar(self.blocking(owner, version.id, node.position))
            is not None
        ):
            fail("NODE_LOCKED", "Complete or skip preceding nodes", 403)
        return node, lesson, {"rewards": rewards, "allow_review_skip": allow_review_skip}, progress

    async def detail(self, owner, identifier):
        node, lesson, _, _ = await self.context(owner, identifier)
        definition = NodeDefinition.model_validate(lesson.engine_definition).model_dump(mode="json")
        for activity in definition["lesson"]["activities"]:
            activity.pop("correct_option", None)
        revisions = (
            (
                await self.session.execute(
                    select(VocabularyRevision)
                    .join(
                        RoadmapVocabulary,
                        (RoadmapVocabulary.vocabulary_id == VocabularyRevision.vocabulary_id)
                        & (RoadmapVocabulary.content_version == VocabularyRevision.content_version),
                    )
                    .where(RoadmapVocabulary.node_version_id == node.id)
                )
            )
            .scalars()
            .all()
        )
        # Project educational fields only, pinned to catalog history rather than today's entry.
        by_id = {
            revision.vocabulary_id: {
                "vocabulary_id": str(revision.vocabulary_id),
                "content_version": revision.content_version,
                **{
                    key: revision.payload.get(key)
                    for key in (
                        "simplified",
                        "pinyin",
                        "pinyin_numbered",
                        "sino_vietnamese",
                        "vietnamese_meanings",
                        "examples",
                    )
                },
            }
            for revision in revisions
        }
        return {
            "node_version_id": node.id,
            "lesson_version_id": lesson.id,
            "definition": definition,
            "vocabulary": [
                by_id[ref.vocabulary_id]
                for ref in NodeDefinition.model_validate(lesson.engine_definition).lesson.vocabulary
            ],
        }

    async def run_view(self, run):
        accepted = list(
            await self.session.scalars(
                select(ActivityReceipt.activity_id)
                .where(ActivityReceipt.run_id == run.id, ActivityReceipt.accepted)
                .distinct()
            )
        )
        return {
            "id": run.id,
            "node_version_id": run.node_version_id,
            "replay": run.replay,
            "completed_at": run.completed_at,
            "accepted_activity_ids": accepted,
            "accepted_repetitions": await self.accepted_repetitions(run.id),
        }

    async def accepted_repetitions(self, run_id):
        rows = (
            await self.session.execute(
                select(ActivityReceipt.activity_id, ActivityReceipt.evidence).where(
                    ActivityReceipt.run_id == run_id, ActivityReceipt.accepted
                )
            )
        ).all()
        result = {}
        for activity_id, evidence in rows:
            result.setdefault(str(activity_id), set()).add(evidence["repetition"])
        return {key: sorted(value) for key, value in result.items()}

    async def media(self, owner, identifier, asset_id):
        from starlette.concurrency import run_in_threadpool

        from app.core.config import get_settings
        from app.models import Asset
        from app.services.content_files import ContentError
        from app.services.content_storage import LocalContentStorage, verify_object

        _, lesson, _, _ = await self.context(owner, identifier)
        content = NodeDefinition.model_validate(lesson.engine_definition).lesson
        enrichments = [content.audio, content.examples, content.notes, content.stroke_order]
        enrichments += [component.explanation for component in content.components]
        if not any(e.status == "AVAILABLE" and e.asset_id == asset_id for e in enrichments):
            fail("NOT_FOUND", "Asset unavailable", 404)
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            fail("NOT_FOUND", "Asset unavailable", 404)
        try:
            raw = await run_in_threadpool(
                verify_object,
                LocalContentStorage(get_settings().content_storage_dir),
                asset.storage_key,
                asset.sha256,
                asset.byte_length,
            )
        except ContentError:
            fail("ASSET_UNAVAILABLE", "Asset temporarily unavailable", 503)
        return raw, asset.media_type

    async def start(self, owner, identifier, replay=False, request_id=None):
        async with self.session.begin():
            await self.serialize_owner(owner)
            node, _, _, progress = await self.context(owner, identifier)
            if replay and (not progress or progress.status != "COMPLETED"):
                fail("NOT_COMPLETED", "Replay requires prior completion")
            if replay and request_id is None:
                fail("REPLAY_ID_REQUIRED", "Replay requires a request identity", 422)
            if replay:
                run = await self.session.get(NodeRun, request_id)
                if run and (
                    run.user_id != owner or run.node_version_id != identifier or not run.replay
                ):
                    fail("IDEMPOTENCY_CONFLICT", "Replay identity conflict")
            else:
                run = await self.session.scalar(
                    select(NodeRun).where(
                        NodeRun.user_id == owner,
                        NodeRun.node_version_id == identifier,
                        ~NodeRun.replay,
                    )
                )
            if not run:
                run_id = request_id if replay else uuid4()
                await self.session.execute(
                    insert(NodeRun)
                    .values(id=run_id, user_id=owner, node_version_id=identifier, replay=replay)
                    .on_conflict_do_nothing()
                )
                run = await self.session.get(NodeRun, run_id)
                if (
                    not run
                    or run.user_id != owner
                    or run.node_version_id != identifier
                    or run.replay != replay
                ):
                    fail("IDEMPOTENCY_CONFLICT", "Run identity conflict")
            if progress is None:
                progress = NodeProgress(user_id=owner, node_id=node.node_id, status="IN_PROGRESS")
                self.session.add(progress)
            elif progress.status != "COMPLETED":
                progress.status = "IN_PROGRESS"
            await self.session.flush()
            return await self.run_view(run)

    async def owned_run(self, owner, identifier):
        run = await self.session.scalar(
            select(NodeRun).where(NodeRun.id == identifier, NodeRun.user_id == owner)
        )
        if not run:
            fail("NOT_FOUND", "Run not found", 404)
        return run

    async def record(self, owner, identifier, evidence: ActivitySubmission):
        async with self.session.begin():
            await self.serialize_owner(owner)
            run = await self.owned_run(owner, identifier)
            _, lesson, _, _ = await self.context(owner, run.node_version_id)
            payload = evidence.model_dump(mode="json")
            receipt = await self.session.get(ActivityReceipt, (run.id, evidence.request_id))
            if receipt:
                if receipt.evidence != payload:
                    fail(
                        "IDEMPOTENCY_CONFLICT", "Request identity was used with different evidence"
                    )
                return {"accepted": receipt.accepted, "evaluator": receipt.evaluator}
            if run.completed_at:
                fail("RUN_COMPLETED", "Use the practice run for replay")
            activity = next(
                (
                    a
                    for a in NodeDefinition.model_validate(
                        lesson.engine_definition
                    ).lesson.activities
                    if a.id == evidence.activity_id
                ),
                None,
            )
            if activity is None:
                fail("ACTIVITY_NOT_FOUND", "Activity not in pinned lesson", 422)
            accepted = evaluate(activity, evidence)
            evaluator = "exact-choice-v1" if activity.kind == "QUIZ" else "participation-v1"
            self.session.add(
                ActivityReceipt(
                    run_id=run.id,
                    request_id=evidence.request_id,
                    activity_id=activity.id,
                    evidence=payload,
                    accepted=accepted,
                    evaluator=evaluator,
                )
            )
            return {"accepted": accepted, "evaluator": evaluator}

    async def complete(self, owner, identifier):
        async with self.session.begin():
            await self.serialize_owner(owner)
            run = await self.owned_run(owner, identifier)
            node, lesson, version, progress = await self.context(owner, run.node_version_id)
            if run.completed_at:
                return {"status": "COMPLETED", "exp_awarded": 0}
            definition = NodeDefinition.model_validate(lesson.engine_definition)
            receipts = list(
                await self.session.scalars(
                    select(ActivityReceipt).where(
                        ActivityReceipt.run_id == run.id, ActivityReceipt.accepted
                    )
                )
            )
            for activity in definition.lesson.activities:
                repetitions = {
                    r.evidence["repetition"] for r in receipts if r.activity_id == activity.id
                }
                if activity.required and len(repetitions) < activity.repetitions:
                    fail("ACTIVITIES_INCOMPLETE", "Required activities are incomplete")
            now, amount = datetime.now(UTC), 0
            if progress.status != "COMPLETED":
                if definition.node_type == "NEW_WORD":
                    await CuratedCatalog(self.session).enqueue_lesson_word(
                        owner, definition.lesson.vocabulary[0].vocabulary_id
                    )
                rewards = Rewards.model_validate(version["rewards"])
                reward = rewards.new_word if definition.node_type == "NEW_WORD" else rewards.review
                amount = (
                    await self.session.scalar(
                        insert(ExpGrant)
                        .values(
                            user_id=owner,
                            node_id=node.node_id,
                            node_version_id=node.id,
                            amount=reward,
                        )
                        .on_conflict_do_nothing()
                        .returning(ExpGrant.amount)
                    )
                    or 0
                )
                progress.status, progress.completed_at = "COMPLETED", now
                progress.first_completed_version_id = node.id
            run.completed_at = now
            return {"status": "COMPLETED", "exp_awarded": amount}

    async def skip(self, owner, identifier):
        async with self.session.begin():
            await self.serialize_owner(owner)
            node, lesson, version, progress = await self.context(owner, identifier)
            if progress and progress.status == "COMPLETED":
                return {"status": "COMPLETED", "exp_awarded": 0}
            if (
                lesson.engine_definition["node_type"] == "REVIEW"
                and not version["allow_review_skip"]
            ):
                fail("REVIEW_GATE_REQUIRED", "Review gate cannot be skipped")
            if progress:
                progress.status = "SKIPPED"
            else:
                self.session.add(
                    NodeProgress(user_id=owner, node_id=node.node_id, status="SKIPPED")
                )
            return {"status": "SKIPPED", "exp_awarded": 0}

    async def summary(self, owner):
        total = await self.session.scalar(
            select(func.coalesce(func.sum(ExpGrant.amount), 0)).where(ExpGrant.user_id == owner)
        )
        completed, skipped = (
            await self.session.execute(
                select(
                    func.count().filter(NodeProgress.status == "COMPLETED"),
                    func.count().filter(NodeProgress.status == "SKIPPED"),
                ).where(NodeProgress.user_id == owner)
            )
        ).one()
        return {"total_exp": total, "completed_nodes": completed, "skipped_nodes": skipped}
