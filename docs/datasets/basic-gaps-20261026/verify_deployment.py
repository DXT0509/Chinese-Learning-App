"""Read-only supplement preview/preservation checks and local backup, never DB writes."""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyLocalReview
from app.schemas.dictionary import DictionaryQuery
from app.services.curated_catalog import CuratedCatalog, visible
from app.services.curated_import import record_checksum
from app.services.local_codex_review import canonical, digest, load_checkpoint, preview

ROOT = Path(__file__).resolve().parent
PRIVATE = Path(".vocabulary-pipeline/basic-gaps-20261026")
APPEND_ONLY = {
    "curated_vocabulary",
    "curated_vocabulary_batches",
    "curated_vocabulary_revisions",
    "curated_vocabulary_local_reviews",
    "vocabulary_meanings",
    "vocabulary_examples",
}


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


async def inspect(stage):
    settings = get_settings()
    url = make_url(settings.database_url)
    assert url.database == "chinese_learning" and url.host in ("127.0.0.1", "localhost")
    assert (url.port or 5432) == 5432 and url.username == "postgres"
    assert settings.environment == "development" and settings.allow_local_codex_reviewed_vocabulary
    records, evidence, coverage = load_checkpoint(ROOT / "checkpoint")
    assert len(records) == 322 and coverage["unreviewed"] == 0 and not coverage["excluded"]
    planned = json.loads((ROOT / "import-plan.json").read_text(encoding="utf-8"))
    engine = create_async_engine(settings.database_url, echo=False)
    try:
        async with engine.connect() as c, c.begin():
            await c.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
            async with AsyncSession(c) as s:
                identity = list(
                    (
                        await s.execute(
                            text(
                                "SELECT current_database(), inet_server_addr()::text, inet_server_port(), current_user"
                            )
                        )
                    ).one()
                )
                assert identity == planned["database"]
                revisions = list(await s.scalars(text("SELECT version_num FROM alembic_version")))
                assert revisions == ["0010_local_codex_review"]
                words = list(await s.scalars(select(CuratedVocabulary)))
                statuses = dict(Counter(w.review_status for w in words))
                tables = list(
                    await s.scalars(
                        text(
                            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
                        )
                    )
                )
                hashes = {}
                for table in tables:
                    quoted = engine.dialect.identifier_preparer.quote(table)
                    rows = await s.scalars(
                        text("SELECT to_jsonb(t)::text FROM public." + quoted + " AS t")
                    )
                    hashes[table] = sorted(
                        hashlib.sha256(r.encode("utf-8")).hexdigest() for r in rows
                    )
                count_visible = await s.scalar(
                    select(func.count()).select_from(CuratedVocabulary).where(visible())
                )
                receipts = list(await s.scalars(select(VocabularyLocalReview)))
                result = {
                    "checked_at": datetime.now(UTC).isoformat(),
                    "database": identity,
                    "migrations": revisions,
                    "catalog_records": len(words),
                    "status_counts": statuses,
                    "search_visible_by_enabled_application_predicate": count_visible,
                    "local_receipts": len(receipts),
                    "protected_editorial_holds": statuses.get("NEEDS_REVIEW", 0),
                    "unresolved_old_drafts_still_excluded": 13,
                    "transaction": "REPEATABLE READ READ ONLY",
                    "database_writes": 0,
                    "tables": hashes,
                }
                assert statuses.get("NEEDS_REVIEW") == 6
                if stage == "before":
                    assert len(words) == 2488 and count_visible == 2482 and len(receipts) == 2482
                    live = await preview(s, records, evidence, coverage)
                    assert live == planned
                    assert len(live["changes"]) == 322
                    assert all(
                        change["action"] == "INSERT_AND_ACCEPT_LOCAL" and change["before"] is None
                        for change in live["changes"]
                    )
                    assert not {r.simplified for r in records} & {w.simplified for w in words}
                    write_new(PRIVATE / "before.json", result)
                    print(
                        json.dumps(
                            {
                                "target": identity,
                                "checked_actions": 322,
                                "insert_only": True,
                                "conflicts": 0,
                                "existing_tables_snapshotted": len(tables),
                                "database_writes": 0,
                            }
                        )
                    )
                else:
                    before = json.loads((PRIVATE / "before.json").read_text(encoding="utf-8"))
                    assert set(hashes) == set(before["tables"])
                    for table, previous in before["tables"].items():
                        if table in APPEND_ONLY:
                            assert not (Counter(previous) - Counter(hashes[table])), (
                                "Existing row changed: " + table
                            )
                        else:
                            assert previous == hashes[table], "Protected table changed: " + table
                    assert len(words) == 2810 and statuses.get("LOCAL_CODEX_REVIEWED") == 2804
                    assert count_visible == 2804 and len(receipts) == 2804
                    expected_delta = {
                        "curated_vocabulary_batches": 1,
                        "curated_vocabulary": 322,
                        "curated_vocabulary_revisions": 322,
                        "curated_vocabulary_local_reviews": 322,
                        "vocabulary_examples": 322,
                        "vocabulary_meanings": sum(len(r.vietnamese_meanings) for r in records),
                    }
                    for table, delta in expected_delta.items():
                        assert len(hashes[table]) - len(before["tables"][table]) == delta
                    by_key = {w.lexical_key: w for w in words}
                    bound = {(r.vocabulary_id, r.checksum, r.content_version): r for r in receipts}
                    for record in records:
                        word = by_key[record.lexical_key]
                        assert word.review_status == "LOCAL_CODEX_REVIEWED"
                        assert word.content_version == 1 and word.checksum == record_checksum(
                            record
                        )
                        receipt = bound[word.id, word.checksum, 1]
                        assert receipt.submitted_by == "dxt"
                        assert receipt.evidence == evidence[record.lexical_key]
                        assert receipt.evidence_checksum == digest(canonical(receipt.evidence))
                    # All original rows remain byte-equivalent; explicitly bind unresolved keys as well.
                    old_source = [
                        json.loads(line)
                        for line in (
                            ROOT.parent / "codex-review-4.0.3" / "provisional-deployment.jsonl"
                        )
                        .read_text(encoding="utf-8")
                        .splitlines()
                    ]
                    baseline_forms = set(
                        json.loads((ROOT / "coverage-scan.json").read_text(encoding="utf-8"))[
                            "all_existing_catalog_forms"
                        ]
                    )
                    assert all(
                        r["lexical_key"] not in by_key
                        for r in old_source
                        if r["simplified"] not in baseline_forms
                    )
                    catalog = CuratedCatalog(s)
                    for record in records:
                        page = await catalog.search(DictionaryQuery(q=record.simplified, limit=50))
                        hit = next(w for w in page.items if w.simplified == record.simplified)
                        detail = await catalog.get_entry(hit.entry_id)
                        assert detail.review_status == "LOCAL_CODEX_REVIEWED"
                    result["all_322_new_entries_search_and_detail_verified"] = True
                    result["all_existing_database_rows_preserved"] = True
                    result["protected_tables_unchanged"] = len(set(tables) - APPEND_ONLY)
                    result["operator"] = "dxt"
                    write_new(PRIVATE / "after.json", result)
                    print(json.dumps({k: v for k, v in result.items() if k != "tables"}))
    finally:
        await engine.dispose()


def backup():
    url = make_url(get_settings().database_url)
    binary = Path(r"C:\Program Files\PostgreSQL\18\bin")
    path = PRIVATE / "before-basic-supplement.dump"
    assert not path.exists()
    child = dict(
        os.environ,
        PGHOST=url.host,
        PGPORT=str(url.port or 5432),
        PGUSER=url.username,
        PGDATABASE=url.database,
        PGPASSWORD=url.password or "",
    )
    subprocess.run(
        [str(binary / "pg_dump.exe"), "--no-password", "-Fc", "-f", str(path)],
        env=child,
        check=True,
        capture_output=True,
    )
    assert path.stat().st_size > 0
    subprocess.run(
        [str(binary / "pg_restore.exe"), "--list", str(path)], check=True, capture_output=True
    )
    subprocess.run(
        [str(binary / "pg_restore.exe"), "--file=NUL", str(path)], check=True, capture_output=True
    )
    result = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": digest(path.read_bytes()),
        "archive_fully_readable": True,
        "restore_to_database_performed": False,
        "database_writes": 0,
    }
    write_new(PRIVATE / "backup-verification.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["before", "after"])
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(inspect(args.stage))
    if args.stage == "before":
        backup()
