"""Recorded session reviews only: validate, read-only plan, explicitly confirmed local apply."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.services.curated_import import digest, import_records
from app.services.local_codex_review import HEAD, accept_local, load_checkpoint, preview


async def run(args):
    records, evidence, coverage = load_checkpoint(args.checkpoint)
    if args.command == "validate":
        print(json.dumps(coverage, ensure_ascii=False, indent=2))
        return
    value = os.environ.get(args.database_env)
    if not value:
        raise ValueError("Explicit database environment variable required")
    url = make_url(value)
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in {"localhost", "127.0.0.1", "::1"}
        or url.database != "chinese_learning"
    ):
        raise ValueError("This operator command is restricted to local chinese_learning")
    engine = create_async_engine(url, echo=False)
    try:
        if args.command == "plan":
            async with engine.connect() as connection, connection.begin():
                await connection.execute(
                    text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                )
                async with AsyncSession(connection) as session:
                    plan = await preview(session, records, evidence, coverage)
            args.output.write_text(
                json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(
                json.dumps(
                    {
                        "database": plan["database"],
                        "migrations": plan["migrations"],
                        "coverage": {k: v for k, v in coverage.items() if k != "receipts"},
                        "confirmation": plan["confirmation"],
                        "output": str(args.output),
                    },
                    ensure_ascii=False,
                )
            )
            return
        settings = get_settings()
        if (
            not args.enable_local_codex_review
            or settings.environment != "development"
            or not settings.allow_local_codex_reviewed_vocabulary
            or not args.operator.strip()
        ):
            raise ValueError("Explicit flag, development configuration and named operator required")
        async with engine.begin() as connection:
            await connection.execute(select(func.pg_advisory_xact_lock(740001)))
            async with AsyncSession(
                connection, join_transaction_mode="create_savepoint"
            ) as session:
                plan = await preview(session, records, evidence, coverage)
                await session.rollback()
            if plan["confirmation"] != args.confirm or plan["migrations"] != [HEAD]:
                raise ValueError("Stale confirmation or migration 0010 not applied; preview again")
            if any(c["action"].endswith("CONFLICT") for c in plan["changes"]):
                raise ValueError("Resolve content/version conflicts before applying")
            selected_keys = {
                c["lexical_key"]
                for c in plan["changes"]
                if c["action"] not in {"PRESERVE_HOLD", "PRESERVE_APPROVAL"}
            }
            selected = [r for r in records if r.lexical_key in selected_keys]
            if selected:
                payload = ("\n".join(r.model_dump_json() for r in selected) + "\n").encode()
                checksum = digest(payload)
                async with AsyncSession(
                    connection, join_transaction_mode="create_savepoint"
                ) as session:
                    await import_records(
                        session, "local-codex-" + checksum[:40], checksum, selected
                    )
                    await accept_local(session, selected, evidence, args.operator)
        print(
            json.dumps(
                {
                    "accepted_local": len(selected),
                    "production_AI_APPROVED_created": 0,
                    "preserved": len(records) - len(selected),
                }
            )
        )
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "plan", "apply"])
    parser.add_argument(
        "--checkpoint", type=Path, default=Path("../docs/datasets/codex-review-4.0.3")
    )
    parser.add_argument("--database-env", default="LOCAL_VOCABULARY_DATABASE_URL")
    parser.add_argument(
        "--output", type=Path, default=Path("../docs/datasets/codex-review-4.0.3/local-plan.json")
    )
    parser.add_argument("--enable-local-codex-review", action="store_true")
    parser.add_argument("--operator", default="")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    try:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            runner.run(run(args))
    except Exception:  # noqa: BLE001 -- no DB exception, payload or credentials in output
        parser.exit(
            1,
            "Local review operation failed. Check validation, flags, migration, conflicts and confirmation.\n",
        )


if __name__ == "__main__":
    main()
