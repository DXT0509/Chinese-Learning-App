import json
import logging

from app.core.logging import JsonFormatter


def test_structured_logging_omits_exception_details():
    error = RuntimeError("sensitive-token-value")
    record = logging.LogRecord(
        "chinese_learning",
        logging.ERROR,
        __file__,
        1,
        "unhandled_server_error",
        (),
        (RuntimeError, error, None),
    )
    output = JsonFormatter().format(record)
    assert json.loads(output)["event"] == "unhandled_server_error"
    assert "sensitive-token-value" not in output
