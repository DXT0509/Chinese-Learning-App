"""Guarded, retry-safe LOCAL DEVELOPMENT deployment of the exact owner-approved HSK 0 v4."""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
from pathlib import Path
from uuid import uuid5

import psycopg
from psycopg import sql
from sqlalchemy import select
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.core.database import engine, session_factory
from app.core.event_loop import new_event_loop
from app.models import Asset
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyRevision
from app.models.roadmap import Roadmap, RoadmapNode, RoadmapVersion
from app.schemas.content import content_id
from app.schemas.roadmap_preparation import PreparationPlan
from app.services.content_authoring import import_library
from app.services.content_files import ContentError, load_library
from app.services.content_storage import LocalContentStorage, verify_object
from app.services.curated_catalog import visible
from app.services.curated_import import record_checksum
from app.services.roadmap_authoring import (
    TEMPLATE_ID,
    TEMPLATE_VERSION_ID,
    activate,
    compile_preview,
    import_draft,
    publish,
    version_id,
)
from app.services.roadmap_preparation import (
    checksum,
    load_catalog,
    load_json,
    validate_generated,
    write_artifact,
)
from scripts.finalize_hsk0_review import audit_assets, audit_quizzes, audit_vocabulary, review_items
from scripts.prepare_hsk0_pack import CATALOG, PACK

SIGNED = PACK / "signed-complete-v4"
EXPECTED_SHA = "5431957cc5be3205393d1c5d47456f92afef5079d6cbe7741f4756eac2edcfcf"
PG_BIN = Path("C:/Program Files/PostgreSQL/18/bin")
TABLES = {
    "assets",
    "lessons",
    "lesson_versions",
    "lesson_templates",
    "lesson_template_versions",
    "roadmaps",
    "roadmap_versions",
    "roadmap_node_identities",
    "roadmap_nodes",
    "roadmap_vocabulary",
}


def target():
    settings = get_settings()
    url = make_url(settings.database_url)
    if (
        settings.environment != "development"
        or url.drivername != "postgresql+psycopg"
        or url.host != "127.0.0.1"
        or (url.port or 5432) != 5432
        or url.database != "chinese_learning"
    ):
        raise ContentError(
            "STOP: configured target is not the explicitly authorized local development database"
        )
    return url


def artifacts():
    plan = PreparationPlan.model_validate(load_json(SIGNED / "plan.json"))
    approval = load_json(SIGNED / "owner-authorization.json")
    evidence = load_json(SIGNED / "signoff-verification.json")
    bundle = load_json(SIGNED / "bundle.json")
    definition, report = validate_generated(plan, load_catalog([CATALOG]), PACK, SIGNED / "content")
    if (
        plan.version != 4
        or checksum(definition.model_dump(mode="json")) != EXPECTED_SHA
        or bundle["definition"] != definition.model_dump(mode="json")
        or checksum(plan.model_dump(mode="json")) != evidence["signed_plan_sha256"]
        or hashlib.sha256((SIGNED / "bundle.json").read_bytes()).hexdigest()
        != evidence["bundle_file_sha256"]
        or hashlib.sha256((SIGNED / "content/manifest.json").read_bytes()).hexdigest()
        != evidence["manifest_file_sha256"]
        or hashlib.sha256((SIGNED / "content/publication-candidate.json").read_bytes()).hexdigest()
        != evidence["publication_candidate_file_sha256"]
        or approval["educational_content_sha256"] != EXPECTED_SHA
        or approval["signed_plan_sha256"] != evidence["signed_plan_sha256"]
        or not report.payload()["draft_valid"]
        or report.payload()["counts"]["ERROR"]
    ):
        raise ContentError("STOP: approved bundle, manifest or content checksum mismatch")
    bound = {
        r["location"]: r["sha256"] for r in load_json(SIGNED / "review-bindings.json")["items"]
    }
    items = list(review_items(plan))
    if len(items) != 17 or len(bound) != 17:
        raise ContentError("STOP: expected exactly seventeen approved items")
    for location, _, item, review, excluded in items:
        if (
            review.status != "REVIEWED"
            or review.reviewer != "dxt"
            or review.evidence != "HSK0-EDU-REVIEW-20261102"
            or review.content_sha256 != checksum(item.model_dump(mode="json", exclude=excluded))
            or bound.get(location) != review.content_sha256
        ):
            raise ContentError("STOP: an approval identity, reference or bound checksum differs")
    audit_assets(plan)
    audit_vocabulary(plan, load_catalog([CATALOG]))
    audit_quizzes(definition, load_catalog([CATALOG]))
    library = load_library(SIGNED / "content/asset-library", assets_only=True)
    if (
        len(library.assets) != 6
        or len(definition.nodes) != 4
        or sum(len(n.lesson.activities) for n in definition.nodes) != 22
    ):
        raise ContentError("STOP: pack scope differs from authorization")
    return plan, definition, library


