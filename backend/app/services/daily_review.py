"""Daily workload target, durable selection and bounded active-time accounting."""

import math
import random
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import Integer, func, select

from app.models import User
from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.models.srs_v2 import SrsActiveTime as Timing
from app.models.srs_v2 import SrsDailyPlan as Plan
from app.models.srs_v2 import SrsMemory as Memory
from app.services.curated_catalog import visible
from app.services.fsrs_scheduler import retrievability
from app.services.srs_state import utc

TARGET_SECONDS = 1200
COLD_START_SECONDS = 45
TIMEZONE = "Asia/Ho_Chi_Minh"


def priority(saved, memory, now):
    """Overdue review risk, other due, short-term, pending; stable identity tie-break."""
    if not saved.learning_activated:
        return (3, 0, saved.saved_at, str(saved.id))
    short_term = (
        memory.card["state"] in (1, 3)
        if memory
        else getattr(saved, "phase", "REVIEW") in ("LEARNING", "RELEARNING")
    )
    overdue = saved.next_review_at < now
    group = 2 if short_term else 0 if overdue else 1
    risk = retrievability(memory.card, now, memory.configuration) if memory else 0.0
    return (group, risk, saved.next_review_at, str(saved.id))


def capacity(active_seconds, estimate, beyond=False, limit=50):
    remaining = TARGET_SECONDS - active_seconds
    return min(limit, max(0, math.floor((TARGET_SECONDS if beyond else remaining) / estimate)))


