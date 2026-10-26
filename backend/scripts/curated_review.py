"""Offline exchange CLI. Never calls a paid API or synthesizes semantic evidence."""

import argparse
import asyncio
import json
from pathlib import Path

from app.core.database import session_factory
from app.core.event_loop import new_event_loop
from app.schemas.curated_review import ModelIdentity, ReviewInput, ReviewResult
from app.services.curated_batch001 import convert_batch001
from app.services.curated_import import load_records
from app.services.curated_review import coverage, import_reviews, load_exchange, review_inputs


def write_jsonl(path, rows):
    with path.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(row.model_dump_json() + "\n")


async def run(args):
    if args.command == "convert-batch001":
        rows, provenance = convert_batch001(args.file)
        if args.output.exists() or args.provenance.exists():
            raise ValueError("Output files must be new")
        write_jsonl(args.output, rows)
        with args.provenance.open("x", encoding="utf-8") as stream:
            json.dump(provenance, stream, ensure_ascii=False, indent=2)
        print(json.dumps({"records": len(rows), "publication": "pending"}))
    elif args.command == "export":
        _, records = load_records(args.file)
        generator = ModelIdentity(
            provider=args.generator_provider,
            model=args.generator_model,
            version=args.generator_version,
        )
        catalog = load_records(args.catalog_file)[1] if args.catalog_file else []
        write_jsonl(args.output, review_inputs(records, generator, catalog))
        print("Review input exported. Independent semantic review is pending; no reviewer invoked.")
    elif args.command == "schemas":
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(
                {
                    "input": ReviewInput.model_json_schema(),
                    "output": ReviewResult.model_json_schema(),
                },
                stream,
                indent=2,
            )
    elif args.command == "submit":
        requests = load_exchange(args.request, ReviewInput)
        results = load_exchange(args.results, ReviewResult)
        async with session_factory() as session:
            print(json.dumps(await import_reviews(session, requests, results, args.operator)))
    else:
        async with session_factory() as session:
            print(json.dumps(await coverage(session), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    convert = commands.add_parser("convert-batch001")
    convert.add_argument("--file", type=Path, required=True)
    convert.add_argument("--output", type=Path, required=True)
    convert.add_argument("--provenance", type=Path, required=True)
    export = commands.add_parser("export")
    export.add_argument("--file", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--catalog-file", type=Path)
    for field in ("provider", "model", "version"):
        export.add_argument(f"--generator-{field}", required=True)
    schemas = commands.add_parser("schemas")
    schemas.add_argument("--output", type=Path, required=True)
    submit = commands.add_parser("submit")
    submit.add_argument("--request", type=Path, required=True)
    submit.add_argument("--results", type=Path, required=True)
    submit.add_argument("--operator", required=True)
    commands.add_parser("report")
    try:
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            runner.run(run(parser.parse_args()))
    except Exception:  # noqa: BLE001 -- suppress secrets in database/provider errors
        parser.exit(
            1, "Review operation failed; verify exchange, revision and database configuration.\n"
        )


if __name__ == "__main__":
    main()