def snapshot(definition):
    url = target()
    with psycopg.connect(
        host=url.host,
        port=url.port or 5432,
        dbname=url.database,
        user=url.username,
        password=url.password,
    ) as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        name, host, port = connection.execute(
            "SELECT current_database(),host(inet_server_addr()),inet_server_port()"
        ).fetchone()
        revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        if (name, host, port, revision) != (
            "chinese_learning",
            "127.0.0.1",
            5432,
            "0015_roadmap_engine",
        ):
            raise ContentError("STOP: actual database identity or schema revision differs")
        table_names = [
            r[0]
            for r in connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
            )
        ]
        result = {}
        for table in table_names:
            keys = [
                r[0]
                for r in connection.execute(
                    """
                SELECT a.attname FROM pg_index i JOIN pg_attribute a
                ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey)
                WHERE i.indrelid=%s::regclass AND i.indisprimary ORDER BY a.attnum
            """,
                    (f"public.{table}",),
                )
            ]
            if not keys:
                raise ContentError("STOP: table without primary key cannot be preservation-audited")
            query = sql.SQL("""SELECT encode(sha256(convert_to(jsonb_build_array({keys})::text,'UTF8')),'hex'),
                encode(sha256(convert_to(to_jsonb(t)::text,'UTF8')),'hex') FROM {table} t""").format(
                keys=sql.SQL(",").join(map(sql.Identifier, keys)),
                table=sql.Identifier("public", table),
            )
            rows = dict(connection.execute(query).fetchall())
            result[table] = {"keys": keys, "rows": rows, "count": len(rows)}
        lesson_ids = [uuid5(version_id(definition), f"lesson:{n.id}") for n in definition.nodes]
        bundle_ids = [
            str(r[0])
            for r in connection.execute(
                "SELECT bundle_asset_id FROM roadmap_versions WHERE id=%s UNION SELECT bundle_asset_id FROM lesson_versions WHERE id=ANY(%s)",
                (version_id(definition), lesson_ids),
            )
            if r[0] is not None
        ]
        return {
            "target": {"host": host, "port": port, "database": name, "revision": revision},
            "tables": result,
            "publication_bundle_asset_ids": bundle_ids,
        }


