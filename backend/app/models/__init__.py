"""Import all models here so Alembic sees the complete metadata."""

from app.models.content import (
    Asset,
    LessonTemplate,
    LessonTemplateScene,
    LessonTemplateVersion,
    LessonVersion,
)
from app.models.curated_vocabulary import (  # noqa: F401
    CuratedBatch,
    CuratedUserVocabulary,
    CuratedVocabulary,
    VocabularyExample,
    VocabularyMeaning,
    VocabularyReviewSubmission,
    VocabularyRevision,
)
from app.models.dictionary import (
    DictionaryCharacterEnrichment,
    DictionaryEnrichmentImport,
    DictionaryEntry,
    DictionaryImport,
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
from app.models.personal_vocabulary import PersonalVocabularyEntry
from app.models.session import (
    AuthSession,
    LessonRun,
    PasswordCredential,
    RefreshCredential,
    SceneCheckpoint,
)
from app.models.srs import SrsReviewAttempt, SrsTargetPolicy
from app.models.srs_v2 import SrsActiveTime, SrsDailyPlan, SrsMemory  # noqa: F401

__all__ = [
    "Asset",
    "AuthSession",
    "Character",
    "DictionaryCharacterEnrichment",
    "DictionaryEnrichmentImport",
    "DictionaryEntry",
    "DictionaryImport",
    "Lesson",
    "LessonRun",
    "LessonTemplate",
    "LessonTemplateScene",
    "LessonTemplateVersion",
    "LessonVersion",
    "LessonVocabulary",
    "PasswordCredential",
    "PersonalVocabularyEntry",
    "RefreshCredential",
    "SceneCheckpoint",
    "SrsReviewAttempt",
    "SrsState",
    "SrsTargetPolicy",
    "User",
    "UserLessonProgress",
    "UserVocabulary",
    "Vocabulary",
    "VocabularyCharacter",
]
