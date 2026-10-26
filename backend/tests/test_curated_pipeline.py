"""Synthetic provider fixtures are NEVER genuine evidence or live API calls."""

import json
from pathlib import Path

import pytest

from app.schemas.curated_review import ASPECTS, ModelIdentity
from app.services.curated_audit import scan_dataset
from app.services.curated_bulk import import_batches, plan_token
from app.services.curated_import import digest, load_records
from app.services.curated_review import review_inputs
from app.services.curated_reviewer import (
    AnthropicReviewer,
    independent,
    load_run,
    normalize_response,
    run_reviews,
    safe_correction,
    verified_generators,
    write_new,
)
from tests.test_curated_vocabulary import curated_sessions, record  # noqa: F401

ROOT = Path(__file__).resolve().parents[2] / "docs/datasets/original-zhvi"
GENERATOR = ModelIdentity(provider="synthetic", model="generator-fixture", version="test")


class SyntheticReviewer:
    def __init__(self, answer=None, model="reviewer-fixture"):
        self.identity = ModelIdentity(provider="anthropic", model=model, version=model)
        self.calls = 0
        self.answer = answer

    def __call__(self, request, max_tokens):
        self.calls += 1
        answer = self.answer or {
            "decision": "AI_APPROVED",
            "confidence": 0.99,
            "assessments": [
                {"aspect": a, "result": "pass", "rationale": "Synthetic unit fixture"}
                for a in ASPECTS
            ],
            "findings": [],
            "suggested_record": None,
        }
        if callable(answer):
            answer = answer(request)
        return {
            "type": "message",
            "role": "assistant",
            "model": self.identity.model,
            "id": f"synthetic-test-only-{self.identity.model}-{self.calls}",
            "stop_reason": "end_turn",
            "content": [{"type": "text", "text": json.dumps(answer)}],
            "usage": {"input_tokens": 100, "output_tokens": 100},
        }


def request_for_review():
    r = record(examples=[{"simplified": "学", "pinyin": "xué", "vietnamese": "học"}])
    return review_inputs([r], GENERATOR)[0]


@pytest.fixture(scope="module")
def dataset_audit():
    return scan_dataset(ROOT)


def test_all_50_batches(dataset_audit):
    audit, rows = dataset_audit
    assert audit["structural_integrity"] == "PASSED"
    assert len(audit["files"]) == 50 and len(rows) == 2501
    assert audit["unique_learning_items"] == 2500
    assert audit["by_learning_level"] == {
        "0": 100,
        "1": 100,
        "2": 150,
        "3": 300,
        "4": 600,
        "5": 1250,
    }
    assert audit["missing_content"] == ["谁|shui2"]
    assert len(audit["editorial_holds"]) == 5
    assert audit["stages"]["PUBLISHED"] is None
    assert all(
        p["status"] == "UNVERIFIED_MANIFEST_ASSERTION" for p in audit["generator_provenance"]
    )
    assert audit["duplicate_candidates"]


def test_global_duplicates_and_bad_registry(tmp_path, monkeypatch):
    # Point a cloned manifest set to a repeated valid source; count/level/registry checks fail.
    import shutil

    for f in ROOT.glob("*.json*"):
        shutil.copyfile(f, tmp_path / f.name)
    coverage_path = tmp_path / "coverage-manifest.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    coverage["batches"][1] = coverage["batches"][0]
    coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
    audit, _ = scan_dataset(tmp_path)
    assert audit["structural_integrity"] == "FAILED"
    assert audit["duplicate_keys"] and audit["duplicate_identities"]
    assert any(isinstance(e, dict) and "registry_mismatch" in e for e in audit["errors"])


def test_source_tamper(tmp_path):
    import shutil

    for f in ROOT.glob("*.json*"):
        shutil.copyfile(f, tmp_path / f.name)
    with (tmp_path / "level-1-batch-001.jsonl").open("ab") as stream:
        stream.write(b"\n")
    audit, _ = scan_dataset(tmp_path)
    assert audit["structural_integrity"] == "FAILED"
    assert any(
        isinstance(e, dict) and "hash mismatch" in e.get("reason", "") for e in audit["errors"]
    )


