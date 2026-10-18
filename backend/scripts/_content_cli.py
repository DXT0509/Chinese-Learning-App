import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.core.event_loop import new_event_loop
from app.schemas.content import content_id
from app.services.content_files import ContentError, load_library
from app.services.content_storage import LocalContentStorage


def run(command: str):
    # Redirected Python streams use a legacy code page on some Windows installations.
    # Authoring and inspected bundles always use UTF-8, including when piped to a file.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=f"{command} local Slice 1 content")
    parser.add_argument("--storage-dir", type=Path, default=Path(".content-storage"))
    if command in ("validate", "import"):
        parser.add_argument("--content-dir", type=Path, default=Path("content"))
    else:
        parser.add_argument("--lesson", required=True)
        parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()
    try:
        library = load_library(args.content_dir) if command in ("validate", "import") else None
        if command == "validate":
            from app.services.content_storage import verify_object

            for asset in library.assets:
                verify_object(
                    LocalContentStorage(args.storage_dir),
                    asset.storage_key,
                    asset.sha256,
                    asset.byte_length,
                )
            print(
                f"Valid: {len(library.vocabulary)} vocabulary, {len(library.templates)} template "
                f"versions, {len(library.lessons)} lesson versions. CONTENT_PREVIEW only."
            )
        else:
            with asyncio.Runner(loop_factory=new_event_loop) as runner:
                runner.run(_database_command(command, args, library))
    except ContentError as error:
        print(f"Content error: {error}", file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print(
            "Database operation failed. Check DATABASE_URL, migrations, ID conflicts and "
            "publication constraints; no changes were committed.",
            file=sys.stderr,
        )
        return 1
    except OSError:
        print(
            "Local storage operation failed; check the storage directory and permissions.",
            file=sys.stderr,
        )
        return 1
    return 0


async def _database_command(command, args, library):
    from app.core.database import engine, session_factory
    from app.services.content_authoring import import_library
    from app.services.lesson_publication import inspect_bundle, publish_lesson

    storage = LocalContentStorage(args.storage_dir)
    try:
        async with session_factory() as session:
            if command == "import":
                await import_library(session, library, storage)
                print(
                    "Import complete. New versions are DRAFT; identical definitions were retained."
                )
            elif command == "publish":
                key = await publish_lesson(
                    session, content_id("lesson", args.lesson), args.version, storage
                )
                print(f"Published CONTENT_PREVIEW: {key}")
            else:
                data = await inspect_bundle(
                    session, content_id("lesson", args.lesson), args.version, storage
                )
                print(json.dumps(json.loads(data), ensure_ascii=False, indent=2))
    finally:
        await engine.dispose()
