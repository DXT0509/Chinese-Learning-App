"""Read bounded JSON authoring files and validate their complete reference graph."""

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.schemas.content import (
    AssetDefinition,
    LessonDefinition,
    TemplateDefinition,
    VocabularyDefinition,
    content_id,
)


class ContentError(ValueError):
    """Safe author-facing error: no SQL, credentials or payload excerpts."""


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContentError("duplicate JSON object key")
        result[key] = value
    return result


@dataclass
class ContentLibrary:
    assets: list[AssetDefinition]
    vocabulary: list[VocabularyDefinition]
    templates: list[TemplateDefinition]
    lessons: list[LessonDefinition]


def _read_folder(root: Path, folder: str, schema):
    items = []
    for path in sorted((root / folder).glob("*.json")):
        try:
            if path.stat().st_size > 1_000_000:
                raise ContentError("authoring file exceeds 1 MB")
            value = json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=unique_json_object,
                parse_constant=lambda _: (_ for _ in ()).throw(
                    ContentError("non-finite JSON number")
                ),
            )
            items.append(schema.model_validate(value))
        except ValidationError as error:
            issues = [
                f"{'.'.join(map(str, item['loc']))}: {item['msg']}"
                for item in error.errors(include_input=False, include_url=False)
            ]
            raise ContentError(f"{folder}/{path.name}: {'; '.join(issues)}") from None
        except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
            raise ContentError(
                f"{folder}/{path.name}: unreadable or malformed UTF-8 JSON"
            ) from None
    return items


def load_library(root: Path) -> ContentLibrary:
    if not root.is_dir():
        raise ContentError("content directory does not exist")
    library = ContentLibrary(
        _read_folder(root, "assets", AssetDefinition),
        _read_folder(root, "vocabulary", VocabularyDefinition),
        _read_folder(root, "templates", TemplateDefinition),
        _read_folder(root, "lessons", LessonDefinition),
    )
    for kind, items in (
        ("asset", library.assets),
        ("vocabulary", library.vocabulary),
        ("template", library.templates),
        ("lesson", library.lessons),
    ):
        keys = [(content_id(kind, item.id), getattr(item, "version", None)) for item in items]
        if len(keys) != len(set(keys)):
            raise ContentError(f"duplicate {kind} identifiers/versions")
    if not library.lessons:
        raise ContentError("content directory must contain at least one lesson")
    assets = {content_id("asset", item.id): item for item in library.assets}
    words = {content_id("vocabulary", item.id) for item in library.vocabulary}
    templates = {(content_id("template", item.id), item.version) for item in library.templates}
    characters = {}
    descriptions = {}
    for template in library.templates:
        key = content_id("template", template.id)
        if key in descriptions and descriptions[key] != template.description:
            raise ContentError("template versions must agree on the stable template description")
        descriptions[key] = template.description
    for word in library.vocabulary:
        references = [(word.audio_asset, "audio/")]
        for character in word.characters:
            key = content_id("character", character.id)
            if key in characters and characters[key] != character:
                raise ContentError(f"conflicting character definition: {character.id}")
            characters[key] = character
            references.append((character.stroke_order_asset, "image/"))
        for ref, media_prefix in references:
            if ref is None:
                continue
            asset = assets.get(content_id("asset", ref))
            if not asset:
                raise ContentError(f"vocabulary {word.id}: missing asset reference {ref}")
            if not asset.media_type.startswith(media_prefix):
                raise ContentError(f"vocabulary {word.id}: incompatible asset type {ref}")
    for lesson in library.lessons:
        if (content_id("template", lesson.template.id), lesson.template.version) not in templates:
            raise ContentError(f"lesson {lesson.id}: missing exact template version")
        if content_id("vocabulary", lesson.vocabulary[0].vocabulary) not in words:
            raise ContentError(f"lesson {lesson.id}: missing TEACHES vocabulary reference")
    return library
