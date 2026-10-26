"""Audit, review, reconcile, import and submit; no implicit migration or publication toggle."""

import argparse
import asyncio
import json
import os
from collections import Counter
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.services.curated_audit import scan_dataset
from app.services.curated_bulk import import_batches, plan_token, reconcile
from app.services.curated_import import digest, load_records
from app.services.curated_review import import_reviews, review_inputs
from app.services.curated_reviewer import (
    AnthropicReviewer,
    load_run,
    run_reviews,
    verified_generators,
    write_new,
)


def effective_sources(root, audit, review_dir):
    """Overlay reviewed, versioned corrections without modifying source artifacts."""
    evidence = load_run(review_dir) if review_dir else []
    replacements = {}
    for request, result in evidence:
        key = request.content.lexical_key
        if (
            key not in replacements
            or request.content.content_version > replacements[key].content_version
        ):
            replacements[key] = request.content
    effective = []
    files = []
    for batch in audit["files"]:
        _, records = load_records(root / batch["file"])
        rows = []
        for r in records:
            new = replacements.pop(r.lexical_key, r)
            if new.content_version < r.content_version:
                raise ValueError("Review run predates source")
            if new.content_version == r.content_version and new != r:
                raise ValueError("Changed review content requires a higher version")
            rows.append(new)
        effective.extend(rows)
        files.append((batch, rows))
    if replacements:
        raise ValueError("Review run contains unknown source identities")
    return effective, files, evidence


async def database_run(args, audit, records):
    url = os.environ.get(args.database_env)
    if not url or make_url(url).drivername != "postgresql+psycopg":
        raise ValueError("Select an explicit PostgreSQL environment variable")
    effective, files, evidence = effective_sources(args.dataset, audit, args.review_dir)
    engine = create_async_engine(url, connect_args={"connect_timeout": 10})
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions() as session:
            plan = await reconcile(session, audit, effective)
        plan["allow_ai_approved_vocabulary"] = get_settings().allow_ai_approved_vocabulary
        plan["write_plan"] = {
            "operation": args.operation,
            "source_files": audit["files"],
            "review_run_config_sha256": digest((args.review_dir / "config.json").read_bytes())
            if args.review_dir
            else None,
            "review_evidence_ids": [str(result.review_id) for _, result in evidence],
            "tables": (
                [
                    "curated_vocabulary_batches",
                    "curated_vocabulary",
                    "vocabulary_meanings",
                    "vocabulary_examples",
                    "curated_vocabulary_revisions",
                ]
                if args.operation == "import"
                else ["curated_vocabulary_ai_reviews", "curated_vocabulary"]
            ),
            "per_batch_transactions": True,
            "user_tables_modified": False,
        }
        token = plan_token(plan, audit)
        report = {"audit": audit, "database": plan, "confirmation_token": token}
        report["execution"] = {
            "read_only": args.command in {"plan", "report"},
            "review_provider_configured": os.environ.get("VOCAB_REVIEW_PROVIDER"),
            "review_model_configured": os.environ.get("VOCAB_REVIEW_MODEL"),
            "review_credentials_configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "selected_run_review_receipts": len(evidence),
            "publication_flag_changed": False,
        }
        report["per_batch_reconciliation"] = []
        by_key = {a["lexical_key"]: a["action"] for a in plan.get("actions", [])}
        for batch, rows in files:
            report["per_batch_reconciliation"].append(
                {
                    "batch": batch["batch"],
                    "actions": dict(Counter(by_key.get(r.lexical_key, "BLOCKED") for r in rows)),
                }
            )
        if args.command in {"plan", "report"}:
            write_new(args.output, report)
            print(
                json.dumps(
                    {
                        "identity": plan["identity"],
                        "migration": plan["migration"],
                        "action_counts": plan.get("action_counts"),
                        "confirmation_token": token,
                    }
                )
            )
            return
        if plan.get("blocked"):
            raise ValueError(plan["blocked"])
        if args.confirm != token:
            raise ValueError("Confirmation token does not match current database/write plan")
        if any(a["action"].endswith("CONFLICT") for a in plan["actions"]):
            raise ValueError("Resolve version/identity conflicts using new versioned corrections")
        if args.operation == "submit" and not evidence:
            raise ValueError("No genuine review run selected")
        if args.operation == "import":
            # Source batches use the existing importer. Corrected batches use immutable derived bytes.
            if not args.review_dir:

                def progress(batch, result):
                    print(json.dumps({"committed_batch": batch, **result}))

                await import_batches(sessions, args.dataset, audit, progress)
            else:
                from app.services.curated_import import import_records

                for batch, rows in files:
                    payload = "\n".join(r.model_dump_json() for r in rows).encode()
                    sha = digest(payload)
                    async with sessions() as session:
                        result = await import_records(
                            session, f"bulk-{batch['batch']}-{sha}", sha, rows
                        )
                    print(json.dumps({"committed_batch": batch["batch"], **result}))
        else:
            if not args.operator:
                raise ValueError("Named submitting operator required")
            current = {r.lexical_key: r for r in effective}
            for request, result in evidence:
                if request.content != current[request.content.lexical_key]:
                    continue  # Old findings stay in receipts; stale approvals are never submitted.
                async with sessions() as session:
                    counts = await import_reviews(session, [request], [result], args.operator)
                print(json.dumps({"review_id": str(result.review_id), **counts}))
        async with sessions() as session:
            report["after"] = await reconcile(session, audit, effective)
        write_new(args.output, report)
    finally:
        await engine.dispose()


