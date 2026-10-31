"""Validate/install reviewed policies, or report missing policies. Never writes learner state."""

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import select, text

from app.core.database import session_factory
from app.core.event_loop import new_event_loop
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.services.policy_installation import import_policies
from app.services.review_targets import ReviewedPolicy, ReviewedTargets, editorial_flags


async def run(args):
    async with session_factory() as session, session.begin():
        if not args.install:
            await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        if args.file:
            policies = [
                ReviewedPolicy.model_validate(p)
                for p in json.loads(Path(args.file).read_text(encoding="utf-8"))
            ]
            result = await import_policies(session, policies, install=args.install)
            print(json.dumps({**result, "install_requested": args.install}))
        else:
            words = list(await session.scalars(select(Word).order_by(Word.id)))
            flags = await editorial_flags(session, words)
            excluded = []
            for word in words:
                target = await ReviewedTargets().resolve(session, word)
                if not target.gradeable:
                    excluded.append(
                        {
                            "vocabulary_id": str(word.id),
                            "lexical_key": word.lexical_key,
                            "reason": "REVIEWED_POLICY_REQUIRED",
                            "editorial_flags": flags[word.id],
                        }
                    )
            print(
                json.dumps({"catalog_count": len(words), "excluded": excluded}, ensure_ascii=False)
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="JSON array of operator-reviewed policies")
    parser.add_argument(
        "--install", action="store_true", help="Explicitly persist validated policies"
    )
    args = parser.parse_args()
    if args.install and not args.file:
        parser.error("--install requires --file")
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(run(args))


if __name__ == "__main__":
    main()
