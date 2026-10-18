from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: SecretStr = Field(min_length=6, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class RefreshInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: SecretStr = Field(min_length=20, max_length=128)


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    display_name: str
    email: str | None
    email_verified: bool = False


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 600


class StartRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lesson_version_id: UUID
    request_id: UUID
    allow_preview: bool = False


class CheckpointInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(ge=0, le=10000)


class LessonMetadata(BaseModel):
    lesson_id: UUID
    lesson_version_id: UUID
    version: int
    title: str
    purpose: Literal["CONTENT_PREVIEW"] = "CONTENT_PREVIEW"
    learning_completion_supported: Literal[False] = False


class CheckpointInfo(BaseModel):
    scene_key: UUID
    page: int


class RunInfo(BaseModel):
    id: UUID
    lesson_version_id: UUID
    learning_completion_supported: Literal[False] = False
    checkpoints: list[CheckpointInfo]
