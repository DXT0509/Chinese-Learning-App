"""The operational wrapper cannot widen target or preservation scope."""

import copy
from types import SimpleNamespace

import pytest

from app.services.content_files import ContentError
from scripts import deploy_hsk0_v4 as deployment


@pytest.mark.parametrize(
    "environment,url",
    [
        ("production", "postgresql+psycopg://test@127.0.0.1:5432/chinese_learning"),
        ("development", "postgresql+psycopg://test@db.example.com:5432/chinese_learning"),
        ("development", "postgresql+psycopg://test@127.0.0.1:5433/chinese_learning"),
        ("development", "postgresql+psycopg://test@127.0.0.1:5432/other_database"),
    ],
)
def test_target_mismatch_is_rejected_before_connection(monkeypatch, environment, url):
    monkeypatch.setattr(
        deployment,
        "get_settings",
        lambda: SimpleNamespace(environment=environment, database_url=url),
    )
    with pytest.raises(ContentError, match="authorized local development"):
        deployment.target()


def baseline():
    return {
        "target": {"database": "synthetic"},
        "publication_bundle_asset_ids": [],
        "tables": {
            **{
                table: {
                    "keys": ["node_version_id", "vocabulary_id"]
                    if table == "roadmap_vocabulary"
                    else ["id"],
                    "rows": {},
                    "count": 0,
                }
                for table in deployment.TABLES
            },
            "users": {"keys": ["id"], "rows": {"existing-user": "original"}, "count": 1},
        },
    }


@pytest.mark.parametrize("mutation", ["learner", "unrelated_asset", "delete", "schema"])
def test_unrelated_changes_fail_preservation(mutation):
    _, definition, library = deployment.artifacts()
    before = baseline()
    after = copy.deepcopy(before)
    if mutation == "learner":
        after["tables"]["users"]["rows"]["existing-user"] = "changed"
    elif mutation == "delete":
        after["tables"]["users"]["rows"] = {}
    elif mutation == "schema":
        after["tables"]["users"]["keys"] = ["other"]
    else:
        after["tables"]["assets"]["rows"]["unrelated"] = "inserted"
    with pytest.raises(ContentError, match="STOP"):
        deployment.preservation(before, after, definition, library)


def test_exact_asset_insert_and_idempotent_retry_are_allowed():
    _, definition, library = deployment.artifacts()
    before = baseline()
    after = copy.deepcopy(before)
    key = next(iter(deployment.authorized_row_keys(after, definition, library)["assets"]))
    after["tables"]["assets"]["rows"][key] = "approved-source-bytes"
    assert deployment.preservation(before, after, definition, library) == {
        "assets": {"inserted": 1, "updated": 0, "deleted": 0}
    }
    assert deployment.preservation(after, after, definition, library) == {}
