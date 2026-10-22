import gzip
import hashlib
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.dependencies.authentication import current_user_id
from app.main import create_app
from app.schemas.dictionary import DictionaryQuery
from app.services.cedict import DictionaryImportError, load_dataset, parse_row, tone_marks

FIXTURE = Path(__file__).parent / "fixtures/dictionary/cedict-test.u8"


def fixture_dataset():
    return load_dataset(FIXTURE, hashlib.sha256(FIXTURE.read_bytes()).hexdigest())


@pytest.mark.parametrize(
    "numbered,marked",
    [
        ("ni3 hao3", "nǐ hǎo"),
        ("nu:3", "nǚ"),
        ("liu2 gui4", "liú guì"),
        ("ou3", "ǒu"),
        ("ma5", "ma"),
        ("Lu:4", "Lǜ"),
        ("m2 n3", "ḿ ň"),
    ],
)
def test_tone_rendering(numbered, marked):
    assert tone_marks(numbered) == marked


def test_stable_identity_preserves_readings_forms_case_and_updates():
    entry = parse_row("行 行 [xing2] /test one/test two/")
    assert entry.id == parse_row("行 行 [xing2] /changed gloss/").id
    assert entry.id != parse_row("行 行 [hang2] /test one/").id
    assert entry.id != parse_row("行 行 [Xing2] /test one/").id
    assert entry.english_glosses == ["test one", "test two"]
    assert len(fixture_dataset().entries) == 10


def test_normalizes_unicode_and_spacing():
    first = parse_row("女 女 [nu:3] /cafe\u0301/")
    second = parse_row("女 女 [nu:3] /café/")
    assert first == second
    assert DictionaryQuery(q="  学生  ").q == "学生"


def test_duplicate_rows_and_gzip(tmp_path):
    path = tmp_path / "source.gz"
    row = "你 你 [ni3] /test/\n"
    path.write_bytes(gzip.compress((row + row).encode()))
    result = load_dataset(path, hashlib.sha256(path.read_bytes()).hexdigest())
    assert len(result.entries) == 1 and result.duplicate_rows == 1


@pytest.mark.parametrize(
    "rows",
    [
        "broken",
        "你 你 [[ni3]] /v2/",
        "你 你 [ni3] //",
        "你 你 [ni3] /one//two/",
        "你 你 [ni3] /one/\n你 你 [ni3] /different/",
        "# no rows\n",
    ],
)
def test_malformed_or_conflicting_rows_fail_closed(tmp_path, rows):
    path = tmp_path / "source.u8"
    path.write_text(rows, encoding="utf-8")
    with pytest.raises(DictionaryImportError):
        load_dataset(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_checksum_rejected():
    with pytest.raises(DictionaryImportError, match="SHA-256 mismatch"):
        load_dataset(FIXTURE, "0" * 64)


@pytest.mark.parametrize(
    "data",
    [
        {"q": ""},
        {"q": "   "},
        {"q": "你" * 65},
        {"q": "你\x00"},
        {"q": "学\u200b"},
        {"q": "你", "limit": 51},
        {"q": "你", "limit": 0},
        {"q": "你", "offset": 1001},
        {"q": "你", "offset": -1},
    ],
)
def test_query_validation(data):
    with pytest.raises(ValidationError):
        DictionaryQuery(**data)


def test_http_authentication_and_validation():
    app = create_app()
    with TestClient(app) as client:
        for path in ("/search?q=你", f"/entries/{uuid4()}"):
            assert client.get("/api/v1/dictionary" + path).status_code == 401
        app.dependency_overrides[current_user_id] = lambda: uuid4()
        for params in ({}, {"q": " "}, {"q": "你" * 65}, {"q": "你", "limit": 51}):
            response = client.get("/api/v1/dictionary/search", params=params)
            assert response.status_code == 422
            assert response.json() == {"detail": "Invalid request"}
        assert client.get("/api/v1/dictionary/entries/invalid").status_code == 422


def test_cli_validation_without_database():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.import_dictionary",
            "--file",
            str(FIXTURE),
            "--sha256",
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "--revision",
            "synthetic-test-v1",
            "--acknowledge-license",
            "CC-BY-SA-4.0",
            "--validate-only",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0
    assert '"entries": 10' in result.stdout
