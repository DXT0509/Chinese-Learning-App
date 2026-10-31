"""Create fresh dedicated databases and run checks; never migrate configured development."""

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def main():
    source = make_url(get_settings().database_url)
    suffix = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    names = [
        f"chinese_srs_v2_{kind}_{suffix}"
        for kind in ("test", "upgrade", "concurrent", "creation", "srs", "v2")
    ]
    with psycopg.connect(
        host=source.host,
        port=source.port or 5432,
        user=source.username,
        password=source.password,
        dbname="postgres",
        autocommit=True,
    ) as connection:
        for name in names:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            print(f"Created isolated database {name}", flush=True)
    urls = [source.set(database=name).render_as_string(hide_password=False) for name in names]
    for url in (urls[0], *urls[2:]):
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env={**os.environ, "DATABASE_URL": url},
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("Isolated migration failed; inspect isolated schema")
    env = {
        **os.environ,
        "ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY": "false",
        "ALLOW_AI_APPROVED_VOCABULARY": "false",
        "DATABASE_URL": urls[0],
        "TEST_DATABASE_URL": urls[0],
        "SRS_V2_MIGRATION_TEST_DATABASE_URL": urls[1],
        "REVIEW_CONCURRENCY_TEST_DATABASE_URL": urls[2],
        "SRS_CONCURRENCY_TEST_DATABASE_URL": urls[4],
        "SRS_CREATION_CONCURRENCY_TEST_DATABASE_URL": urls[3],
        "SRS_V2_CONCURRENCY_TEST_DATABASE_URL": urls[5],
    }
    Path(".test-postgres-slice2-v2").mkdir(exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--basetemp",
            f".test-postgres-slice2-v2/pytest-{suffix}",
            "-o",
            f"cache_dir=.test-postgres-slice2-v2/cache-{suffix}",
        ],
        env=env,
        check=False,
    )
    check = subprocess.run(
        [sys.executable, "-m", "alembic", "check"], env=env, capture_output=True, check=False
    )
    print(f"Isolated alembic check exit: {check.returncode}; fixtures retained", flush=True)
    sys.exit(result.returncode or check.returncode)


if __name__ == "__main__":
    main()
