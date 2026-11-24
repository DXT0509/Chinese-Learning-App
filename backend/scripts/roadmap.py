"""Explicit local operator workflow; no development writes without invoking a write command."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.core.database import session_factory
from app.schemas.roadmap import RoadmapDefinition
from app.services.content_files import ContentError, unique_json_object
from app.services.content_storage import LocalContentStorage
from app.services.roadmap_authoring import activate, compile_preview, import_draft, publish


def preparation_run(args):
    """Offline commands deliberately never instantiate a session or configured storage."""
    from app.schemas.roadmap_preparation import PreparationPlan
    from app.services.roadmap_preparation import (
        generate,
        load_catalog,
        load_json,
        validate_generated,
        write_artifact,
    )

    plan = PreparationPlan.model_validate(load_json(args.plan))
    catalog = load_catalog(args.catalog)
    if args.command in {"generate-drafts", "build-reviews", "preview-for-review"}:
        _, report = generate(
            plan,
            catalog,
            args.asset_root,
            args.output,
            operator_preview=args.command == "preview-for-review",
        )
    else:
        definition, report = validate_generated(plan, catalog, args.asset_root, args.output)
        if args.command == "preview-file":
            payload = definition.model_dump(mode="json")
            for node in payload["nodes"]:
                for activity in node["lesson"]["activities"]:
                    activity.pop("correct_option", None)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif args.command == "missing-assets":
            print(
                json.dumps(
                    [i for i in report.issues if i["severity"] == "OPTIONAL_MISSING"],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "prepare-bundle" and report.payload()["draft_valid"]:
            # Private operator artifact, never a learner response or publication attestation.
            write_artifact(
                Path(args.output) / "publication-candidate.json",
                {
                    "purpose": "ROADMAP_DRAFT_CANDIDATE",
                    "status": "DRAFT",
                    "publication_ready": False,
                    "definition": definition.model_dump(mode="json"),
                    "manifest": load_json(Path(args.output) / "manifest.json"),
                    "assets": load_json(Path(args.output) / "assets.json"),
                    "quality": report.payload(),
                },
                immutable=True,
            )
        elif args.command == "stage-assets" and report.payload()["draft_valid"]:
            from app.services.content_storage import verify_object

            source = LocalContentStorage(Path(args.output) / "objects")
            target = LocalContentStorage(args.storage_dir or get_settings().content_storage_dir)
            assets = load_json(Path(args.output) / "assets.json")
            verified = [
                (a, verify_object(source, a["storage_key"], a["sha256"], a["byte_length"]))
                for a in assets
            ]
            if args.apply:
                for asset, raw in verified:
                    if target.put_bundle(raw) != asset["storage_key"]:
                        raise ContentError("staged object identity differs")
                print(f"Staged {len(verified)} verified objects; no database writes")
            else:
                print(f"Dry run: {len(verified)} verified objects; target {target.root}; no writes")
        write_artifact(Path(args.output) / "quality.json", report.payload())
        write_artifact(Path(args.output) / "quality.md", report.markdown())
    if args.command not in {"preview-file", "missing-assets"}:
        print(report.markdown())
    elif not report.payload()["draft_valid"]:
        print(report.markdown(), file=sys.stderr)
    return 0 if report.payload()["draft_valid"] else 1


async def run(args):
    storage = LocalContentStorage(get_settings().content_storage_dir)
    async with session_factory() as session:
        if args.command in ("validate", "import"):
            path = Path(args.file)
            if path.stat().st_size > 20_000_000:
                raise ContentError("roadmap authoring file exceeds 20 MB")
            definition = RoadmapDefinition.model_validate(
                json.loads(
                    path.read_text("utf-8"),
                    object_pairs_hook=unique_json_object,
                    parse_constant=lambda _: (_ for _ in ()).throw(
                        ContentError("non-finite JSON number")
                    ),
                )
            )
            if args.command == "import":
                from app.services.roadmap_preparation import load_json

                manifest_path = path.parent / "manifest.json"
                if (
                    manifest_path.exists()
                    and load_json(manifest_path).get("purpose") == "OPERATOR_REVIEW_ONLY"
                ):
                    raise ContentError(
                        "operator review previews cannot be imported; obtain real review and regenerate"
                    )
                print(await import_draft(session, definition))
            else:
                print(
                    "Valid draft; catalog/assets and operator review checked at preview/publication"
                )
        elif args.command == "preview":
            async with session.begin():
                definition, _ = await compile_preview(session, UUID(args.version_id), storage)
                print(json.dumps(definition.model_dump(mode="json"), ensure_ascii=False, indent=2))
        elif args.command == "publish":
            await publish(session, UUID(args.version_id), storage, args.reviewed_by)
            print("Published and activated reviewed roadmap")
        elif args.command == "activate":
            await activate(session, UUID(args.roadmap_id), UUID(args.version_id))
        else:
            await activate(session, UUID(args.roadmap_id), None)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    offline = {
        "generate-drafts": "Generate/resume immutable filesystem lesson drafts and reports",
        "preview-for-review": "Private preview including pending content; errors block publication",
        "build-reviews": "Generate drafts with exact preceding REVIEW groups (no DB writes)",
        "check-content": "Validate inputs, assets, generated contracts and version integrity",
        "missing-assets": "Print machine-readable missing enrichment inventory",
        "preview-file": "Preview filesystem lessons with server answer keys removed",
        "quality-report": "Refresh human/machine content quality reports",
        "prepare-bundle": "Prepare a private DRAFT candidate; never publishes or activates",
        "stage-assets": "Verify CAS staging; --apply copies immutable bytes without DB writes",
    }
    for name, help_text in offline.items():
        command = commands.add_parser(name, help=help_text, description=help_text)
        command.add_argument("--plan", required=True, type=Path)
        command.add_argument(
            "--catalog",
            required=True,
            type=Path,
            nargs="+",
            help="Existing converted CuratedRecord JSONL files; never rewritten",
        )
        command.add_argument("--asset-root", type=Path, default=Path("."))
        command.add_argument(
            "--output",
            required=True,
            type=Path,
            help="Version-specific filesystem artifact directory",
        )
        if name == "stage-assets":
            command.add_argument(
                "--storage-dir",
                type=Path,
                help="Defaults to the API's configured content storage directory",
            )
            command.add_argument(
                "--apply", action="store_true", help="Explicitly copy verified objects"
            )
    for name in ("validate", "import"):
        commands.add_parser(name).add_argument("file")
    for name in ("preview", "publish"):
        command = commands.add_parser(name)
        command.add_argument("version_id")
        if name == "publish":
            command.add_argument(
                "--reviewed-by",
                required=True,
                help="Operator attestation, never external AI approval",
            )
    command = commands.add_parser("activate")
    command.add_argument("roadmap_id")
    command.add_argument("version_id")
    commands.add_parser("depublish").add_argument("roadmap_id")
    args = parser.parse_args()
    try:
        if args.command in offline:
            raise SystemExit(preparation_run(args))
        asyncio.run(run(args))
    except (ContentError, ValueError, OSError) as error:
        parser.exit(2, f"roadmap: {error}\n")


if __name__ == "__main__":
    main()
