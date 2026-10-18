"""Run the API with a psycopg-compatible loop on every supported platform."""

import uvicorn

from app.core.logging import SERVER_LOG_CONFIG

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        loop="app.core.event_loop:new_event_loop",
        access_log=False,
        log_config=SERVER_LOG_CONFIG,
    )
