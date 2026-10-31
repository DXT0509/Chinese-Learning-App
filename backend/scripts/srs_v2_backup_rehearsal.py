"""Read-only consistent backup, restore into a fresh isolated DB and fingerprint verification."""

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def fingerprints(connection):
    tables = connection.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name"
    ).fetchall()
    result = {}
    for (name,) in tables:
        rows = connection.execute(
            sql.SQL("SELECT to_jsonb(t) FROM {} t").format(sql.Identifier(name))
        ).fetchall()
        result[name] = {
            "rows": len(rows),
            "sha256": hashlib.sha256(
                "\n".join(sorted(json.dumps(r[0], sort_keys=True) for r in rows)).encode()
            ).hexdigest(),
        }
    return result


def main():
    source = make_url(get_settings().database_url)
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    restore_name = f"chinese_srs_v2_restore_{stamp}"
    backup = Path(".vocabulary-backups") / f"srs-v2-{stamp}.dump"
    backup.parent.mkdir(exist_ok=True)
    pg_bin = Path(os.environ.get("PG_BIN", "C:/Program Files/PostgreSQL/18/bin"))
    connection_args = {
        "host": source.host,
        "port": source.port or 5432,
        "user": source.username,
        "password": source.password,
    }
    env = {
        **os.environ,
        "PGHOST": source.host,
        "PGPORT": str(source.port or 5432),
        "PGUSER": source.username,
        "PGPASSWORD": source.password,
    }
    with psycopg.connect(**connection_args, dbname=source.database) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        snapshot = connection.execute("SELECT pg_export_snapshot()").fetchone()[0]
        before = fingerprints(connection)
        dump = subprocess.run(
            [
                str(pg_bin / "pg_dump.exe"),
                "--format=custom",
                "--snapshot",
                snapshot,
                "--file",
                str(backup),
                source.database,
            ],
            env=env,
            capture_output=True,
            check=False,
        )
        if dump.returncode:
            raise RuntimeError("Read-only backup failed; no restore attempted")
    with psycopg.connect(**connection_args, dbname="postgres", autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(restore_name)))
    restore = subprocess.run(
        [
            str(pg_bin / "pg_restore.exe"),
            "--no-owner",
            "--no-privileges",
            "--exit-on-error",
            "--dbname",
            restore_name,
            str(backup),
        ],
        env=env,
        capture_output=True,
        check=False,
    )
    if restore.returncode:
        raise RuntimeError(
            "Isolated restore failed; retain backup and restore database for inspection"
        )
    with psycopg.connect(**connection_args, dbname=restore_name) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        after = fingerprints(connection)
    if before != after:
        raise RuntimeError("Restore fingerprint mismatch; do not deploy")
    report = {
        "verified_at": datetime.now(UTC).isoformat(),
        "source_database_writes": 0,
        "restore_database": restore_name,
        "backup_path": str(backup),
        "backup_size_bytes": backup.stat().st_size,
        "backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
        "all_public_table_fingerprints_match": True,
        "table_count": len(before),
        "tables": before,
    }
    Path("../docs/srs-v2-backup-rehearsal.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(f"Backup restored and verified across {len(before)} tables; development writes: zero")


if __name__ == "__main__":
    main()
