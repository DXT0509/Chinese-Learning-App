"""Dry-run by default. --confirm changes only the verified revision and audit metadata."""

import argparse
import asyncio
import json
import sys
import zlib
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.core.event_loop import new_event_loop
from app.services.cedict import DictionaryImportError


async def execute(args):
    from app.core.database import engine, session_factory
    from app.services.dictionary_maintenance import correct_revision

    try:
        async with session_factory() as session:
            summary = await correct_revision(
                session, args.file, args.sha256.lower(), args.from_revision
            )
            print(json.dumps({**summary, "mode": "dry-run"}))
            if args.confirm:
                summary = await correct_revision(
                    session,
                    args.file,
                    args.sha256.lower(),
                    args.from_revision,
                    confirm=True,
                )
                print(json.dumps({**summary, "mode": "confirmed"}))
    finally:
        await engine.dispose()


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument(
        "--sha256", required=True, help="Expected checksum from the existing import"
    )
    parser.add_argument("--from-revision", default="your-actual-source-release")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    if args.confirm:
        parser.error("Provider retired in Phase 4; legacy revision repair is read-only")
    try:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            runner.run(execute(args))
    except DictionaryImportError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, EOFError, zlib.error):
        print("Cannot read verified dictionary artifact; no changes committed.", file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print("Revision correction failed; no changes committed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
