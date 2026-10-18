import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_rejects_wildcard_cors():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=["*"])


def test_rejects_incompatible_database_driver():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="sqlite:///test.db")
