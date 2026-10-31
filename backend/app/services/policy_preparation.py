"""Deterministic catalog recall policies. Never infer senses, readings or POS."""

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select, text

from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.curated_vocabulary import VocabularyExample, VocabularyMeaning
from app.models.srs import SrsTargetPolicy
from app.schemas.curated_vocabulary import is_hanzi
from app.services.curated_catalog import visible
from app.services.review_grading import POS_OPTIONS
from app.services.review_targets import ReviewedPolicy

GENERATOR = "catalog-cued-v1"


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value or "").casefold().split())


@dataclass
class CatalogEntry:
    word: Word
    meanings: list[str]
    published: bool
    examples: list[str] = field(default_factory=list)


async def catalog_entries(session):
    """Use the real publication predicate, including current evidence and feature flags."""
    published = set(await session.scalars(select(Word.id).where(visible())))
    meanings = defaultdict(list)
    examples = defaultdict(list)
    for identifier, translation in await session.execute(
        select(VocabularyExample.vocabulary_id, VocabularyExample.vietnamese).order_by(
            VocabularyExample.vocabulary_id, VocabularyExample.position
        )
    ):
        examples[identifier].append(translation)
    for identifier, gloss in await session.execute(
        select(VocabularyMeaning.vocabulary_id, VocabularyMeaning.gloss)
        .where(VocabularyMeaning.language == "vi")
        .order_by(VocabularyMeaning.vocabulary_id, VocabularyMeaning.position)
    ):
        meanings[identifier].append(gloss)
    return [
        CatalogEntry(w, meanings[w.id], w.id in published, examples[w.id])
        for w in await session.scalars(select(Word).order_by(Word.lexical_key))
    ]


async def installed_policies(session):
    # Preparation works before 0012; it must never create or migrate the table.
    if not await session.scalar(text("SELECT to_regclass('public.srs_target_policies')")):
        return []
    return [
        ReviewedPolicy.model_validate(p)
        for p in await session.scalars(select(SrsTargetPolicy.policy))
    ]