def test_requires_real_configuration(monkeypatch):
    monkeypatch.delenv("VOCAB_REVIEW_PROVIDER", raising=False)
    with pytest.raises(ValueError, match="Explicit"):
        AnthropicReviewer()
    monkeypatch.setenv("VOCAB_REVIEW_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="unavailable"):
        AnthropicReviewer()


def test_unverified_generator_is_blocked(tmp_path, dataset_audit):
    audit, _ = dataset_audit
    write_new(tmp_path / "ledger.json", {"operator": "test", "batches": {}})
    with pytest.raises(KeyError):
        verified_generators(ROOT, audit, tmp_path / "ledger.json")


def test_provenance_requires_exact_artifact_and_evidence(tmp_path):
    receipt = tmp_path / "generation.json"
    receipt.write_text('{"fixture":true}', encoding="utf-8")
    entry = {
        "artifact_sha256": "a" * 64,
        "generator": GENERATOR.model_dump(),
        "evidence_file": receipt.name,
        "evidence_sha256": digest(receipt.read_bytes()),
        "verification_note": "SYNTHETIC TEST ONLY",
    }
    ledger = tmp_path / "ledger.json"
    write_new(ledger, {"operator": "test", "batches": {"b": entry}})
    audit = {"files": [{"batch": "b", "sha256": "a" * 64}]}
    assert verified_generators(ROOT, audit, ledger)["b"] == GENERATOR
    receipt.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        verified_generators(ROOT, audit, ledger)


def test_resume_no_repeat_paid_call(tmp_path):
    provider = SyntheticReviewer()
    request = request_for_review()
    for _ in range(2):
        counts = run_reviews(
            [request], tmp_path, provider, max_calls=1, max_tokens=4000, attempts=2
        )
        assert counts["AI_APPROVED"] == 1
    assert provider.calls == 1
    assert len(load_run(tmp_path)) == 1
    # Standalone forged/edited result cannot replace the provider receipt.
    result_path = next(tmp_path.glob("*.result.json"))
    result_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="evidence changed"):
        run_reviews([request], tmp_path, provider, max_calls=1, max_tokens=4000, attempts=2)
    assert len(load_run(tmp_path)) == 1


@pytest.mark.parametrize(
    "mode", ["invalid_json", "incomplete", "different_model", "low_confidence"]
)
def test_invalid_responses_never_approve(tmp_path, mode):
    provider = SyntheticReviewer()
    request = request_for_review()
    raw = provider(request, 100)
    if mode == "invalid_json":
        raw["content"][0]["text"] = "not-json"
    elif mode == "incomplete":
        raw["stop_reason"] = "max_tokens"
    elif mode == "different_model":
        raw["model"] = "unconfigured"
    else:
        answer = json.loads(raw["content"][0]["text"])
        answer["confidence"] = 0.94
        raw["content"][0]["text"] = json.dumps(answer)
    from datetime import UTC, datetime

    with pytest.raises(ValueError):
        normalize_response(raw, request, provider.identity, datetime.now(UTC).isoformat())


def test_independence_and_safe_versions():
    same = GENERATOR.model_copy(update={"version": "different"})
    with pytest.raises(ValueError, match="Independent"):
        independent(GENERATOR, same)
    original = request_for_review().content
    with pytest.raises(ValueError, match="increment"):
        safe_correction(original, original)
    changed = original.model_copy(update={"content_version": 2})
    assert safe_correction(original, changed).content_version == 2
    with pytest.raises(ValueError, match="Identity"):
        safe_correction(
            original,
            changed.model_copy(
                update={
                    "lexical_key": "学习|xue2 xi2",
                    "simplified": "学习",
                    "pinyin": "xué xí",
                    "pinyin_numbered": "xue2 xi2",
                }
            ),
        )


def test_correction_requires_another_model(tmp_path):
    def needs_fix(request):
        return {
            "decision": "NEEDS_REVIEW",
            "confidence": 0.8,
            "assessments": [
                {"aspect": a, "result": "uncertain", "rationale": "Synthetic"} for a in ASPECTS
            ],
            "findings": [
                {
                    "aspect": "vietnamese_definitions",
                    "severity": "blocking",
                    "message": "Synthetic correction",
                    "resolved": False,
                }
            ],
            "suggested_record": request.content.model_copy(
                update={"content_version": request.content.content_version + 1}
            ).model_dump(),
        }

    first = SyntheticReviewer(needs_fix)
    second = SyntheticReviewer(model="independent-correction-fixture")
    counts = run_reviews(
        [request_for_review()],
        tmp_path,
        first,
        max_calls=2,
        max_tokens=4000,
        attempts=2,
        correction_reviewer=second,
    )
    assert counts["AI_APPROVED"] == 1
    evidence = load_run(tmp_path)
    assert len(evidence) == 2
    corrected = next(r for r, _ in evidence if r.content.content_version == 2)
    assert corrected.generator == first.identity
    assert corrected.content_checksum != request_for_review().content_checksum


