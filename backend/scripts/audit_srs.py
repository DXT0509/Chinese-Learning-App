"""Read-only SRS compatibility inventory; never changes catalog or personal data."""

import argparse
import asyncio
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.core.pinyin import tone_marks
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyMeaning
from app.schemas.curated_vocabulary import is_hanzi, simplified_only
from app.services.curated_catalog import visible


async def audit():
    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            async with AsyncSession(connection) as session:
                words = list(await session.scalars(select(CuratedVocabulary)))
                public = set(await session.scalars(select(CuratedVocabulary.id).where(visible())))
                meanings = defaultdict(list)
                gloss_targets = defaultdict(set)
                for m in await session.scalars(select(VocabularyMeaning)):
                    if m.language == "vi":
                        meanings[m.vocabulary_id].append(m.gloss)
                        gloss_targets[m.gloss.casefold().strip()].add(m.vocabulary_id)
                forms = defaultdict(list)
                issues = []
                for w in words:
                    forms[w.simplified].append(w.lexical_key)
                    flags = []
                    if w.lexical_key != f"{w.simplified}|{w.pinyin_numbered}":
                        flags.append("identity_mismatch")
                    try:
                        simplified_only(w.simplified)
                        if not all(is_hanzi(c) for c in w.simplified):
                            raise ValueError("Nonlexical form")
                    except ValueError:
                        flags.append("invalid_simplified_disable_hanzi")
                    if not re.fullmatch(r"[a-zü]+[1-5](?: [a-zü]+[1-5])*", w.pinyin_numbered):
                        flags.append("invalid_numbered_pinyin")
                    if len(w.pinyin_numbered.split()) != len(w.simplified):
                        flags.append("syllable_count_mismatch")
                    if not w.part_of_speech or not w.part_of_speech.strip():
                        flags.append("missing_pos_disable_pos_stage")
                    elif any(c in w.part_of_speech for c in "/,;|"):
                        flags.append("compound_pos_requires_sense_mapping")
                    if len(meanings[w.id]) > 1:
                        flags.append("multiple_glosses_require_sense_review")
                    if any(len(gloss_targets[g.casefold().strip()]) > 1 for g in meanings[w.id]):
                        flags.append("shared_vi_gloss_disable_unqualified_hanzi_prompt")
                    if not meanings[w.id]:
                        flags.append("missing_vi_disable_prompt")
                    try:
                        if tone_marks(w.pinyin_numbered) != w.pinyin:
                            flags.append("pinyin_mismatch_disable_pinyin")
                    except ValueError:
                        flags.append("invalid_pinyin_disable_pinyin")
                    if flags:
                        issues.append(
                            {
                                "id": str(w.id),
                                "lexical_key": w.lexical_key,
                                "visible": w.id in public,
                                "pos": w.part_of_speech,
                                "vi": meanings[w.id],
                                "issues": flags,
                            }
                        )
                counts = {}
                for table in (
                    "users",
                    "curated_user_vocabulary",
                    "curated_vocabulary_reviews",
                    "personal_vocabulary_entries",
                    "user_vocabulary",
                    "srs_states",
                    "user_lesson_progress",
                    "lesson_runs",
                ):
                    counts[table] = await session.scalar(text(f"SELECT count(*) FROM {table}"))
                return {
                    "audited_at": datetime.now(UTC).isoformat(),
                    "database_writes": 0,
                    "database_identity": list(
                        (
                            await session.execute(
                                text(
                                    "SELECT current_database(), inet_server_addr()::text, inet_server_port(), current_user"
                                )
                            )
                        ).one()
                    ),
                    "revision": await session.scalar(
                        text("SELECT version_num FROM alembic_version")
                    ),
                    "catalog_count": len(words),
                    "visible_count": len(public),
                    "review_status_counts": dict(Counter(w.review_status for w in words)),
                    "unavailable_records": [
                        {
                            "id": str(w.id),
                            "lexical_key": w.lexical_key,
                            "review_status": w.review_status,
                        }
                        for w in words
                        if w.id not in public
                    ],
                    "pos_counts": dict(Counter(w.part_of_speech for w in words)),
                    "preservation_counts": counts,
                    "backfill_counts": dict(
                        (
                            await session.execute(
                                text(
                                    "SELECT mastery_level, count(*) FROM curated_user_vocabulary GROUP BY mastery_level"
                                )
                            )
                        ).all()
                    ),
                    "backfill_null_due": await session.scalar(
                        text(
                            "SELECT count(*) FROM curated_user_vocabulary WHERE next_review_at IS NULL"
                        )
                    ),
                    "distinct_readings": {k: v for k, v in forms.items() if len(v) > 1},
                    "issue_counts": dict(Counter(f for row in issues for f in row["issues"])),
                    "records_requiring_exercise_policy": issues,
                    "linguistic_limit": "Structural flags are not semantic adjudication; unflagged glosses also require reviewed answer sets before grading.",
                }
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        report = runner.run(audit())
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("records_requiring_exercise_policy", "distinct_readings", "pos_counts")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
