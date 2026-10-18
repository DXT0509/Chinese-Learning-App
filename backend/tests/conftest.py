from app.core.event_loop import new_event_loop


def pytest_asyncio_loop_factories(config, item):
    return {"psycopg_compatible": new_event_loop}
