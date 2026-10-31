"""Additive catalog policy preparation; existing immutable policies always win.

Do not turn dictionary structural labels (idiom/phrase) into invented POS.
Vietnamese examples are context cues, never answer synonyms or new readings.
"""

import re
from collections import Counter, defaultdict

from app.schemas.curated_vocabulary import is_hanzi
from app.services.policy_preparation import normalized, prepare
from app.services.review_grading import POS_OPTIONS
from app.services.review_targets import ReviewedPolicy

GENERATOR = "catalog-context-v2"
GENERATORS = {"catalog-cued-v1", GENERATOR}


def catalog_pos(value):
    """Normalize explicit subtypes; retain every supported source category.

    time/locality/word element qualify a supplied category, not extra POS.
    A bare structural label still needs editorial investigation.
    """
    aliases = {"measure word": "classifier", "proper noun": "noun", "modal verb": "verb"}
    tokens = re.split(r"\s*[;,/|]\s*", normalized(value))
    categories = {aliases.get(token, token) for token in tokens}
    qualifiers = {"time", "locality", "word element"}
    supported = categories & set(POS_OPTIONS)
    unknown = categories - set(POS_OPTIONS) - qualifiers
    if unknown or not supported:
        return [], sorted(unknown or categories)
    return [pos for pos in POS_OPTIONS if pos in supported], []


def safe_text(value):
    return (
        bool(normalized(value))
        and any(c.isalpha() for c in value)
        and not any(is_hanzi(c) for c in value)
    )


def usable_cue(entry):
    cue = normalized(entry.word.sino_vietnamese)
    return (
        cue
        if (
            re.fullmatch(r"[^\W\d_]+(?: [^\W\d_]+)*", cue)
            and len(cue.split()) == len(entry.word.simplified)
            and safe_text(cue)
        )
        else None
    )


