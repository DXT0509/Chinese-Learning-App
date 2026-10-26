"""Fail-closed checks that never need or connect to a database."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.services import vocabulary_reset as reset


@pytest.mark.parametrize(
    "failure", ["token", "identity", "missing", "modified", "expired", "drift"]
)
async def test_apply_refuses_invalid_evidence_before_deletion(tmp_path, monkeypatch, failure):
    backup = tmp_path / "backup.dump"
    backup.write_bytes(b"synthetic backup fixture")
    identity = {"database": "test", "host": "127.0.0.1", "port": 55440}
    report = {
        "created_at": datetime.now(UTC).isoformat(),
        "identity": identity,
        "inventory": {"clear": {"vocabulary": 1}},
        "backup": {
            "path": str(backup),
            "size": backup.stat().st_size,
            "sha256": reset.file_checksum(backup),
        },
    }
    if failure == "expired":
        report["created_at"] = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    report["confirmation"] = reset.fingerprint(report)
    token = report["confirmation"]
    if failure == "token":
        token = "not-confirmed"
    if failure == "identity":
        identity = {**identity, "database": "other"}
    if failure == "missing":
        backup.unlink()
    if failure == "modified":
        backup.write_bytes(b"changed backup")

    async def changed_inventory(connection):
        return {"clear": {"vocabulary": 2}}

    monkeypatch.setattr(reset, "inventory", changed_inventory)
    # None would fail immediately if deletion attempted to execute SQL.
    with pytest.raises(ValueError):
        await reset.execute_reset(None, report, token, identity)


async def test_backup_failure_stops_report_generation(tmp_path, monkeypatch):
    identity = {"database": "test", "host": "127.0.0.1", "port": 55440}
    settings = Settings(database_url="postgresql+psycopg://test@127.0.0.1:55440/test")

    async def fake_inventory(connection):
        return {"server": identity}

    class Connection:
        async def scalar(self, statement):
            return "synthetic-snapshot"

    monkeypatch.setattr(reset, "inventory", fake_inventory)
    monkeypatch.setattr(reset.shutil, "which", lambda executable: "pg_dump")
    monkeypatch.setattr(reset.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=1))
    with pytest.raises(ValueError, match="Backup failed"):
        await reset.prepare(Connection(), settings, identity, tmp_path)
