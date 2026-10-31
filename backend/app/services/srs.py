"""Transaction-owning SRS access and scheduling. No client outcome writer."""

from collections.abc import Callable
from dataclasses import asdict, replace
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.models.srs import SrsTargetPolicy
from app.models.srs_v2 import SrsMemory
from app.services import fsrs_scheduler
from app.services.curated_catalog import visible
from app.services.daily_review import DailyReview
from app.services.review_mastery import advance_mastery
from app.services.review_targets import ReviewedTargets
from app.services.srs_contract import ReviewTarget, Stage, ValidatedReview
from app.services.srs_state import Outcome, Phase, State, utc


def state_of(saved):
    return State(
        saved.mastery_level,
        Phase(saved.phase),
        saved.phase_step,
        saved.level_progress,
        saved.next_review_at,
        saved.last_reviewed_at,
    )


def state_json(state):
    return {
        k: utc(v).isoformat() if isinstance(v, datetime) else v for k, v in asdict(state).items()
    }


def progress_json(saved):
    return {
        "saved_id": saved.id,
        "vocabulary_id": saved.vocabulary_id,
        **state_json(state_of(saved)),
        "is_active": saved.is_active,
        "schedule_version": saved.schedule_version,
        "due_review_count": saved.due_review_count,
        "failure_count": saved.failure_count,
        "practice_count": saved.practice_count,
    }


class TargetResolver(Protocol):
    async def resolve(self, session, word: Word) -> ReviewTarget:
        """Server-owned pinned sense/answer policy, gradeable flag and ordered stages.

        Must include content_version/checksum. No HTTP input can supply this policy.
        The default implementation requires an operator-reviewed sense policy.
        """
        ...