async def database_preflight(definition, library):
    catalog = load_catalog([CATALOG])
    async with session_factory() as session, session.begin():
        from sqlalchemy import text

        await session.execute(text("SET TRANSACTION READ ONLY"))
        for ref in definition.nodes[-1].lesson.vocabulary:
            word = await session.scalar(
                select(CuratedVocabulary).where(
                    CuratedVocabulary.id == ref.vocabulary_id, visible()
                )
            )
            revision = await session.get(
                VocabularyRevision, (ref.vocabulary_id, ref.content_version)
            )
            if (
                not word
                or not revision
                or word.content_version != ref.content_version
                or word.checksum != revision.checksum
                or word.checksum != record_checksum(catalog[ref.vocabulary_id])
            ):
                raise ContentError("STOP: live approved catalog binding differs")
        for asset in library.assets:
            existing = await session.get(Asset, content_id("asset", asset.id))
            collision = await session.scalar(
                select(Asset).where(Asset.storage_key == asset.storage_key)
            )
            if collision and collision.id != content_id("asset", asset.id):
                raise ContentError(
                    "STOP: source object is registered with a different asset identity"
                )
            if existing and (
                existing.storage_key,
                existing.sha256,
                existing.byte_length,
                existing.media_type,
                existing.asset_metadata,
            ) != (
                asset.storage_key,
                asset.sha256,
                asset.byte_length,
                asset.media_type,
                asset.metadata.model_dump(exclude_none=True),
            ):
                raise ContentError("STOP: existing asset metadata differs")
        roadmap = await session.get(Roadmap, definition.id)
        release = await session.get(RoadmapVersion, version_id(definition))
        if roadmap and (
            roadmap.code != definition.code
            or roadmap.active_version_id not in (None, version_id(definition))
        ):
            raise ContentError("STOP: existing roadmap identity/active version differs")
        if release and release.definition != definition.model_dump(mode="json"):
            raise ContentError("STOP: existing release content differs")
        for node in definition.nodes:
            stable = await session.get(RoadmapNode, node.id)
            expected_word = (
                node.lesson.vocabulary[0].vocabulary_id if node.node_type == "NEW_WORD" else None
            )
            if stable and (stable.roadmap_id, stable.node_type, stable.vocabulary_id) != (
                definition.id,
                node.node_type,
                expected_word,
            ):
                raise ContentError("STOP: existing stable node identity differs")
        return {
            "release_status": release.status if release else "ABSENT",
            "active": bool(roadmap and roadmap.active_version_id == version_id(definition)),
            "assets_existing": sum(
                [
                    await session.get(Asset, content_id("asset", a.id)) is not None
                    for a in library.assets
                ]
            ),
        }


