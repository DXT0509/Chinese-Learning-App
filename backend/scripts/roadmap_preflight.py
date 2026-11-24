"""Read-only full-row fingerprints for an operator-approved migration; never prints data/URLs."""

import argparse
import json
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def inspect_database(baseline=None):
    source = make_url(get_settings().database_url)
    with psycopg.connect(
        host=source.host,
        port=source.port or 5432,
        user=source.username,
        password=source.password,
        dbname=source.database,
    ) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        if baseline is None and revision != "0014_fsrs_only":
            raise RuntimeError("Preflight requires revision 0014_fsrs_only")
        if baseline is not None and revision != "0015_roadmap_engine":
            raise RuntimeError("Verification requires revision 0015_roadmap_engine")
        columns = {}
        for table, column in connection.execute("""
          SELECT table_name,column_name FROM information_schema.columns
          WHERE table_schema='public' AND table_name <> 'alembic_version'
          ORDER BY table_name,ordinal_position
        """):
            columns.setdefault(table, []).append(column)
        selected = (
            {name: row["columns"] for name, row in baseline["tables"].items()}
            if baseline
            else columns
        )
        tables = {}
        for table, fields in selected.items():
            # Each row is hashed on the server; only sorted hashes/counts cross this boundary.
            query = sql.SQL("""SELECT count(*), md5(coalesce(string_agg(h,'' ORDER BY h),''))
                FROM (SELECT md5(jsonb_build_array({fields})::text) AS h FROM {table}) rows""").format(
                fields=sql.SQL(",").join(map(sql.Identifier, fields)), table=sql.Identifier(table)
            )
            count, digest = connection.execute(query).fetchone()
            tables[table] = {"columns": fields, "rows": count, "fingerprint": digest}
        return {"revision": revision, "tables": tables}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.output:
        # Refuse replacement of an earlier preflight audit.
        result = inspect_database()
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
        print("Read-only preflight recorded; migration remains pending operator approval")
    else:
        baseline = json.loads(args.verify.read_text("utf-8"))
        result = inspect_database(baseline)
        if result["tables"] != baseline["tables"]:
            raise RuntimeError("Preservation verification differs; inspect before reopening writes")
        print("Every original table row/column fingerprint preserved at 0015_roadmap_engine")


if __name__ == "__main__":
    main()