class DailyReview:
    def __init__(self, session, clock, targets):
        self.session, self.clock, self.targets = session, clock, targets

    async def metrics(self, owner):
        now = utc(self.clock())
        local_day = now.astimezone(ZoneInfo(TIMEZONE)).date()
        # Attribute receipt time to its practice date; unfinished attempts count too.
        active_ms = await self.session.scalar(
            select(func.coalesce(func.sum(Timing.daily_ms[str(local_day)].astext.cast(Integer)), 0))
            .join(Plan)
            .where(Plan.user_id == owner)
        )
        samples = list(
            (
                await self.session.scalars(
                    select(Timing.active_ms)
                    .join(Attempt)
                    .join(Plan, Plan.id == Timing.plan_id)
                    .where(
                        Plan.user_id == owner,
                        Attempt.completed_at.is_not(None),
                        Timing.active_ms >= 1000,
                    )
                    .order_by(Attempt.completed_at.desc())
                    .limit(100)
                )
            ).all()
        )
        estimate = (
            min(180, max(10, sum(samples) / len(samples) / 1000))
            if len(samples) >= 5
            else COLD_START_SECONDS
        )
        due = await self.session.scalar(
            select(func.count())
            .select_from(Saved)
            .join(Word)
            .where(
                Saved.user_id == owner,
                Saved.is_active,
                (Saved.next_review_at <= now) | ~Saved.learning_activated,
                visible(),
            )
        )
        pending = await self.session.scalar(
            select(func.count())
            .select_from(Saved)
            .join(Word)
            .where(Saved.user_id == owner, Saved.is_active, ~Saved.learning_activated, visible())
        )
        return {
            "target_seconds": TARGET_SECONDS,
            "active_seconds": active_ms // 1000,
            "estimated_seconds_per_word": estimate,
            "overdue_count": due,
            "estimated_backlog_seconds": math.ceil(due * estimate),
            "pending_count": pending,
            "local_day": local_day,
            "timezone": TIMEZONE,
        }

    async def create(self, owner, request_id, beyond=False, limit=50):
        async with self.session.begin():
            # Serialize plan reservations across devices; no saved schedule writes.
            await self.session.scalar(select(User).where(User.id == owner).with_for_update())
            existing = await self.session.get(Plan, request_id)
            if existing:
                if existing.user_id != owner:
                    raise HTTPException(409, "Plan identity conflict")
                return await self.view(existing)
            plans = list(
                await self.session.scalars(
                    select(Plan).where(Plan.user_id == owner).order_by(Plan.created_at, Plan.id)
                )
            )
            for plan in plans:
                if set(plan.items) - set(plan.completed) - set(plan.deferred):
                    return await self.view(plan)
            metrics = await self.metrics(owner)
            count = capacity(
                metrics["active_seconds"], metrics["estimated_seconds_per_word"], beyond, limit
            )
            now = utc(self.clock())
            rows = list(
                (
                    await self.session.execute(
                        select(Saved, Word, Memory)
                        .join(Word)
                        .outerjoin(Memory, Memory.user_vocabulary_id == Saved.id)
                        .where(
                            Saved.user_id == owner,
                            Saved.is_active,
                            visible(),
                            (Saved.next_review_at <= now) | ~Saved.learning_activated,
                        )
                    )
                ).all()
            )
            rows.sort(key=lambda row: priority(row[0], row[2], now))
            items, new_items = [], []
            self.session.info["review_policy_batch"] = (
                self.session.sync_session.get_transaction(),
                {w.id for _, w, _ in rows},
            )
            for saved, word, memory in rows:
                if len(items) >= count:
                    break
                if (await self.targets.resolve(self.session, word)).gradeable:
                    items.append(str(saved.id))
                    if not saved.learning_activated:
                        new_items.append(str(saved.id))
            random.SystemRandom().shuffle(items)
            plan = Plan(
                id=request_id,
                user_id=owner,
                local_day=metrics["local_day"],
                timezone=TIMEZONE,
                target_seconds=TARGET_SECONDS,
                items=items,
                new_items=new_items,
                completed=[],
                created_at=now,
            )
            self.session.add(plan)
            await self.session.flush()
            return await self.view(plan)

    async def view(self, plan):
        return {
            "plan_id": plan.id,
            "items": [
                {"saved_id": item, "due": True}
                for item in plan.items
                if item not in plan.completed and item not in plan.deferred
            ],
            "excluded": [],
            **await self.metrics(plan.user_id),
        }

    async def plan_for(self, owner, saved_id):
        plans = await self.session.scalars(
            select(Plan).where(Plan.user_id == owner).order_by(Plan.created_at.desc(), Plan.id)
        )
        return next(
            (
                p
                for p in plans
                if str(saved_id) in p.items
                and str(saved_id) not in p.completed
                and str(saved_id) not in p.deferred
            ),
            None,
        )

    async def receipt(self, owner, attempt, active_ms):
        """Caller holds saved/attempt locks. Absolute monotonic totals make retries safe."""
        plan_id = attempt.target.get("plan_id")
        if not plan_id:
            raise HTTPException(409, "Timed review requires a daily plan")
        now = utc(self.clock())
        timing = await self.session.get(Timing, attempt.id)
        if attempt.completed_at is not None:
            return {"active_ms": timing.active_ms if timing else 0}
        if timing is None:
            timing = Timing(
                attempt_id=attempt.id,
                plan_id=UUID(plan_id),
                active_ms=0,
                daily_ms={},
                received_at=now,
            )
            self.session.add(timing)
            # First heartbeat bounded by elapsed attempt age, at most 15 seconds.
            elapsed = (now - utc(attempt.started_at)).total_seconds()
        else:
            elapsed = (now - utc(timing.received_at)).total_seconds()
        if active_ms <= timing.active_ms:
            return {"active_ms": timing.active_ms}
        allowed = max(0, min(15000, int(elapsed * 1000)))
        if (
            active_ms - timing.active_ms > allowed + 1000
            or active_ms > int((now - utc(attempt.started_at)).total_seconds() * 1000) + 1000
        ):
            raise HTTPException(422, "Active time exceeds foreground receipt window")
        day = str(now.astimezone(ZoneInfo(TIMEZONE)).date())
        timing.daily_ms = {
            **timing.daily_ms,
            day: timing.daily_ms.get(day, 0) + active_ms - timing.active_ms,
        }
        timing.active_ms = active_ms
        timing.received_at = now
        await self.session.flush()
        return {"active_ms": timing.active_ms}

    async def completed(self, attempt):
        if not attempt.target.get("plan_id"):
            return
        plan = await self.session.scalar(
            select(Plan).where(Plan.id == UUID(attempt.target["plan_id"])).with_for_update()
        )
        word = str(attempt.user_vocabulary_id)
        if word not in plan.completed:
            plan.completed = [*plan.completed, word]

    async def defer(self, attempt):
        if not attempt.target.get("plan_id"):
            return
        plan = await self.session.scalar(
            select(Plan).where(Plan.id == UUID(attempt.target["plan_id"])).with_for_update()
        )
        item = str(attempt.user_vocabulary_id)
        if item not in plan.deferred and item not in plan.completed:
            plan.deferred = [*plan.deferred, item]
