"""Run from backend: python -m scripts.curated_vocabulary --help."""

import argparse
import asyncio
import json
from pathlib import Path
from uuid import UUID, uuid5

from app.core.database import session_factory
from app.core.event_loop import new_event_loop
from app.services.curated_import import (
    NAMESPACE,
    approve_record,
    import_records,
    load_records,
    record_checksum,
)


async def run(args):
    if args.command in {"validate", "import"}:
        checksum, records = load_records(args.file)
        print(
            json.dumps({"sha256": checksum, "records": len(records), "publication": "unapproved"})
        )
        if args.manifest:
            with args.manifest.open("x", encoding="utf-8") as stream:
                json.dump(
                    [
                        {
                            "id": str(uuid5(NAMESPACE, r.lexical_key)),
                            "lexical_key": r.lexical_key,
                            "content_version": r.content_version,
                            "checksum": record_checksum(r),
                        }
                        for r in records
                    ],
                    stream,
                    indent=2,
                    ensure_ascii=False,
                )
        if args.command == "import":
            async with session_factory() as session:
                print(json.dumps(await import_records(session, args.batch, checksum, records)))
    else:
        async with session_factory() as session:
            await approve_record(session, args.id, args.checksum, args.reviewer)
        print("Human review recorded")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "import"):
        command = commands.add_parser(name)
        command.add_argument("--file", type=Path, required=True)
        command.add_argument("--manifest", type=Path)
        if name == "import":
            command.add_argument("--batch", required=True)
    review = commands.add_parser("approve")
    review.add_argument("--id", type=UUID, required=True)
    review.add_argument("--checksum", required=True)
    review.add_argument("--reviewer", required=True)
    try:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            runner.run(run(parser.parse_args()))
    except Exception:  # noqa: BLE001 -- never print database exception details or secrets
        parser.exit(
            1, "Curated operation failed; inspect input, identity and database configuration.\n"
        )


if __name__ == "__main__":
    main()
