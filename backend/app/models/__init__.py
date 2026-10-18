"""Import all models here so Alembic sees the complete metadata."""

from app.models.content import (
    Asset,
    LessonTemplate,
    LessonTemplateScene,
    LessonTemplateVersion,
    LessonVersion,
)
from app.models.learning import (
    Character,
    Lesson,
    LessonVocabulary,
    SrsState,
    User,
    UserLessonProgress,
    UserVocabulary,
    Vocabulary,
    VocabularyCharacter,
)
from app.models.session import (
    AuthSession,
    LessonRun,
    PasswordCredential,
    RefreshCredential,
    SceneCheckpoint,
)

__all__ = [
    "Asset",
    "AuthSession",
    "Character",
    "Lesson",
    "LessonRun",
    "LessonTemplate",
    "LessonTemplateScene",
    "LessonTemplateVersion",
    "LessonVersion",
    "LessonVocabulary",
    "PasswordCredential",
    "RefreshCredential",
    "SceneCheckpoint",
    "SrsState",
    "User",
    "UserLessonProgress",
    "UserVocabulary",
    "Vocabulary",
    "VocabularyCharacter",
]