async def run(args):
    audit, records = scan_dataset(args.dataset)
    if args.command == "audit":
        write_new(args.output, audit)
        print(
            json.dumps(
                {
                    k: audit[k]
                    for k in ("structural_integrity", "generated_records", "unique_learning_items")
                }
            )
        )
        return 0 if audit["structural_integrity"] == "PASSED" else 1
    if audit["structural_integrity"] != "PASSED":
        raise ValueError("Dataset integrity failed; run audit")
    if args.command == "review":
        generators = verified_generators(args.dataset, audit, args.provenance)
        reviewer = AnthropicReviewer()
        secondary = (
            AnthropicReviewer("VOCAB_REVIEW_SECONDARY_MODEL")
            if os.environ.get("VOCAB_REVIEW_SECONDARY_MODEL")
            else None
        )
        requests = []
        for batch in audit["files"]:
            _, rows = load_records(args.dataset / batch["file"])
            requests.extend(review_inputs(rows, generators[batch["batch"]], records))
        counts = run_reviews(
            requests,
            args.run_dir,
            reviewer,
            max_calls=args.max_calls,
            max_tokens=args.max_output_tokens,
            attempts=args.attempts,
            correction_reviewer=secondary,
        )
        write_new(
            args.output,
            {
                "configured_reviewer": reviewer.identity.model_dump(),
                "validated_provider_results": len(load_run(args.run_dir)),
                "results": counts,
                "provenance_ledger_sha256": digest(args.provenance.read_bytes()),
            },
        )
        print(json.dumps(counts))
        return 0
    await database_run(args, audit, records)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs/datasets/original-zhvi",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--output", type=Path, required=True)
    review = commands.add_parser("review")
    review.add_argument("--provenance", type=Path, required=True)
    review.add_argument("--run-dir", type=Path, required=True)
    review.add_argument("--max-calls", type=int, required=True)
    review.add_argument("--max-output-tokens", type=int, required=True)
    review.add_argument("--attempts", type=int, default=2)
    review.add_argument("--output", type=Path, required=True)
    for name in ("plan", "report", "execute"):
        command = commands.add_parser(name)
        command.add_argument(
            "--database-env", required=True, help="Name of explicitly selected URL variable"
        )
        command.add_argument("--operation", choices=("import", "submit"), default="import")
        command.add_argument("--review-dir", type=Path)
        command.add_argument("--output", type=Path, required=True)
        if name == "execute":
            command.add_argument(
                "--confirm",
                required=True,
                help="Token from read-only plan; explicit bulk-write confirmation",
            )
            command.add_argument("--operator")
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("Output must be a new file")
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            code = runner.run(run(args))
    except Exception as exc:  # noqa: BLE001 -- never expose DB URLs, provider bodies or secrets
        parser.exit(
            1,
            f"Pipeline refused/failed ({type(exc).__name__}); check configuration and audit artifacts.\n",
        )
    raise SystemExit(code)


if __name__ == "__main__":
    main()
