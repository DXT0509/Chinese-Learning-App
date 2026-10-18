"""psycopg requires selector loops on Windows; avoid deprecated policy APIs."""

import asyncio
import sys


def new_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()
