"""Authorized local-only FSRS deployment: minimal backup, upgrade and preservation checks."""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.models import User
from app.services.review_engine import ReviewEngine
from scripts.srs_v2_backup_rehearsal import fingerprints
from scripts.srs_v2_preview import policy_bundle


def pg_environment(source):
    return {
        **os.environ,
        "PGHOST": source.host,
        "PGPORT": str(source.port or 5432),
        "PGUSER": source.username,
        "PGPASSWORD": source.password,
    }


def preservation(connection):
    """Compare original columns, including complete attempts and installed policies."""
    tables = connection.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name"
    ).fetchall()
    result = {}
    for (name,) in tables:
        if name in ("alembic_version", "srs_memory", "srs_daily_plans", "srs_active_time"):
            continue
        from psycopg import sql

        expression = (
            sql.SQL("to_jsonb(t) - 'learning_activated'")
            if name == "curated_user_vocabulary"
            else sql.SQL("to_jsonb(t)")
        )
        rows = connection.execute(
            sql.SQL("SELECT {} FROM {} t").format(expression, sql.Identifier(name))
        ).fetchall()
        result[name] = {
            "rows": len(rows),
            "sha256": hashlib.sha256(
                "\n".join(sorted(json.dumps(r[0], sort_keys=True) for r in rows)).encode()
            ).hexdigest(),
        }
    return result


async def read_checks():
    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            async with AsyncSession(connection) as session:
                owners = list(await session.scalars(select(User.id).order_by(User.id)))
                dashboards = []
                for owner in owners:
                    dashboard = await ReviewEngine(session).dashboard(owner)
                    budget = dashboard["daily_review"]
                    assert budget["target_seconds"] == 1200
                    dashboards.append(
                        {
                            "owner_sha256": hashlib.sha256(str(owner).encode()).hexdigest(),
                            "available_count": dashboard["available_count"],
                            "due_count": dashboard["due_count"],
                            "grading_available": dashboard["grading_available"],
                            **budget,
                        }
                    )
                return dashboards
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    args = parser.parse_args()
    settings, stamp = get_settings(), datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    source = make_url(settings.database_url)
    if (
        settings.environment != "development"
        or source.host not in ("127.0.0.1", "localhost")
        or source.database != args.database
    ):
        raise RuntimeError(
            "Refusing deployment outside the explicitly named local development database"
        )
    private = Path(".vocabulary-backups") / f"fsrs-only-{stamp}"
    private.mkdir(parents=True, exist_ok=False)
    backup = private / "before-migration.dump"
    pg_bin = Path(os.environ.get("PG_BIN", "C:/Program Files/PostgreSQL/18/bin"))
    pg_env = pg_environment(source)
    connection_args = {
        "host": source.host,
        "port": source.port or 5432,
        "user": source.username,
        "password": source.password,
        "dbname": source.database,
    }
    with psycopg.connect(**connection_args) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        if revision not in ("0012_srs_review_engine", "0013_srs_v2"):
            raise RuntimeError("Expected reviewed 0012/0013 baseline; inspect before deployment")
        snapshot = connection.execute("SELECT pg_export_snapshot()").fetchone()[0]
        before = preservation(connection)
        full_before = fingerprints(connection)
        result = subprocess.run(
            [
                str(pg_bin / "pg_dump.exe"),
                "--format=custom",
                "--snapshot",
                snapshot,
                "--file",
                str(backup),
                source.database,
            ],
            env=pg_env,
            capture_output=True,
            check=False,
        )
        if result.returncode or not backup.is_file() or backup.stat().st_size == 0:
            raise RuntimeError("Minimal backup failed; migration was not started")
    listing = subprocess.run(
        [str(pg_bin / "pg_restore.exe"), "--list", str(backup)], capture_output=True, check=False
    )
    if listing.returncode:
        raise RuntimeError("Backup archive listing failed; migration was not started")
    (private / "before.json").write_text(json.dumps(full_before, indent=2), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "0014_fsrs_only"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Migration failed; keep backend stopped and retain minimal backup for inspection"
        )
    check = subprocess.run(
        [sys.executable, "-m", "alembic", "check"], capture_output=True, check=False
    )
    if check.returncode:
        raise RuntimeError("Schema consistency check failed; keep backend stopped")
    with psycopg.connect(**connection_args) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        after = preservation(connection)
        if before != after:
            raise RuntimeError("Preservation mismatch; keep backend stopped and inspect")
        counts = {name: value["rows"] for name, value in after.items()}
        memory_count, due_mismatches, unreviewed_with_history = connection.execute("""
            SELECT count(*), count(*) FILTER (WHERE (m.card->>'due')::timestamptz <> s.next_review_at),
              count(*) FILTER (WHERE m.card->>'last_review' IS NOT NULL AND NOT EXISTS
                (SELECT 1 FROM srs_review_attempts a WHERE a.user_vocabulary_id=s.id
                 AND a.scheduling_applied IS TRUE AND a.completed_at IS NOT NULL))
            FROM srs_memory m JOIN curated_user_vocabulary s ON s.id=m.user_vocabulary_id
        """).fetchone()
        assert (
            memory_count == counts["curated_user_vocabulary"]
            and due_mismatches == unreviewed_with_history == 0
        )
        adopted_history_count = connection.execute(
            "SELECT count(*) FROM srs_memory WHERE card->>'last_review' IS NOT NULL"
        ).fetchone()[0]
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        policies = runner.run(policy_bundle())
        dashboards = runner.run(read_checks())
    assert (
        policies["validated_source_policies"] == counts["srs_target_policies"] == 2804
        and policies["unavailable"] == 0
    )
    report = {
        "deployed_at": datetime.now(UTC).isoformat(),
        "environment": "local development",
        "database": source.database,
        "previous_revision": revision,
        "revision": "0014_fsrs_only",
        "scheduler": "fsrs-6.3.2/binary-v2",
        "backup": {
            "path": str(backup),
            "bytes": backup.stat().st_size,
            "sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
            "archive_listing_verified": True,
            "restore_rehearsal_performed": False,
        },
        "all_original_rows_and_columns_preserved": True,
        "preserved_tables": after,
        "counts": counts,
        "memory_rows": memory_count,
        "memory_rows_with_recorded_history": adopted_history_count,
        "schedule_updates": 0,
        "mastery_updates": 0,
        "historical_attempt_updates": 0,
        "installed_policy_updates": 0,
        "two_stage_policies_valid": policies["validated_source_policies"],
        "dashboards": dashboards,
        "alembic_check_passed": True,
    }
    Path("../docs/srs-fsrs-only-deployment.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    print(
        f"Migrated local development {revision} -> 0014; original rows preserved; {memory_count} FSRS cards; 2804 valid two-stage projections"
    )


if __name__ == "__main__":
    main()
