"""Read-only 0012-compatible preflight and synthetic workload simulation. No write mode."""

import argparse
import asyncio
import hashlib
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.services.fsrs_scheduler import configuration, replay, retrievability, review
from app.services.srs_state import Outcome


async def policy_bundle():
    from app.models.curated_vocabulary import CuratedVocabulary as Word
    from app.models.srs import SrsTargetPolicy
    from app.services.review_policy_v2 import TwoStagePolicy, project
    from app.services.review_targets import ReviewedTargets

    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            async with AsyncSession(connection) as session:
                words = list(
                    await session.scalars(
                        select(Word)
                        .join(
                            SrsTargetPolicy,
                            (SrsTargetPolicy.vocabulary_id == Word.id)
                            & (SrsTargetPolicy.content_version == Word.content_version)
                            & (SrsTargetPolicy.checksum == Word.checksum),
                        )
                        .order_by(Word.id)
                    )
                )
                session.info["review_policy_batch"] = (
                    session.sync_session.get_transaction(),
                    {w.id for w in words},
                )
                result, unavailable = [], 0
                for word in words:
                    target = await ReviewedTargets().resolve(session, word)
                    if target.gradeable:
                        snapshot = project(target)
                        result.append(
                            TwoStagePolicy.model_validate(
                                {k: snapshot[k] for k in TwoStagePolicy.model_fields}
                            ).model_dump(mode="json")
                        )
                    else:
                        unavailable += 1
                return {
                    "format_version": 2,
                    "database_writes": 0,
                    "validated_source_policies": len(result),
                    "unavailable": unavailable,
                    "policies": result,
                }
    finally:
        await engine.dispose()


async def preflight():
    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            await connection.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            counts, hashes = {}, {}
            for table in (
                "users",
                "curated_user_vocabulary",
                "personal_vocabulary_entries",
                "srs_review_attempts",
                "srs_target_policies",
                "curated_vocabulary_reviews",
            ):
                rows = list(await connection.scalars(text(f"SELECT to_jsonb(t) FROM {table} t")))
                counts[table] = len(rows)
                hashes[table] = hashlib.sha256(
                    "\n".join(sorted(json.dumps(r, sort_keys=True) for r in rows)).encode()
                ).hexdigest()
            saved = list(
                (
                    await connection.execute(
                        text(
                            "SELECT id, next_review_at, mastery_level, last_reviewed_at FROM curated_user_vocabulary"
                        )
                    )
                ).mappings()
            )
            history = list(
                (
                    await connection.execute(
                        text(
                            "SELECT user_vocabulary_id, outcome, completed_at FROM srs_review_attempts WHERE scheduling_applied IS TRUE ORDER BY completed_at, id"
                        )
                    )
                ).mappings()
            )
            now, config = datetime.now(UTC), configuration()
            projections = []
            for row in saved:
                recorded = [
                    (h["outcome"], h["completed_at"])
                    for h in history
                    if h["user_vocabulary_id"] == row["id"]
                ]
                card = replay(recorded, config)
                completion = max(now, row["next_review_at"])
                good, _ = review(card, Outcome.PASS, completion, config)
                again, _ = review(card, Outcome.FAIL, completion, config)
                projections.append(
                    {
                        "identity_sha256": hashlib.sha256(str(row["id"]).encode()).hexdigest(),
                        "mastery_preserved": row["mastery_level"],
                        "current_due_unchanged": row["next_review_at"].isoformat(),
                        "recorded_scheduling_outcomes": len(recorded),
                        "memory_initialization": "recorded replay"
                        if recorded
                        else "cold start (no invented history)",
                        "hypothetical_next_eligible_completion": completion.isoformat(),
                        "hypothetical_good_due": good["due"],
                        "hypothetical_again_due": again["due"],
                    }
                )
            return {
                "captured_at": now.isoformat(),
                "transaction_read_only": await connection.scalar(
                    text("SHOW transaction_read_only")
                ),
                "revision": await connection.scalar(
                    text("SELECT version_num FROM alembic_version")
                ),
                "database_writes": 0,
                "counts": counts,
                "preservation_sha256": hashes,
                "expected_migration_writes": {
                    "new_tables": 3,
                    "new_columns": 1,
                    "existing_rows_receiving_activation_default": counts["curated_user_vocabulary"],
                    "schedule_updates": 0,
                    "mastery_updates": 0,
                    "policy_inserts": 0,
                    "history_updates": 0,
                    "alembic_version_updates": 1,
                },
                "projections": projections,
            }
    finally:
        await engine.dispose()


def simulate(size, algorithm, budgeted, days=365):
    """Synthetic mature cohort, staggered existing due dates, binary 90% success.

    One opportunity/word/day, fixed 45s, no arrivals, no parameter optimization.
    This deliberately reports backlog when 20 minutes cannot cover the population.
    """
    rng, config = random.Random(5000 + size), configuration()
    start = datetime(2030, 1, 1, tzinfo=UTC)
    cards, dues = [], []
    for i in range(size):
        history = [("PASS", start - timedelta(days=d)) for d in (90, 60, 30)]
        cards.append(replay(history, config))
        dues.append(start + timedelta(days=i % 21))
    daily, backlogs = [], []
    for day in range(days):
        now = start + timedelta(days=day)
        due = [i for i in range(size) if dues[i] <= now]
        due.sort(key=lambda i: (retrievability(cards[i], now, config), dues[i], i))
        selected = due[:26] if budgeted else due
        for i in selected:
            outcome = Outcome.PASS if rng.random() < 0.9 else Outcome.FAIL
            cards[i], _ = review(cards[i], outcome, now, config)
            dues[i] = datetime.fromisoformat(cards[i]["due"])
        daily.append(len(selected) * 45 / 60)
        backlogs.append(len(due) - len(selected))
    return {
        "catalog_size": size,
        "scheduler": algorithm,
        "budgeted": budgeted,
        "days": days,
        "mean_daily_minutes": round(sum(daily) / days, 2),
        "last_90_days_mean_minutes": round(sum(daily[-90:]) / 90, 2),
        "max_daily_minutes": max(daily),
        "final_deferred_words": backlogs[-1],
        "max_deferred_words": max(backlogs),
        "days_above_20_minutes": sum(m > 20 for m in daily),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--simulate", type=Path)
    parser.add_argument("--policies", type=Path)
    args = parser.parse_args()
    if args.policies:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            result = runner.run(policy_bundle())
        args.policies.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            f"Read-only policy bundle: {result['validated_source_policies']} valid; {result['unavailable']} unavailable; no installation"
        )
    if args.preflight:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            result = runner.run(preflight())
        args.preflight.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print("Read-only preflight written; zero database writes")
    if args.simulate:
        results = [
            simulate(size, algorithm, budgeted)
            for size in (500, 2000, 5000)
            for algorithm, budgeted in (("FSRS", True), ("FSRS", False))
        ]
        args.simulate.write_text(
            json.dumps(
                {
                    "data": "SYNTHETIC; not measured learner outcomes",
                    "assumptions": "365 days; existing cohort; 3 synthetic prior Good reviews; due dates staggered over 21 days; 90% binary success; 45 seconds per review; one opportunity per word per day; no new words; seed 5000+size",
                    "results": results,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("Synthetic simulations written")


if __name__ == "__main__":
    main()