def test_interrupted_network_reservation_is_not_retried(tmp_path):
    class Interrupted(SyntheticReviewer):
        def __call__(self, request, max_tokens):
            self.calls += 1
            raise TimeoutError()

    provider = Interrupted()
    for _ in range(2):
        counts = run_reviews(
            [request_for_review()], tmp_path, provider, max_calls=2, max_tokens=100, attempts=2
        )
        assert counts["unresolved"] == 1
    assert provider.calls == 1
    assert load_run(tmp_path) == []


def test_invalid_response_retry_and_budget_limit(tmp_path):
    provider = SyntheticReviewer(answer={"invalid": "fixture"})
    counts = run_reviews(
        [request_for_review()], tmp_path, provider, max_calls=1, max_tokens=100, attempts=3
    )
    assert counts["unresolved"] == 1 and provider.calls == 1
    assert load_run(tmp_path) == []


async def test_bulk_import_interruption_recovery_and_drift(curated_sessions, tmp_path):  # noqa: F811
    from sqlalchemy import func, select

    from app.models.curated_vocabulary import CuratedVocabulary

    rows = [
        record(),
        record(simplified="习", lexical_key="习|xi2", pinyin="xí", pinyin_numbered="xi2"),
    ]
    files = []
    for n, row in enumerate(rows):
        path = tmp_path / f"batch{n}.jsonl"
        path.write_text(row.model_dump_json() + "\n", encoding="utf-8")
        sha, _ = load_records(path)
        files.append({"batch": f"B{n}", "file": path.name, "sha256": sha})
    audit = {"files": files, "stages": {"GENERATED": 2}}

    def interruption(batch, result):
        raise RuntimeError("Simulated interruption after commit")

    with pytest.raises(RuntimeError):
        await import_batches(curated_sessions, tmp_path, audit, interruption)
    committed = []
    await import_batches(curated_sessions, tmp_path, audit, lambda b, r: committed.append(r))
    assert committed[0]["unchanged_batch"] and not committed[1]["unchanged_batch"]
    async with curated_sessions() as session:
        assert await session.scalar(select(func.count()).select_from(CuratedVocabulary)) == 2
    await import_batches(curated_sessions, tmp_path, audit, lambda b, r: None)
    (tmp_path / "batch0.jsonl").write_text(
        rows[0].model_copy(update={"content_version": 2}).model_dump_json(), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="changed after audit"):
        await import_batches(curated_sessions, tmp_path, audit, lambda b, r: None)


def test_confirmation_bound_to_database_and_plan():
    audit = {"files": [{"sha256": "a" * 64}]}
    plan = {"identity": {"database": "isolated"}, "actions": ["INSERT"]}
    token = plan_token(plan, audit)
    assert token != plan_token({**plan, "identity": {"database": "development"}}, audit)
    assert token != plan_token({**plan, "actions": ["NEW_REVISION"]}, audit)


def test_input_checksum_mismatch_is_rejected():
    from datetime import UTC, datetime

    provider = SyntheticReviewer()
    request = request_for_review().model_copy(update={"content_checksum": "f" * 64})
    with pytest.raises(ValueError, match="checksum"):
        normalize_response(
            provider(request, 100), request, provider.identity, datetime.now(UTC).isoformat()
        )


async def test_existing_receipt_cannot_hide_catalog_drift(curated_sessions, tmp_path):  # noqa: F811
    from sqlalchemy import update

    from app.models.curated_vocabulary import CuratedVocabulary

    row = request_for_review().content
    path = tmp_path / "batch.jsonl"
    path.write_text(row.model_dump_json(), encoding="utf-8")
    sha, _ = load_records(path)
    audit = {"files": [{"batch": "drift", "file": path.name, "sha256": sha}]}
    await import_batches(curated_sessions, tmp_path, audit, lambda b, r: None)
    async with curated_sessions() as session, session.begin():
        await session.execute(update(CuratedVocabulary).values(checksum="f" * 64))
    with pytest.raises(ValueError, match="receipt"):
        await import_batches(curated_sessions, tmp_path, audit, lambda b, r: None)
