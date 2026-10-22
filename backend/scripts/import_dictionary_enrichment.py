"""Import a checksum-verified hsk-sino-viet characters.json artifact, without lexical joins."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.core.event_loop import new_event_loop
from app.services.cedict import DictionaryImportError
from app.services.dictionary_enrichment import LICENSE, load_character_dataset
from app.services.dictionary_revision import validate_revision


async def execute(dataset, revision):
    from app.core.database import engine, session_factory
    from app.services.dictionary_enrichment import import_character_enrichment

    try:
        async with session_factory() as session:
            return await import_character_enrichment(session, dataset, revision)
    finally:
        await engine.dispose()


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--revision", help="Pinned source commit or a local artifact revision")
    parser.add_argument("--acknowledge-license", choices=[LICENSE], required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        revision = validate_revision(args.revision or "artifact-sha256-" + args.sha256.lower())
        dataset = load_character_dataset(args.file, args.sha256.lower())
        if args.validate_only:
            summary = {"records": len(dataset.records)}
        else:
            with asyncio.Runner(loop_factory=new_event_loop) as runner:
                summary = runner.run(execute(dataset, revision))
        print(
            json.dumps(
                {
                    **summary,
                    "revision": revision,
                    "sha256": dataset.sha256,
                    "scope": "character",
                    "lexical_translations_added": 0,
                }
            )
        )
    except DictionaryImportError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError):
        print("Cannot read enrichment artifact; no changes committed.", file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print("Enrichment import failed; no changes committed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