def prepare_coverage(entries, existing=(), *, installed_keys=None, only_ids=None):
    """Extend v1 without replacing any installed policy or publication decision.

    Missing Hán-Việt is not missing linguistic meaning. Require a usable source
    example instead, and compare every source gloss against all answer candidates.
    """
    existing = list(existing)
    preserved = {}
    for policy in existing:
        key = (policy.vocabulary_id, policy.content_version, policy.checksum)
        if key in preserved and preserved[key] != policy:
            raise ValueError("Conflicting preserved policies")
        preserved[key] = policy
    policies, baseline = prepare(
        entries, [p for p in existing if p.policy_version != GENERATOR], only_ids=only_ids
    )
    by_id = {entry.word.id: entry for entry in entries}
    by_string_id = {str(entry.word.id): entry for entry in entries}
    policies = {p.vocabulary_id: p for p in policies}
    forms = defaultdict(set)
    cue_groups = defaultdict(list)
    length_groups = defaultdict(list)
    for entry in entries:
        forms[entry.word.simplified].add(entry.word.id)
        cue_groups[(usable_cue(entry), len(entry.word.simplified))].append(entry)
        length_groups[len(entry.word.simplified)].append(entry)
    rows = []
    for original in baseline["records"]:
        row = dict(original)
        entry = by_string_id[row["vocabulary_id"]]
        word = entry.word
        key = (word.id, word.content_version, word.checksum)
        row["learning_level"] = word.learning_level
        row["vietnamese_examples"] = entry.examples
        row["baseline_reasons"] = row.pop("reasons")
        row["installed"] = False
        # Never rewrite an existing payload, even a generated one.
        if entry.published and key in preserved and preserved[key].policy_version != GENERATOR:
            policy = preserved[key]
            try:
                policy.target(word)
                # v1 must still pass current-catalog safety checks.
                if policy.policy_version == "catalog-cued-v1" and word.id not in policies:
                    raise ValueError("Current catalog invalidates v1")
                policies[word.id] = policy
                row["installed"] = True
            except ValueError:
                policies.pop(word.id, None)
                row["binding_error"] = "INVALID_OR_STALE_INSTALLED_POLICY"
        reasons = []
        if row.get("binding_error"):
            reasons.append("POLICY_REQUIRES_NEW_CONTENT_VERSION")
        if not entry.published:
            reasons.append("PUBLICATION_EXCLUDED")
        if word.id not in policies and entry.published:
            pos, unknown = catalog_pos(word.part_of_speech)
            if not pos:
                reasons.append("MISSING_POS" if not word.part_of_speech else "POS_EDITORIAL_REVIEW")
            if not entry.meanings or not all(safe_text(g) for g in entry.meanings):
                reasons.append("PROMPT_EDITORIAL_REVIEW")
            cue = usable_cue(entry)
            contexts = [example for example in entry.examples if safe_text(example)]
            if not cue and not contexts:
                reasons.append("CONTEXT_EDITORIAL_REVIEW")
            if len(forms[word.simplified]) > 1:
                reasons.append("PRONUNCIATION_EDITORIAL_REVIEW")
            # Shared cues are usable only if meanings distinguish every peer.
            # Check any overlapping gloss, not just the complete gloss tuple.
            length = len(word.simplified)
            candidates = (
                cue_groups[(cue, length)] + cue_groups[(None, length)]
                if cue
                else length_groups[length]
            )
            peers = [e for e in candidates if e.word.id != word.id]
            conflicting = [
                e
                for e in peers
                if {normalized(g) for g in e.meanings} & {normalized(g) for g in entry.meanings}
            ]
            row["conflicting_candidates"] = sorted(e.word.lexical_key for e in conflicting)
            if conflicting:
                reasons.append("ANSWER_CONFLICT_EDITORIAL_REVIEW")
            if not reasons:
                payload = {
                    "vocabulary_id": word.id,
                    "content_version": word.content_version,
                    "checksum": word.checksum,
                    "policy_version": GENERATOR,
                    "sense_key": "whole-lexeme-all-source-pos",
                    "vietnamese_prompt": (
                        f"Viết mục từ đã học ({len(word.simplified)} chữ Hán). "
                        + (f"Âm Hán-Việt «{word.sino_vietnamese}». " if cue else "")
                        + "Nghĩa trong danh mục: "
                        + "; ".join(entry.meanings)
                        + ". "
                        + ("Ngữ cảnh minh họa: " + contexts[0] + " " if contexts else "")
                        + "Ở bước từ loại, chọn tất cả từ loại của mục từ này trong danh mục."
                    ),
                    "reviewed_by": "Deterministic catalog preparation: " + GENERATOR,
                    "ambiguity_resolution": (
                        "Whole lexeme, all source glosses and all explicitly supported source POS; "
                        "source Vietnamese example required when Hán-Việt is unavailable. "
                        "no positional sense alignment. Shared cues checked with character count "
                        "and overlapping glosses across all entries including holds. Source POS "
                        "subtypes normalized; no new lexical category or pronunciation inferred. "
                        "Automated preparation, not human semantic certification."
                    ),
                    "accepted_pos": pos,
                }
                try:
                    policy = ReviewedPolicy.model_validate(payload)
                    policy.target(word)
                    policies[word.id] = policy
                except ValueError:
                    reasons.append("INVALID_LEXICAL_IDENTITY_OR_PROMPT")
            row["unsupported_pos_labels"] = unknown
        row["reasons"] = reasons
        if key in preserved and preserved[key].policy_version == GENERATOR:
            row["installed"] = policies.get(word.id) == preserved[key]
            if not row["installed"]:
                row["binding_error"] = "INVALID_OR_STALE_INSTALLED_POLICY"
                policies.pop(word.id, None)
                if "POLICY_REQUIRES_NEW_CONTENT_VERSION" not in reasons:
                    reasons.append("POLICY_REQUIRES_NEW_CONTENT_VERSION")
        if installed_keys is not None:
            row["installed"] = row["installed"] and key in installed_keys
        row["status"] = (
            "COVERED"
            if word.id in policies
            else "NEEDS_GRADING_REVIEW"
            if entry.published
            else "PUBLICATION_EXCLUDED"
        )
        rows.append(row)
    levels = {}
    for level in range(6):
        selected = [r for r in rows if r["published"] and r["learning_level"] == level]
        levels[str(level)] = {
            "published": len(selected),
            "installed_valid": sum(r["installed"] for r in selected),
            "proposed": sum(r["status"] == "COVERED" for r in selected),
        }
    counts = Counter(reason for r in rows if r["published"] for reason in r["reasons"])
    current_keys = {(e.word.id, e.word.content_version, e.word.checksum) for e in entries}
    return sorted(policies.values(), key=lambda p: by_id[p.vocabulary_id].word.lexical_key), {
        "counts": dict(counts),
        "per_level": levels,
        "total_catalog": len(entries),
        "published": sum(e.published for e in entries),
        "installed_valid": sum(r["installed"] for r in rows),
        "proposed_valid": len(policies),
        "new_policy_count": sum(not r["installed"] and r["status"] == "COVERED" for r in rows),
        "remaining_unresolved": sum(r["status"] == "NEEDS_GRADING_REVIEW" for r in rows),
        "records": rows,
        "baseline_counts": baseline["counts"],
        "outdated_or_unknown_preserved_policies": [
            p.model_dump(mode="json") for key, p in preserved.items() if key not in current_keys
        ],
    }
