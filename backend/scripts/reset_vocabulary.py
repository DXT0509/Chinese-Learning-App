"""Two-step local reset. Dry-run creates a full backup; apply requires its exact token."""

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.services.vocabulary_reset import execute_reset, local_identity, prepare


async def run(args):
    settings = get_settings()
    identity = local_identity(settings, args.database, args.host, args.port)
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.begin() as connection:
            if args.command == "dry-run":
                report = await prepare(
                    connection, settings, identity, args.backup_dir, args.pg_dump
                )
                # Never overwrite an existing report/approval artifact.
                with args.report.open("x", encoding="utf-8") as stream:
                    json.dump(report, stream, indent=2, ensure_ascii=False)
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                report = json.loads(args.report.read_text(encoding="utf-8"))
                print(
                    json.dumps(
                        await execute_reset(connection, report, args.confirm, identity), indent=2
                    )
                )
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["dry-run", "apply"])
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--backup-dir", type=Path, default=Path(".vocabulary-backups"))
    parser.add_argument("--pg-dump", default="pg_dump")
    parser.add_argument("--confirm")
    args = parser.parse_args()
    if args.command == "apply" and not args.confirm:
        parser.error("apply requires --confirm from a reviewed dry-run report")
    try:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            runner.run(run(args))
    except (ValueError, FileExistsError) as error:
        parser.exit(1, str(error) + "\n")
    except Exception:  # noqa: BLE001 -- never print database exception details or secrets
        parser.exit(
            1,
            "Reset stopped; verify PostgreSQL tools, permissions, schema and identity. No reset was committed.\n",
        )


if __name__ == "__main__":
    main()
