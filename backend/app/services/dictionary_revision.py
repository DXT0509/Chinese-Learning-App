"""Artifact-grounded revision labels; no guessed upstream release dates."""

import gzip
import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from app.services.cedict import DictionaryImportError


def validate_revision(revision: str) -> str:
    tokens = re.split(r"[-_.]", revision.lower())
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", revision) or {
        "your",
        "example",
        "placeholder",
        "replace",
    }.intersection(tokens):
        raise DictionaryImportError(
            "Invalid or placeholder source revision; omit --revision to derive it"
        )
    return revision


def artifact_revision(path: Path, expected_sha256: str) -> dict:
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or actual != expected_sha256:
        raise DictionaryImportError("Source SHA-256 mismatch")
    if path.suffix == ".gz":
        payload = gzip.decompress(payload)
    headers = {}
    for line in payload.decode("utf-8-sig").splitlines():
        if line.startswith("#! ") and "=" in line:
            key, value = line[3:].split("=", 1)
            if key in headers:
                raise DictionaryImportError("Ambiguous artifact metadata")
            headers[key] = value
    date = headers.get("date")
    if date:
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            if "time" in headers and int(headers["time"]) != int(timestamp.timestamp()):
                raise ValueError("Inconsistent timestamp")
        except ValueError:
            raise DictionaryImportError("Invalid or inconsistent artifact date") from None
        return {
            "revision": "cedict-" + timestamp.strftime("%Y%m%dT%H%M%SZ"),
            "evidence_kind": "artifact_header",
            "upstream_date": date,
            "sha256": actual,
        }
    return {
        "revision": "artifact-sha256-" + actual,
        "evidence_kind": "artifact_sha256",
        "upstream_date": None,
        "sha256": actual,
    }
