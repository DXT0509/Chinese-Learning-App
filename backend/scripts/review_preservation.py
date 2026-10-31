"""Read-only fingerprints of all pre-0012 rows; outputs no row contents or credentials."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from sqlalchemy import text

from app.core.database import engine
from app.core.event_loop import new_event_loop


async def inventory(connection):
    tables = list(
        await connection.scalars(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_type='BASE TABLE' "
                "AND table_name NOT IN ('alembic_version','srs_target_policies') ORDER BY table_name"
            )
        )
    )
    result = {}
    for name in tables:
        quoted = connection.dialect.identifier_preparer.quote(name)
        # Only the newly introduced journal is omitted from old-row comparison.
        expression = (
            "to_jsonb(t) - 'submissions'" if name == "srs_review_attempts" else "to_jsonb(t)"
        )
        rows = list(await connection.scalars(text(f"SELECT {expression} FROM public.{quoted} t")))
        canonical = sorted(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)
        digest = hashlib.sha256("\n".join(canonical).encode()).hexdigest()
        result[name] = {"rows": len(rows), "sha256": digest}
    return result


async def run(args):
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            await connection.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            revision = await connection.scalar(text("SELECT version_num FROM alembic_version"))
            database = await connection.scalar(text("SELECT current_database()"))
            tables = await inventory(connection)
            if args.snapshot:
                if revision != "0011_srs_foundation":
                    raise ValueError("Snapshot requires revision 0011")
                await asyncio.to_thread(
                    save_snapshot, args.snapshot, {"database": database, "tables": tables}
                )
                print("0011 preservation fingerprint recorded")
            else:
                baseline = json.loads(
                    await asyncio.to_thread(Path(args.verify).read_text, encoding="utf-8")
                )
                if revision != "0012_srs_review_engine":
                    raise ValueError("Verification requires revision 0012")
                if baseline != {"database": database, "tables": tables}:
                    raise ValueError("Preservation mismatch; keep API stopped and inspect")
                print("All preexisting table row counts and fingerprints match")
    finally:
        await engine.dispose()


def save_snapshot(path, snapshot):
    with Path(path).open("x", encoding="utf-8") as output:
        json.dump(snapshot, output, indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot")
    mode.add_argument("--verify")
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(run(args))


if __name__ == "__main__":
    main()
