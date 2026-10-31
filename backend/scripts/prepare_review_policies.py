"""Read-only bulk preparation; no migration, policy installation or learner writes."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from sqlalchemy import text

from app.core.database import session_factory
from app.core.event_loop import new_event_loop
from app.services.policy_coverage import prepare_coverage
from app.services.policy_preparation import catalog_entries, installed_policies, prepare
from app.services.review_targets import ReviewedPolicy


def write_new(path, payload):
    with Path(path).open("x", encoding="utf-8", newline="\n") as output:
        output.write(payload)


async def run(args):
    async with session_factory() as session, session.begin():
        await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        existing = await installed_policies(session)
        installed_keys = {(p.vocabulary_id, p.content_version, p.checksum) for p in existing}
        if args.preserve_file:
            existing += [
                ReviewedPolicy.model_validate(p)
                for p in json.loads(Path(args.preserve_file).read_text(encoding="utf-8"))
            ]
        entries = await catalog_entries(session)
        if args.complete_coverage:
            policies, report = prepare_coverage(entries, existing, installed_keys=installed_keys)
        else:
            policies, report = prepare(entries, existing)
        report["source_revision"] = await session.scalar(
            text("SELECT version_num FROM alembic_version")
        )
        report["installed_policy_count"] = len(await installed_policies(session))
        report["preserved_file"] = args.preserve_file
        target = (
            (
                await session.execute(
                    text(
                        "SELECT current_database() AS database, current_user AS role, "
                        "inet_server_addr()::text AS host, inet_server_port() AS port"
                    )
                )
            )
            .mappings()
            .one()
        )
        report["database_target"] = dict(target)
    payload = (
        json.dumps([p.model_dump(mode="json") for p in policies], ensure_ascii=False, indent=2)
        + "\n"
    )
    report["policy_bundle_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    report["database_writes"] = 0
    if args.output:
        # Refuse accidental replacement of a previously reviewed bundle.
        await asyncio.to_thread(write_new, args.output, payload)
    if args.audit:
        await asyncio.to_thread(
            write_new, args.audit, json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        )
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in ("records", "examples")}, ensure_ascii=True
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Explicit read-only preview (default)"
    )
    parser.add_argument("--output", help="New JSON bundle file; never installed")
    parser.add_argument("--audit", help="New detailed JSON audit file")
    parser.add_argument("--preserve-file", help="Also preserve an uninstalled reviewed JSON array")
    parser.add_argument(
        "--complete-coverage", action="store_true", help="Additive v2 coverage audit"
    )
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(run(args))


if __name__ == "__main__":
    main()
