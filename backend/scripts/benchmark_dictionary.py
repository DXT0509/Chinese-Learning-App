"""Rollback-only synthetic PostgreSQL benchmark; never claims real corpus performance."""

import argparse
import asyncio
import json
import os
import statistics
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.event_loop import new_event_loop
from app.repositories.dictionary import DictionaryRepository, search_statement
from app.schemas.dictionary import DictionaryQuery
from app.services.cedict import CedictDataset, parse_row
from app.services.dictionary import DictionaryService
from app.services.dictionary_import import import_dictionary


async def benchmark(rows: int):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise ValueError("Set TEST_DATABASE_URL to an isolated migrated PostgreSQL database")
    # Artificial headwords exercise Unicode indexes, broad prefixes and several readings.
    # English labels explicitly identify generated data; never use this as a real dictionary.
    entries = [
        parse_row(
            f"{chr(0x4E00 + i // 25)}{chr(0x4E00 + i % 25)} "
            f"{chr(0x4E00 + i // 25)}{chr(0x4E00 + i % 25)} "
            "[ce4 shi4] /SYNTHETIC BENCHMARK DATA/"
        )
        for i in range(rows)
    ]
    entries += [
        parse_row(f"学{chr(0x4E00 + i)} 学{chr(0x4E00 + i)} [ce4 shi4] /SYNTHETIC COMMON PREFIX/")
        for i in range(1000)
    ]
    entries = list({entry.id: entry for entry in entries}.values())
    dataset = CedictDataset("b" * 64, entries, 0)
    engine = create_async_engine(url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                factory = async_sessionmaker(
                    connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
                )
                async with factory() as session:
                    started = time.perf_counter()
                    summary = await import_dictionary(session, dataset, "synthetic-benchmark-v1")
                    import_seconds = time.perf_counter() - started
                    await session.execute(text("ANALYZE dictionary_entries"))
                    await session.execute(text("ANALYZE dictionary_imports"))
                    service = DictionaryService(DictionaryRepository(session))
                    timings = []
                    for i in range(105):
                        q = ("你", "学", "学一", "不存在", "一")[i % 5]
                        started = time.perf_counter()
                        await service.search(DictionaryQuery(q=q))
                        if i >= 5:
                            timings.append((time.perf_counter() - started) * 1000)
                    # EXPLAIN uses the same parameterized statement and normal planner settings.
                    compiled = search_statement(DictionaryQuery(q="学")).compile(
                        dialect=engine.sync_engine.dialect
                    )
                    cursor = await connection.get_raw_connection()
                    async with cursor.driver_connection.cursor() as pg_cursor:
                        await pg_cursor.execute(
                            "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + str(compiled),
                            compiled.params,
                        )
                        plan = (await pg_cursor.fetchone())[0]
                    print(
                        json.dumps(
                            {
                                "dataset": "synthetic, not a linguistic corpus",
                                "rows": len(entries),
                                "batches": summary["batches"],
                                "import_seconds": round(import_seconds, 3),
                                "samples": len(timings),
                                "median_ms": round(statistics.median(timings), 3),
                                "p95_ms": round(sorted(timings)[94], 3),
                                "plan": plan,
                                "scope": "warm local repository/service, excludes HTTP/auth/network",
                            },
                            ensure_ascii=True,
                        )
                    )
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rows", type=int, default=125000, help="1,000–200,000 synthetic base rows"
    )
    args = parser.parse_args()
    if not 1000 <= args.rows <= 200000:
        parser.error("--rows must be between 1000 and 200000")
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(benchmark(args.rows))


if __name__ == "__main__":
    run()
