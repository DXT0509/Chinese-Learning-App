"""Serialize authored decisions only against the reviewed baseline bindings; read-only DB."""

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import text

from app.core.database import session_factory
from app.core.event_loop import new_event_loop
from app.services.policy_coverage import catalog_pos
from app.services.policy_preparation import catalog_entries
from app.services.review_targets import ReviewedPolicy
from scripts.phase41d_context_notes import CONTEXT_NOTES
from scripts.prepare_review_policies import write_new


async def run(args):
    baseline = {
        row["lexical_key"]: row
        for row in json.loads(Path(args.baseline).read_text(encoding="utf-8"))["records"]
    }
    result = []
    async with session_factory() as session, session.begin():
        await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        for entry in await catalog_entries(session):
            word = entry.word
            note = CONTEXT_NOTES.get(word.lexical_key)
            if not note:
                continue
            original = baseline[word.lexical_key]
            if not entry.published or (word.checksum, word.content_version) != (
                original["checksum"],
                original["content_version"],
            ):
                raise ValueError("Authored note requires new review against changed content")
            pos, unknown = catalog_pos(word.part_of_speech)
            if not pos or unknown:
                raise ValueError("Authored context does not authorize a POS correction")
            policy = ReviewedPolicy(
                vocabulary_id=word.id,
                content_version=word.content_version,
                checksum=word.checksum,
                policy_version="phase41d-context-reviewed-v1",
                sense_key="cued-lexical-identity-all-source-pos",
                vietnamese_prompt=(
                    f"Viết mục từ đã học ({len(word.simplified)} chữ Hán). "
                    + note
                    + " Ở bước từ loại, chọn tất cả từ loại của mục từ này trong danh mục."
                ),
                reviewed_by="Codex session linguistic review 2026-10-28; no human approval asserted",
                ambiguity_resolution=(
                    note + " Reviewed against catalog conflicts; only the bound "
                    "spelling and pronunciation are answers. All source POS retained. "
                    "Prompt-only decision; published content unchanged."
                ),
                accepted_pos=pos,
            )
            policy.target(word)
            result.append(policy.model_dump(mode="json"))
    if len(result) != len(CONTEXT_NOTES):
        raise ValueError("Missing authored identity")
    write_new(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"authored_contexts": len(result), "database_writes": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--output", required=True)
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