def backup(directory):
    url = target()
    destination = directory / "before-hsk0-v4.dump"
    env = {
        **os.environ,
        "PGHOST": url.host,
        "PGPORT": str(url.port or 5432),
        "PGDATABASE": url.database,
        "PGUSER": url.username,
        "PGPASSWORD": url.password,
    }
    if not destination.exists():
        partial = directory / "before-hsk0-v4.partial"
        result = subprocess.run(
            [
                str(PG_BIN / "pg_dump.exe"),
                "--format=custom",
                "--no-password",
                "--file",
                str(partial),
            ],
            env=env,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise ContentError("STOP: local backup failed; no deployment attempted")
        partial.rename(destination)
    check = subprocess.run(
        [str(PG_BIN / "pg_restore.exe"), "--list", str(destination)],
        capture_output=True,
        check=False,
    )
    if check.returncode or destination.stat().st_size == 0:
        raise ContentError("STOP: backup archive inspection failed")
    return {
        "path": str(destination.resolve()),
        "bytes": destination.stat().st_size,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "pg_restore_list_exit": check.returncode,
    }


def schema_check():
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        env={**os.environ, "PGOPTIONS": "-c default_transaction_read_only=on"},
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ContentError("STOP: read-only Alembic schema drift check failed")


def authorized_row_keys(after, definition, library):
    release_id = version_id(definition)
    rows = {table: [] for table in TABLES}
    rows["assets"] = [{"id": str(content_id("asset", a.id))} for a in library.assets]
    rows["assets"] += [{"id": value} for value in after["publication_bundle_asset_ids"]]
    rows["roadmaps"] = [{"id": str(definition.id)}]
    rows["roadmap_versions"] = [{"id": str(release_id)}]
    rows["lesson_templates"] = [{"id": str(TEMPLATE_ID)}]
    rows["lesson_template_versions"] = [{"id": str(TEMPLATE_VERSION_ID)}]
    for node in definition.nodes:
        membership = uuid5(release_id, str(node.id))
        rows["lessons"].append({"id": str(node.id)})
        rows["roadmap_node_identities"].append({"id": str(node.id)})
        rows["lesson_versions"].append({"id": str(uuid5(release_id, f"lesson:{node.id}"))})
        rows["roadmap_nodes"].append({"id": str(membership)})
        rows["roadmap_vocabulary"] += [
            {"node_version_id": str(membership), "vocabulary_id": str(ref.vocabulary_id)}
            for ref in node.lesson.vocabulary
        ]
    return {
        table: {
            hashlib.sha256(
                json.dumps([row[key] for key in after["tables"][table]["keys"]]).encode()
            ).hexdigest()
            for row in values
        }
        for table, values in rows.items()
    }


def preservation(before, after, definition, library):
    if before["target"] != after["target"] or set(before["tables"]) != set(after["tables"]):
        raise ContentError("STOP: database target/schema changed during deployment")
    differences = {}
    authorized = authorized_row_keys(after, definition, library)
    update_tables = {"roadmaps", "roadmap_versions", "lesson_versions", "lesson_template_versions"}
    for table, original in before["tables"].items():
        current = after["tables"][table]
        if original["keys"] != current["keys"]:
            raise ContentError("STOP: table identity columns changed")
        added = set(current["rows"]) - set(original["rows"])
        removed = set(original["rows"]) - set(current["rows"])
        changed = [
            key
            for key in original["rows"].keys() & current["rows"].keys()
            if original["rows"][key] != current["rows"][key]
        ]
        if removed or ((added or changed) and table not in TABLES):
            raise ContentError(f"STOP: unexpected preservation difference in {table}")
        if table in TABLES and (
            not added <= authorized[table]
            or (changed and (table not in update_tables or not set(changed) <= authorized[table]))
        ):
            raise ContentError(
                f"STOP: changes outside the exact approved row identities in {table}"
            )
        if added or changed:
            differences[table] = {
                "inserted": len(added),
                "updated": len(changed),
                "deleted": len(removed),
            }
    return differences


async def deploy(directory, definition, library):
    before = load_json(directory / "before.json")
    current = snapshot(definition)
    preservation(before, current, definition, library)
    state = await database_preflight(definition, library)
    storage = LocalContentStorage(get_settings().content_storage_dir)
    source = LocalContentStorage(SIGNED / "content/objects")
    for asset in library.assets:
        raw = verify_object(source, asset.storage_key, asset.sha256, asset.byte_length)
        if storage.put_bundle(raw) != asset.storage_key:
            raise ContentError("STOP: object staging identity differs")
    async with session_factory() as session:
        await import_library(session, library, storage)
        if state["release_status"] == "PUBLISHED":
            async with session.begin():
                approved, _ = await compile_preview(session, version_id(definition), storage)
                if approved != definition:
                    raise ContentError("STOP: published release content differs")
            if not state["active"]:
                await activate(session, definition.id, version_id(definition))
        else:
            identifier = await import_draft(session, definition)
            async with session.begin():
                await compile_preview(session, identifier, storage)
            await publish(session, identifier, storage, "dxt / HSK0-EDU-REVIEW-20261102")
    after = snapshot(definition)
    write_artifact(directory / "after.json", after)
    differences = preservation(before, after, definition, library)
    write_artifact(
        directory / "deployment.json",
        {
            "target": after["target"],
            "content_sha256": EXPECTED_SHA,
            "roadmap_id": str(definition.id),
            "version_id": str(version_id(definition)),
            "version": 4,
            "approved_media_assets": 6,
            "changes": differences,
            "other_tables_exactly_preserved": True,
            "retry_existing_publication": state["release_status"] == "PUBLISHED",
        },
    )
    print(json.dumps({"deployed_version": str(version_id(definition)), "changes": differences}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument(
        "--apply", action="store_true", help="User-authorized local deployment only"
    )
    args = parser.parse_args()
    try:
        _, definition, library = artifacts()
        target()
        schema_check()
        args.audit_dir.mkdir(parents=True, exist_ok=True)
        with asyncio.Runner(loop_factory=new_event_loop) as runner:
            try:
                state = runner.run(database_preflight(definition, library))
                baseline_path = args.audit_dir / "before.json"
                if not baseline_path.exists():
                    write_artifact(baseline_path, snapshot(definition), immutable=True)
                if args.apply:
                    backup_info = backup(args.audit_dir)
                    write_artifact(args.audit_dir / "backup.json", backup_info, immutable=True)
                    runner.run(deploy(args.audit_dir, definition, library))
                else:
                    print(
                        json.dumps(
                            {
                                "preflight": "PASS",
                                "target": load_json(baseline_path)["target"],
                                "approvals": 17,
                                "content_sha256": EXPECTED_SHA,
                                "existing": state,
                            }
                        )
                    )
            finally:
                runner.run(engine.dispose())
    except (ContentError, ValueError, OSError) as error:
        parser.exit(2, f"deployment stopped: {error}\n")


if __name__ == "__main__":
    main()
