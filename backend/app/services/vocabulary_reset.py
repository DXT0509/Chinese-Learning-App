"""Explicit local maintenance only. Never imported by startup, migration or importer."""

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app.core.config import Settings

# Child-first; every cascaded child is included explicitly. No TRUNCATE CASCADE.
CLEAR_TABLES = (
    "personal_vocabulary_entries",
    "srs_states",
    "user_vocabulary",
    "lesson_vocabulary",
    "vocabulary_characters",
    "vocabulary",
    "dictionary_character_enrichments",
    "dictionary_enrichment_imports",
    "dictionary_entries",
    "dictionary_imports",
)


def file_checksum(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def fingerprint(report):
    return hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()


def local_identity(settings: Settings, database, host, port):
    url = make_url(settings.database_url)
    if settings.environment != "development" or url.host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Reset requires an explicitly selected loopback development database")
    identity = {"database": url.database, "host": url.host, "port": url.port or 5432}
    if identity != {"database": database, "host": host, "port": port}:
        raise ValueError("Explicit database identity does not match configured database")
    return identity


async def inventory(connection):
    def schema(sync):
        inspector = inspect(sync)
        names = sorted(inspector.get_table_names(schema="public"))
        dependencies = []
        for name in names:
            for fk in inspector.get_foreign_keys(name, schema="public"):
                dependencies.append(
                    {
                        "table": name,
                        "constraint": fk["name"],
                        "columns": fk["constrained_columns"],
                        "target": fk["referred_table"],
                        "target_columns": fk["referred_columns"],
                        "options": fk["options"],
                    }
                )
        return names, dependencies

    names, dependencies = await connection.run_sync(schema)
    if not set(CLEAR_TABLES).issubset(names):
        raise ValueError("Expected legacy schema is incomplete")
    # Lock the entire inspected schema before counting or backing up. Ordinary SELECTs
    # (including pg_dump) still work; concurrent application writes cannot race approval.
    quoted = ", ".join('public."' + n.replace('"', '""') + '"' for n in names)
    await connection.execute(text("SET LOCAL lock_timeout = '5s'"))
    await connection.execute(text("LOCK TABLE " + quoted + " IN SHARE ROW EXCLUSIVE MODE"))
    for dependency in dependencies:
        if dependency["target"] in CLEAR_TABLES and dependency["table"] not in CLEAR_TABLES:
            raise ValueError("Unexpected preserved-table dependency on reset data")
    # Catch inbound dependencies outside public too; do not silently cascade them.
    external = await connection.scalar(
        text("""
        SELECT count(*) FROM pg_constraint c
        JOIN pg_class child ON child.oid=c.conrelid
        JOIN pg_namespace ns ON ns.oid=child.relnamespace
        JOIN pg_class parent ON parent.oid=c.confrelid
        JOIN pg_namespace pn ON pn.oid=parent.relnamespace
        WHERE c.contype='f' AND ns.nspname <> 'public' AND pn.nspname='public'
          AND parent.relname = ANY(:tables)
    """),
        {"tables": list(CLEAR_TABLES)},
    )
    if external:
        raise ValueError("External schema references legacy vocabulary")
    counts = {
        name: await connection.scalar(
            text('SELECT count(*) FROM public."' + name.replace('"', '""') + '"')
        )
        for name in names
    }
    table_checksums = {
        name: await connection.scalar(
            text(
                "SELECT md5(coalesce(string_agg(row::text, E'\\n' ORDER BY row::text), '')) "
                'FROM (SELECT to_jsonb(t) AS row FROM public."'
                + name.replace('"', '""')
                + '" t) snapshot'
            )
        )
        for name in names
    }
    server = (
        (
            await connection.execute(
                text(
                    "SELECT current_database() AS database, inet_server_addr()::text AS server_address, inet_server_port() AS port, (SELECT oid FROM pg_database WHERE datname=current_database()) AS database_oid, pg_postmaster_start_time()::text AS server_started"
                )
            )
        )
        .mappings()
        .one()
    )
    triggers = [
        dict(r)
        for r in (
            await connection.execute(
                text("""
        SELECT event_object_table AS table, trigger_name, action_statement
        FROM information_schema.triggers WHERE trigger_schema='public'
        ORDER BY event_object_table, trigger_name, event_manipulation
    """)
            )
        ).mappings()
    ]
    if any(
        t["table"] in CLEAR_TABLES
        and (t["table"], t["trigger_name"]) != ("lesson_vocabulary", "lesson_vocabulary_immutable")
        for t in triggers
    ):
        raise ValueError(
            "Unexpected trigger on a reset table; review dependencies before proceeding"
        )
    published_links = await connection.scalar(
        text(
            "SELECT count(*) FROM lesson_vocabulary lv JOIN lesson_versions v ON v.id=lv.lesson_version_id WHERE v.status='PUBLISHED'"
        )
    )
    return {
        "server": dict(server),
        "alembic": list(
            await connection.scalars(
                text("SELECT version_num FROM alembic_version ORDER BY version_num")
            )
        ),
        "clear": {n: counts[n] for n in CLEAR_TABLES},
        "preserve": {n: counts[n] for n in names if n not in CLEAR_TABLES},
        "preserved_checksums": {n: table_checksums[n] for n in names if n not in CLEAR_TABLES},
        "cleared_checksums": {n: table_checksums[n] for n in CLEAR_TABLES},
        "foreign_keys": dependencies,
        "triggers": triggers,
        "published_vocabulary_links_removed": published_links,
        "consequences": "All legacy vocabulary, personal associations and vocabulary SRS are deleted. All lesson-vocabulary links, including published links, are removed. Lesson versions, immutable bundle bytes, assets, runs, bookmarks and completion records remain historical; bundle vocabulary UUIDs no longer resolve in dictionary APIs. No mastery or completion is inferred. Curated catalog and its unified state are preserved.",
    }


async def prepare(connection, settings, identity, backup_dir: Path, pg_dump="pg_dump"):
    snapshot = await inventory(connection)
    if (
        snapshot["server"]["database"] != identity["database"]
        or snapshot["server"]["port"] != identity["port"]
    ):
        raise ValueError("Connected server identity mismatch")
    executable = shutil.which(pg_dump)
    if not executable:
        raise ValueError("pg_dump is required")
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    backup = (backup_dir / f"vocabulary-before-reset-{stamp}.dump").resolve()
    url = make_url(settings.database_url)
    environment = os.environ.copy()
    environment.update(
        PGHOST=identity["host"],
        PGPORT=str(identity["port"]),
        PGDATABASE=identity["database"],
        PGUSER=url.username or "",
        PGPASSWORD=url.password or "",
        PGCONNECT_TIMEOUT="10",
    )
    exported = await connection.scalar(text("SELECT pg_export_snapshot()"))
    # Executed by the CLI's worker event loop; no async HTTP route calls this utility.
    result = await asyncio.to_thread(
        subprocess.run,
        [
            executable,
            "--format=custom",
            "--no-password",
            "--snapshot=" + exported,
            "--file=" + str(backup),
        ],
        env=environment,
        capture_output=True,
        timeout=600,
        check=False,
    )
    if result.returncode or not backup.is_file() or backup.stat().st_size == 0:
        raise ValueError("Backup failed; reset forbidden")
    report = {
        "format": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "identity": identity,
        "inventory": snapshot,
        "backup": {
            "path": str(backup),
            "size": backup.stat().st_size,
            "sha256": file_checksum(backup),
        },
    }
    report["confirmation"] = fingerprint(report)
    return report


async def execute_reset(connection, report, confirmation, identity):
    unsigned = {k: v for k, v in report.items() if k != "confirmation"}
    if (
        report.get("confirmation") != confirmation
        or fingerprint(unsigned) != confirmation
        or report["identity"] != identity
    ):
        raise ValueError("Confirmation does not match reviewed report")
    age = (datetime.now(UTC) - datetime.fromisoformat(report["created_at"])).total_seconds()
    if not 0 <= age <= 86400:
        raise ValueError("Dry-run report expired; prepare a new backup")
    backup = Path(report["backup"]["path"])
    if (
        not backup.is_file()
        or backup.stat().st_size != report["backup"]["size"]
        or file_checksum(backup) != report["backup"]["sha256"]
    ):
        raise ValueError("Verified backup is missing or changed")
    current = await inventory(connection)
    if current != report["inventory"]:
        raise ValueError("Database changed since dry run; create a fresh report and backup")
    if not any(current["clear"].values()):
        return {"deleted": current["clear"], "already_empty": True}
    # Product-owner-authorized removal of obsolete vocabulary links only. The named
    # guard is restored inside this transaction; any error rolls back both DDL and data.
    await connection.execute(
        text("ALTER TABLE public.lesson_vocabulary DISABLE TRIGGER lesson_vocabulary_immutable")
    )
    for name in CLEAR_TABLES:
        await connection.execute(text(f'DELETE FROM public."{name}"'))
    await connection.execute(
        text("ALTER TABLE public.lesson_vocabulary ENABLE TRIGGER lesson_vocabulary_immutable")
    )
    after = await inventory(connection)
    if (
        any(after["clear"].values())
        or after["preserve"] != current["preserve"]
        or after["preserved_checksums"] != current["preserved_checksums"]
    ):
        raise ValueError("Reset postconditions failed; transaction must roll back")
    return {"deleted": current["clear"], "preserved": after["preserve"]}
