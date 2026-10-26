"""local-codex-session-v1: explicit development trust, no provider authentication claim."""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid5

from sqlalchemy import func, select, text

from app.core.config import get_settings
from app.models.curated_vocabulary import (
    CuratedVocabulary,
    VocabularyLocalReview,
    VocabularyRevision,
)
from app.services.curated_import import NAMESPACE, digest, load_records, record_checksum

POLICY = "local-codex-session-v1"
HEAD = "0010_local_codex_review"
ASPECTS = {
    "simplified_spelling",
    "mandarin_pinyin_tones",
    "vietnamese_meanings",
    "sino_vietnamese",
    "part_of_speech",
    "example_grammar_naturalness",
    "example_pinyin_translation",
    "learning_level",
    "duplicates_readings_ambiguity",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_checkpoint(root: Path):
    """Revalidate original bytes, complete reviewed copies and actual individual notes.

    Unreviewed batches are never inferred to pass. This is operator-attested evidence,
    not an authenticated API receipt. Unknown model/version/confidence remain unknown.
    """
    root = root.resolve()
    source = root.parent / "original-zhvi"
    coverage = json.loads((source / "coverage-manifest.json").read_text(encoding="utf-8"))
    batches = {b["batch_key"]: b for b in coverage["batches"]}
    accepted, evidence, receipts, excluded = [], {}, [], []
    seen = set()
    for path in sorted(root.glob("L*-B*/review-notes.json")):
        raw = path.read_bytes()
        notes = json.loads(raw)
        batch = batches[notes["batch"]]
        if notes["source_file"] != batch["artifact_file"]:
            raise ValueError("Unexpected source file")
        source_sha, originals = load_records(source / batch["artifact_file"])
        sha, records = load_records(path.parent / "deployment.jsonl")
        if source_sha != notes["source_sha256"] or sha != notes["deployment_sha256"]:
            raise ValueError("Changed source or reviewed bytes")
        if notes["artifact_kind"] != "CODEX_SESSION_LINGUISTIC_NOTES_NOT_REVIEWRESULT":
            raise ValueError("Wrong evidence kind")
        if notes["reviewer_label"] != "Codex session":
            raise ValueError("Unexpected reviewer label")
        timestamp = datetime.fromisoformat(notes["checkpoint_written_at"])
        if timestamp.tzinfo is None:
            raise ValueError("Review time requires timezone")
        findings = {f["lexical_key"]: f for f in notes["records"]}
        original_by_key = {r.lexical_key: r for r in originals}
        if (
            len(findings) != len(notes["records"])
            or set(findings) != set(original_by_key)
            or {r.lexical_key for r in records} != set(findings)
        ):
            raise ValueError("Incomplete or duplicate batch review")
        receipts.append({"batch": notes["batch"], "notes_sha256": digest(raw), "data_sha256": sha})
        for record in records:
            key = record.lexical_key
            finding = findings[key]
            original = original_by_key[key]
            if key in seen:
                raise ValueError("Duplicate lexical identity across checkpoints")
            seen.add(key)
            if record != original and record.content_version <= original.content_version:
                raise ValueError("Changed draft requires a higher content version")
            if (
                finding["source_checksum"] != record_checksum(original)
                or finding["source_content_version"] != original.content_version
                or finding["reviewed_checksum"] != record_checksum(record)
                or finding["reviewed_content_version"] != record.content_version
                or finding["id"] != str(uuid5(NAMESPACE, key))
                or set(finding["checked_aspects"]) != ASPECTS
                or not finding["note"].strip()
            ):
                raise ValueError("Stale or incomplete individual review")
            if finding["linguistic_outcome"] not in {"PASS", "CORRECTED_PASS", "UNCERTAIN"}:
                raise ValueError("Unknown linguistic decision")
            if (
                finding["linguistic_outcome"] == "UNCERTAIN"
                or finding["pending_reason"]
                or not finding["local_development_candidate"]
                or original.review_status == "NEEDS_REVIEW"
                or record.review_status == "NEEDS_REVIEW"
                or not record.examples
            ):
                excluded.append(
                    {"lexical_key": key, "reason": finding["pending_reason"] or "Not accepted"}
                )
                continue
            accepted.append(record)
            evidence[key] = {
                "policy": POLICY,
                "authentication": "LOCAL_OPERATOR_ATTESTED_SESSION_NOTES",
                "reviewer_label": notes["reviewer_label"],
                "reviewer_model": notes["reviewer_model"],
                "reviewer_version": notes["reviewer_version"],
                "checkpoint_written_at": notes["checkpoint_written_at"],
                "source_sha256": source_sha,
                "batch": notes["batch"],
                "notes_sha256": digest(raw),
                "record": finding,
            }
    if not accepted:
        raise ValueError("No recorded passing reviews")
    return (
        accepted,
        evidence,
        {
            "policy": POLICY,
            "reviewed": len(seen),
            "accepted": len(accepted),
            "unreviewed": sum(b["records_count"] for b in batches.values()) - len(seen),
            "excluded": excluded,
            "receipts": receipts,
        },
    )


async def preview(session, records, evidence, coverage):
    """Caller uses a read-only transaction for plan; apply reruns under import lock."""
    identity = (
        await session.execute(
            text(
                "SELECT current_database(), inet_server_addr()::text, inet_server_port(), current_user"
            )
        )
    ).one()
    revisions = list(await session.scalars(text("SELECT version_num FROM alembic_version")))
    words = {w.lexical_key: w for w in await session.scalars(select(CuratedVocabulary))}
    changes = []
    for record in records:
        word = words.get(record.lexical_key)
        checksum = record_checksum(record)
        before = (
            None
            if word is None
            else {
                "version": word.content_version,
                "checksum": word.checksum,
                "status": word.review_status,
            }
        )
        if word is None:
            action = "INSERT_AND_ACCEPT_LOCAL"
        elif word.review_status in {"NEEDS_REVIEW", "REJECTED"}:
            action = "PRESERVE_HOLD"
        elif word.checksum != checksum and record.content_version <= word.content_version:
            action = "VERSION_CONFLICT"
        elif word.review_status in {"HUMAN_APPROVED", "AI_APPROVED"}:
            action = (
                "PRESERVE_APPROVAL" if word.checksum == checksum else "APPROVED_CONTENT_CONFLICT"
            )
        else:
            action = "ACCEPT_LOCAL" if word.checksum == checksum else "REVISE_AND_ACCEPT_LOCAL"
        changes.append(
            {
                "lexical_key": record.lexical_key,
                "before": before,
                "action": action,
                "incoming_version": record.content_version,
                "incoming_checksum": checksum,
                "evidence_checksum": digest(canonical(evidence[record.lexical_key])),
            }
        )
    plan = {
        "database": list(identity),
        "migrations": sorted(revisions),
        "coverage": coverage,
        "changes": changes,
        "policy": POLICY,
    }
    plan["confirmation"] = "LOCAL-CODEX-" + digest(canonical(plan))
    return plan


async def accept_local(session, records, evidence, operator):
    settings = get_settings()
    if settings.environment != "development" or not settings.allow_local_codex_reviewed_vocabulary:
        raise ValueError("Explicit development enablement required")
    if not operator.strip():
        raise ValueError("Named local operator required")
    async with session.begin():
        await session.execute(select(func.pg_advisory_xact_lock(740001)))
        for record in records:
            receipt = evidence[record.lexical_key]
            finding = receipt["record"]
            if (
                receipt["policy"] != POLICY
                or receipt["authentication"] != "LOCAL_OPERATOR_ATTESTED_SESSION_NOTES"
                or receipt["reviewer_label"] != "Codex session"
                or finding["lexical_key"] != record.lexical_key
                or finding["reviewed_content_version"] != record.content_version
                or finding["reviewed_checksum"] != record_checksum(record)
                or finding["linguistic_outcome"] not in {"PASS", "CORRECTED_PASS"}
                or not finding["local_development_candidate"]
                or finding["pending_reason"]
                or set(finding["checked_aspects"]) != ASPECTS
                or not finding["note"].strip()
                or record.review_status == "NEEDS_REVIEW"
                or not record.examples
            ):
                raise ValueError("Incomplete or nonpassing local evidence")
            identifier = uuid5(NAMESPACE, record.lexical_key)
            word = await session.get(CuratedVocabulary, identifier, with_for_update=True)
            checksum = record_checksum(record)
            revision = await session.get(VocabularyRevision, (identifier, record.content_version))
            if (
                word is None
                or word.checksum != checksum
                or word.content_version != record.content_version
                or revision is None
                or revision.checksum != checksum
                or record_checksum(type(record).model_validate(revision.payload)) != checksum
            ):
                raise ValueError("Current content no longer matches reviewed revision")
            if word.review_status in {"NEEDS_REVIEW", "REJECTED", "HUMAN_APPROVED", "AI_APPROVED"}:
                raise ValueError("Existing editorial decision cannot be overwritten")
            receipt_sha = digest(canonical(receipt))
            review_id = uuid5(NAMESPACE, POLICY + identifier.hex + checksum + receipt_sha)
            previous = await session.get(VocabularyLocalReview, review_id)
            if previous is None:
                session.add(
                    VocabularyLocalReview(
                        id=review_id,
                        vocabulary_id=identifier,
                        content_version=record.content_version,
                        checksum=checksum,
                        evidence_checksum=receipt_sha,
                        evidence=receipt,
                        submitted_by=operator,
                    )
                )
            elif previous.evidence_checksum != receipt_sha:
                raise ValueError("Receipt identity mismatch")
            word.review_status = "LOCAL_CODEX_REVIEWED"