class SrsService:
    def __init__(
        self,
        session,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        targets: TargetResolver | None = None,
    ):
        self.session, self.clock = session, clock
        self.targets = targets or ReviewedTargets()

    def planner(self):
        return DailyReview(self.session, self.clock, self.targets)

    def available(self, owner):
        return select(Saved).join(Word).where(Saved.user_id == owner, Saved.is_active, visible())

    async def dashboard(self, owner):
        now = utc(self.clock())
        available = self.available(owner).subquery()
        total, due, *mastery_counts = (
            await self.session.execute(
                select(
                    func.count(),
                    func.count().filter(
                        (available.c.next_review_at <= now) | ~available.c.learning_activated
                    ),
                    *[
                        func.count().filter(available.c.mastery_level == level)
                        for level in range(6)
                    ],
                ).select_from(available)
            )
        ).one()
        active = await self.session.scalar(
            select(func.count()).select_from(Saved).where(Saved.user_id == owner, Saved.is_active)
        )
        grading_available = False
        candidates = await self.session.scalars(
            select(Word)
            .join(Saved)
            .join(
                SrsTargetPolicy,
                (
                    (SrsTargetPolicy.vocabulary_id == Word.id)
                    & (SrsTargetPolicy.content_version == Word.content_version)
                    & (SrsTargetPolicy.checksum == Word.checksum)
                ),
            )
            .where(Saved.user_id == owner, Saved.is_active, visible())
        )
        for word in candidates:
            if (await self.targets.resolve(self.session, word)).gradeable:
                grading_available = True
                break
        result = {
            "scheduler_version": fsrs_scheduler.VERSION,
            "as_of": now,
            "available_count": total,
            "due_count": due,
            "suspended_count": active - total,
            "grading_available": grading_available,
            "mastery_distribution": [
                {"mastery_level": level, "count": count}
                for level, count in enumerate(mastery_counts)
            ],
        }
        result["daily_review"] = await self.planner().metrics(owner)
        return result

    async def due(self, owner, limit):
        now = utc(self.clock())
        rows = await self.session.scalars(
            self.available(owner)
            .where((Saved.next_review_at <= now) | ~Saved.learning_activated)
            .order_by(Saved.next_review_at, Saved.id)
            .limit(limit)
        )
        return {"as_of": now, "items": [progress_json(row) for row in rows]}

    async def progress(self, owner, saved_id):
        row = await self.session.scalar(
            select(Saved).where(Saved.user_id == owner, Saved.id == saved_id)
        )
        if row is None:
            raise HTTPException(404, "Vocabulary progress not found")
        available = bool(
            await self.session.scalar(select(visible()).where(Word.id == row.vocabulary_id))
        )
        return {**progress_json(row), "available": available and row.is_active}

    async def initialize(self, owner, saved_id, request_id: UUID | None = None):
        async with self.session.begin():
            saved = await self.session.scalar(
                select(Saved)
                .where(Saved.user_id == owner, Saved.id == saved_id, Saved.is_active)
                .with_for_update()
            )
            if saved is None:
                raise HTTPException(404, "Vocabulary progress not found")
            if request_id is not None:
                existing = await self.session.get(Attempt, request_id)
                if existing is not None:
                    if existing.user_vocabulary_id != saved.id:
                        raise HTTPException(409, "Review request identity conflict")
                    return self._initialization_response(existing)
            word = await self.session.scalar(
                select(Word)
                .where(Word.id == saved.vocabulary_id, visible())
                .with_for_update(read=True)
            )
            if word is None:
                raise HTTPException(409, "Vocabulary unavailable for review")
            now = utc(self.clock())
            policy = await self.targets.resolve(self.session, word)
            if (policy.vocabulary_id, policy.content_version, policy.checksum) != (
                word.id,
                word.content_version,
                word.checksum,
            ):
                raise ValueError("Target policy does not match current vocabulary")
            target = policy.snapshot()
            target.update(
                review_version="two-stage-v2",
                applicable_stages=["HANZI", "PINYIN"],
                disabled_stages=[],
            )
            if policy.gradeable:
                from app.services.review_policy_v2 import project

                target = project(policy)
            plan = await self.planner().plan_for(owner, saved.id)
            if not saved.learning_activated and plan is None:
                raise HTTPException(409, "Saved vocabulary is pending daily planner admission")
            if plan:
                target["plan_id"] = str(plan.id)
            # The existing primary key is the durable idempotency key. A saved-row
            # lock serializes retries; ON CONFLICT also covers another saved identity
            # or owner concurrently using the same UUID without leaking their attempt.
            attempt = await self.session.scalar(
                insert(Attempt)
                .values(
                    id=request_id or uuid4(),
                    user_vocabulary_id=saved.id,
                    mode="DUE" if now >= saved.next_review_at else "PRACTICE",
                    schedule_version=saved.schedule_version,
                    target=target,
                    state_before=state_json(state_of(saved)),
                    started_at=now,
                )
                .on_conflict_do_nothing(index_elements=[Attempt.id])
                .returning(Attempt)
            )
            if attempt is None:
                raise HTTPException(409, "Review request identity conflict")
            return self._initialization_response(attempt)

    @staticmethod
    def _initialization_response(attempt):
        target = attempt.target
        return {
            "attempt_id": attempt.id,
            "saved_id": attempt.user_vocabulary_id,
            "mode": attempt.mode,
            "started_at": attempt.started_at,
            "grading_available": target["gradeable"],
            "applicable_stages": target["applicable_stages"],
            "disabled_stages": dict(target["disabled_stages"]),
            "skipped_stages": [
                {"stage": stage, "status": "NOT_APPLICABLE", "reason": reason}
                for stage, reason in target["disabled_stages"]
            ],
            "reason": None if target["gradeable"] else "REVIEWED_POLICY_REQUIRED",
            "content_version": target["content_version"],
        }

    async def complete_validated(self, owner: UUID, review: ValidatedReview):
        """Internal evaluator integration only. Caller owns no transaction.

        Lock saved row before attempt, serialize different attempts against the same
        schedule generation. A stale due attempt is retained as practice.
        """
        if not isinstance(review, ValidatedReview):
            raise TypeError("Server-validated review required")
        async with self.session.begin():
            return await self._complete_in_transaction(owner, review)

    async def _complete_in_transaction(self, owner, review):
        """Shared atomic boundary for the persisted-answer evaluator."""
        saved = await self.session.scalar(
            select(Saved)
            .join(Attempt)
            .where(Attempt.id == review.attempt_id, Saved.user_id == owner)
            .with_for_update(of=Saved)
        )
        if saved is None:
            raise HTTPException(404, "Review attempt not found")
        attempt = await self.session.scalar(
            select(Attempt).where(Attempt.id == review.attempt_id).with_for_update()
        )
        evidence = {
            "evaluator_version": review.evaluator_version,
            "stages": [asdict(stage) for stage in review.stages],
        }
        if attempt.completed_at is not None:
            if attempt.evidence != evidence:
                raise HTTPException(409, "Attempt already completed")
            return attempt.state_after
        if not attempt.target["gradeable"]:
            raise HTTPException(409, "Server grading unavailable")
        if attempt.target.get("review_version") != "two-stage-v2":
            raise HTTPException(409, "Legacy attempt is read-only; start a new review")
        word = await self.session.scalar(
            select(Word).where(Word.id == saved.vocabulary_id, visible()).with_for_update(read=True)
        )
        if (
            not saved.is_active
            or word is None
            or (
                word.content_version != attempt.target["content_version"]
                or word.checksum != attempt.target["checksum"]
            )
        ):
            raise HTTPException(409, "Review target no longer available")
        now = utc(self.clock())
        if now < attempt.started_at:
            raise ValueError("Completion precedes initialization")
        outcome = review.outcome(tuple(Stage(s) for s in attempt.target["applicable_stages"]))
        eligible = (
            attempt.mode == "DUE"
            and attempt.schedule_version == saved.schedule_version
            and now >= saved.next_review_at
        )
        updated = state_of(saved)
        fsrs_log = None
        if eligible:
            updated = advance_mastery(updated, outcome, now)
            memory = await self.session.get(SrsMemory, saved.id)
            if memory is None:
                config = fsrs_scheduler.configuration()
                history = (
                    await self.session.execute(
                        select(Attempt.outcome, Attempt.completed_at)
                        .where(
                            Attempt.user_vocabulary_id == saved.id,
                            Attempt.scheduling_applied.is_(True),
                            Attempt.completed_at.is_not(None),
                        )
                        .order_by(Attempt.completed_at, Attempt.id)
                    )
                ).all()
                card = fsrs_scheduler.replay(history, config)
                memory = SrsMemory(
                    user_vocabulary_id=saved.id,
                    scheduler_version=fsrs_scheduler.VERSION,
                    configuration=config,
                    card={},
                    adopted_at=now,
                )
                self.session.add(memory)
            else:
                config, card = memory.configuration, memory.card
            memory.card, fsrs_log = fsrs_scheduler.review(card, outcome, now, config)
            updated = replace(updated, next_review_at=datetime.fromisoformat(memory.card["due"]))
            saved.learning_activated = True
        if eligible:
            for name, value in asdict(updated).items():
                setattr(saved, name, value)
            saved.due_review_count += 1
            saved.failure_count += outcome == Outcome.FAIL
            saved.schedule_version += 1
        else:
            saved.practice_count += 1
        attempt.completed_at, attempt.outcome = now, outcome
        attempt.evidence, attempt.state_after = evidence, state_json(updated)
        if fsrs_log is not None:
            attempt.state_after = {
                **attempt.state_after,
                "fsrs": memory.card,
                "fsrs_previous": card,
                "fsrs_review_log": fsrs_log,
                "scheduler_version": memory.scheduler_version,
                "scheduler_configuration": memory.configuration,
            }
        attempt.scheduling_applied = eligible
        await self.planner().completed(attempt)
        await self.session.flush()
        return attempt.state_after
