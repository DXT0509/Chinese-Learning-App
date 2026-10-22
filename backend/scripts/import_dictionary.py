"""Import a manually acquired, license-checked CC-CEDICT v1 artifact."""

import argparse
import asyncio
import json
import sys
import zlib
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.core.event_loop import new_event_loop
from app.services.cedict import LICENSE, DictionaryImportError, load_dataset
from app.services.dictionary_revision import artifact_revision, validate_revision


async def execute(dataset, revision):
    from app.core.database import engine, session_factory
    from app.services.dictionary_import import import_dictionary

    try:
        async with session_factory() as session:
            return await import_dictionary(session, dataset, revision)
    finally:
        await engine.dispose()


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument(
        "--revision", help="Optional explicit label; otherwise verified header/hash"
    )
    parser.add_argument(
        "--sha256", required=True, help="SHA-256 of the exact local txt/gz artifact"
    )
    parser.add_argument("--acknowledge-license", choices=[LICENSE], required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.revision:
            validate_revision(args.revision)
        evidence = artifact_revision(args.file, args.sha256.lower())
        revision = args.revision or evidence["revision"]
        dataset = load_dataset(args.file, args.sha256.lower())
        if args.validate_only:
            summary = {"entries": len(dataset.entries), "duplicate_rows": dataset.duplicate_rows}
        else:
            with asyncio.Runner(loop_factory=new_event_loop) as runner:
                summary = runner.run(execute(dataset, revision))
        summary["revision"] = revision
        summary["revision_evidence"] = evidence
        print(json.dumps(summary))
    except DictionaryImportError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, EOFError, zlib.error):
        print("Cannot read UTF-8 dictionary artifact; no changes committed.", file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print("Dictionary database operation failed; no changes committed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
