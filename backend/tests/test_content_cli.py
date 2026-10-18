import os
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_cli_supports_hanzi_when_windows_redirected_output_uses_legacy_encoding():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from scripts._content_cli import run; run('validate'); print('你 — nhĩ')",
        ],
        cwd=BACKEND,
        env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0
    assert "你 — nhĩ" in result.stdout.decode("utf-8")


def test_cli_reports_invalid_input_without_a_traceback(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "scripts.validate_content", "--content-dir", str(tmp_path)],
        cwd=BACKEND,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 1
    assert b"Content error:" in result.stderr
    assert b"Traceback" not in result.stderr
