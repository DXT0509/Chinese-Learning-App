import hashlib
import json
import subprocess
import sys

import pytest

from app.services.cedict import DictionaryImportError
from app.services.dictionary_enrichment import load_character_dataset
from app.services.dictionary_revision import artifact_revision, validate_revision
from tests.test_dictionary import FIXTURE

SOURCE_FIXTURE = FIXTURE.parent / "hsk-sino-viet/characters-subset.json"


def character_dataset():
    return load_character_dataset(
        SOURCE_FIXTURE, hashlib.sha256(SOURCE_FIXTURE.read_bytes()).hexdigest()
    )


@pytest.mark.parametrize(
    "revision",
    [
        "your-actual-source-release",
        "example-release",
        "replace-me",
        "PLACEHOLDER",
        "your_release",
    ],
)
def test_placeholder_revision_rejected_before_cli_database_access(revision):
    with pytest.raises(DictionaryImportError, match="placeholder"):
        validate_revision(revision)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.import_dictionary",
            "--file",
            str(FIXTURE),
            "--revision",
            revision,
            "--sha256",
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "--acknowledge-license",
            "CC-BY-SA-4.0",
            "--validate-only",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 1 and "placeholder" in result.stderr


def test_header_revision_and_internal_checksum_fallback(tmp_path):
    path = tmp_path / "source.u8"
    path.write_text("#! date=2026-10-19T20:24:47Z\n#! time=1792441487\n", encoding="utf-8")
    evidence = artifact_revision(path, hashlib.sha256(path.read_bytes()).hexdigest())
    assert evidence["revision"] == "cedict-20261019T202447Z"
    assert evidence["evidence_kind"] == "artifact_header"
    checksum = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    fallback = artifact_revision(FIXTURE, checksum)
    assert fallback["revision"] == "artifact-sha256-" + checksum
    assert fallback["upstream_date"] is None


@pytest.mark.parametrize(
    "header",
    [
        "#! date=not-a-date\n",
        "#! date=2026-10-19T20:24:47Z\n#! time=1\n",
        "#! date=2026-10-19T20:24:47Z\n#! date=2026-10-19T20:24:47Z\n",
    ],
)
def test_inconsistent_acquisition_metadata_is_rejected(tmp_path, header):
    path = tmp_path / "source.u8"
    path.write_text(header, encoding="utf-8")
    with pytest.raises(DictionaryImportError):
        artifact_revision(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_genuine_source_subset_has_character_scope_and_pinned_provenance():
    dataset = character_dataset()
    assert {row.hanzi for row in dataset.records} == {"学", "我"}
    manifest = json.loads((SOURCE_FIXTURE.parent / "manifest.json").read_text())
    assert dataset.sha256 == manifest["subset_sha256"]
    assert manifest["origin_artifact_sha256"] != dataset.sha256
    assert manifest["commit"] == "7cd2805fb0bb46f8e21bda364b857759465f1ce2"


@pytest.mark.parametrize(
    "kind", ["duplicate", "different_reading", "compound", "missing", "variant_collision", "number"]
)
def test_malformed_and_ambiguous_source_records_rejected(tmp_path, kind):
    rows = [row.model_dump() for row in character_dataset().records]
    if kind in ("duplicate", "different_reading"):
        extra = dict(rows[0])
        if kind == "different_reading":
            extra["pinyin"] = "TEST-OTHER-READING"
        rows.append(extra)
    elif kind == "compound":
        rows[0]["hanzi"] = "学生"
    elif kind == "missing":
        rows[0]["meaningVi"] = None
    elif kind == "variant_collision":
        rows[1]["traditional"] = rows[0]["hanzi"]
    else:
        rows[0]["pinyin"] = 123
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(DictionaryImportError):
        load_character_dataset(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_enrichment_checksum_is_required():
    with pytest.raises(DictionaryImportError, match="SHA-256"):
        load_character_dataset(SOURCE_FIXTURE, "0" * 64)