def prepare(entries, existing=(), *, only_ids=None):
    """Whole-lexeme recall, with an explicit Hán-Việt cue, not free translation.

    Check cue collisions and homographs against ALL records, including holds.
    Multiple glosses are retained together; never align gloss and POS positions.
    Only a single supported source POS is automatically eligible.
    """
    if len({e.word.id for e in entries}) != len(entries):
        raise ValueError("Duplicate vocabulary identity")
    forms, cues = defaultdict(set), defaultdict(set)
    for entry in entries:
        forms[entry.word.simplified].add(entry.word.id)
        cues[normalized(entry.word.sino_vietnamese)].add(entry.word.id)
    preserved = {}
    for policy in existing:
        key = (policy.vocabulary_id, policy.content_version, policy.checksum)
        if key in preserved and preserved[key] != policy:
            raise ValueError("Conflicting preserved policies")
        preserved[key] = policy
    policies, audit = [], []
    counts = Counter(
        {
            name: 0
            for name in (
                "automatically_gradable_records",
                "existing_manually_reviewed_policies",
                "existing_generated_policies",
                "published_review_eligible_records",
                "NEEDS_GRADING_REVIEW",
                "MISSING_POS",
                "MISSING_OR_UNSUITABLE_VIETNAMESE_PROMPT",
                "PUBLICATION_EXCLUDED",
            )
        }
    )
    counts["total_catalog_records"] = len(entries)
    current_keys = {(e.word.id, e.word.content_version, e.word.checksum) for e in entries}
    stale = [p.model_dump(mode="json") for k, p in preserved.items() if k not in current_keys]
    counts["outdated_or_unknown_preserved_policies"] = len(stale)
    selected = entries if only_ids is None else [e for e in entries if e.word.id in only_ids]
    for entry in sorted(selected, key=lambda e: e.word.lexical_key):
        w = entry.word
        reasons = []
        pos = normalized(w.part_of_speech)
        cue = normalized(w.sino_vietnamese)
        glosses = entry.meanings
        if not entry.published:
            reasons.append("PUBLICATION_EXCLUDED")
        else:
            counts["published_review_eligible_records"] += 1
        if not pos:
            reasons.append("MISSING_POS")
        elif any(c in pos for c in ";,/|"):
            reasons.append("MULTIPLE_POS_REQUIRES_SENSE_REVIEW")
        elif pos not in (*POS_OPTIONS, "measure word"):
            reasons.append("UNSUPPORTED_POS")
        if not glosses or any(
            not normalized(g) or any(is_hanzi(c) for c in g) or not any(c.isalpha() for c in g)
            for g in glosses
        ):
            reasons.append("MISSING_OR_UNSUITABLE_VIETNAMESE_PROMPT")
        # Explicit source cue avoids treating a unique gloss as proof against synonyms.
        if (
            not cue
            or not re.fullmatch(r"[^\W\d_]+(?: [^\W\d_]+)*", cue)
            or len(cue.split()) != len(w.simplified)
            or any(is_hanzi(c) for c in cue)
        ):
            reasons.append("MISSING_OR_UNSUITABLE_HAN_VIET_CUE")
        elif len(cues[cue]) > 1:
            reasons.append("SHARED_HAN_VIET_CUE")
        if len(forms[w.simplified]) > 1:
            reasons.append("MULTIPLE_PRONUNCIATIONS_REQUIRE_SENSE_REVIEW")
        payload = {
            "vocabulary_id": w.id,
            "content_version": w.content_version,
            "checksum": w.checksum,
            "policy_version": GENERATOR,
            "sense_key": "whole-lexeme-cued-recall",
            "vietnamese_prompt": (
                f"Viết từ đã học có âm Hán-Việt «{w.sino_vietnamese}» "
                f"({len(w.simplified)} chữ Hán). Nghĩa trong danh mục: " + "; ".join(glosses) + "."
            ),
            "reviewed_by": "Deterministic catalog preparation: " + GENERATOR,
            "ambiguity_resolution": (
                "Whole-lexeme recall explicitly constrained by the source Hán-Việt cue and "
                "character count, not an unrestricted translation. All Vietnamese glosses "
                "retained. Cue unique across the complete catalog including holds; no "
                "alternate pronunciation identity; one supported source POS. No sense/POS "
                "alignment inferred. Automated preparation, not human semantic certification."
            ),
            "accepted_pos": ["classifier" if pos == "measure word" else pos],
        }
        # Validate the lexical identity independently of unsupported/missing POS.
        try:
            probe = {**payload, "accepted_pos": [], "pos_skip_reason": "VALIDATION_ONLY"}
            ReviewedPolicy.model_validate(probe).target(w)
        except ValueError:
            reasons.append("INVALID_LEXICAL_IDENTITY_OR_PROMPT")
        key = (w.id, w.content_version, w.checksum)
        manual = preserved.get(key)
        if manual and manual.policy_version != GENERATOR and entry.published:
            manual.target(w)
            if not glosses or not all(g.strip() for g in glosses):
                raise ValueError("Preserved policy missing Vietnamese meanings")
            policies.append(manual)
            status = "PRESERVED_POLICY"
            counts["existing_manually_reviewed_policies"] += 1
        elif not reasons:
            policy = ReviewedPolicy.model_validate(payload)
            policy.target(w)
            policies.append(policy)
            status = "AUTOMATICALLY_GRADABLE"
            counts["automatically_gradable_records"] += 1
            if manual:
                counts["existing_generated_policies"] += 1
        else:
            status = "NEEDS_GRADING_REVIEW" if entry.published else "PUBLICATION_EXCLUDED"
        if status != "PUBLICATION_EXCLUDED":
            counts[status] += 1
        for reason in reasons:
            counts[reason] += 1
        audit.append(
            {
                "vocabulary_id": str(w.id),
                "lexical_key": w.lexical_key,
                "content_version": w.content_version,
                "checksum": w.checksum,
                "review_status": w.review_status,
                "published": entry.published,
                "status": status,
                "reasons": reasons,
                "vietnamese_meanings": glosses,
                "sino_vietnamese": w.sino_vietnamese,
                "part_of_speech": w.part_of_speech,
            }
        )
    counts["final_proposed_coverage"] = len(policies)
    examples = {
        reason: [r for r in audit if reason in r["reasons"]][:5]
        for reason in sorted({reason for row in audit for reason in row["reasons"]})
    }
    return policies, {
        "counts": dict(sorted(counts.items())),
        "examples": examples,
        "records": audit,
        "outdated_or_unknown_preserved_policies": stale,
    }
