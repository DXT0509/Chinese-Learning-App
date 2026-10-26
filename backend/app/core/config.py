from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore"
    )
    app_name: str = "Chinese Learning API"
    environment: Literal["development", "test", "production"] = "development"
    database_url: str = (
        "postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_learning"
    )
    cors_origins: list[str] = []
    google_web_client_id: str | None = None
    allow_content_preview: bool = False
    allow_ai_approved_vocabulary: bool = False
    allow_local_codex_reviewed_vocabulary: bool = False
    content_storage_dir: Path = Path(__file__).resolve().parents[2] / ".content-storage"

    @model_validator(mode="after")
    def local_review_is_development_only(self):
        if self.allow_local_codex_reviewed_vocabulary and self.environment != "development":
            raise ValueError("Local Codex review is restricted to development")
        return self

    @field_validator("database_url")
    @classmethod
    def async_postgres_only(cls, value: str) -> str:
        if make_url(value).drivername != "postgresql+psycopg":
            raise ValueError("Use postgresql+psycopg for all database access")
        return value

    @field_validator("cors_origins")
    @classmethod
    def explicit_origins(cls, value: list[str]) -> list[str]:
        if any(origin == "*" for origin in value):
            raise ValueError("Specify explicit CORS origins")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
