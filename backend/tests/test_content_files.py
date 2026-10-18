import copy
import hashlib
import json
import shutil
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.content import (
    AssetDefinition,
    LessonDefinition,
    TemplateDefinition,
    VocabularyDefinition,
    content_id,
    hanzi_occurrences,
    version_id,
)
from app.services.content_files import ContentError, load_library
from app.services.content_storage import LocalContentStorage, verify_object
from app.services.lesson_publication import canonical_bundle

CONTENT = Path(__file__).resolve().parents[1] / "content"


@pytest.fixture
def content_copy(tmp_path):
    destination = tmp_path / "content"
    shutil.copytree(CONTENT, destination)
    return destination


def test_sample_is_strict_and_contains_no_fabricated_media():
    library = load_library(CONTENT)
    word = library.vocabulary[0]
    assert (word.simplified, word.pinyin, word.sino_vietnamese, word.vietnamese_meaning) == (
        "你",
        "nǐ",
        "nhĩ",
        "bạn",
    )
    assert word.characters[0].stroke_count is None
    assert not library.assets
    assert len(library.lessons[0].vocabulary) == 1


@pytest.mark.parametrize(
    "targets",
    [
        [],
        [
            {"vocabulary": "v-ni", "position": 0, "role": "TEACHES"},
            {"vocabulary": "v-other", "position": 1, "role": "TEACHES"},
        ],
    ],
)
def test_exactly_one_teaches_target(targets):
    value = load_library(CONTENT).lessons[0].model_dump()
    value["vocabulary"] = targets
    with pytest.raises(ValidationError):
        LessonDefinition.model_validate(value)


@pytest.mark.parametrize(
    "mutation",
    [
        {"lesson_type": "GRAMMAR"},
        {"lesson_type": "unknown"},
        {"version": 0},
        {"version": "1"},
        {"unexpected": "no"},
    ],
)
def test_invalid_lesson_contracts(mutation):
    value = load_library(CONTENT).lessons[0].model_dump()
    value.update(mutation)
    with pytest.raises(ValidationError):
        LessonDefinition.model_validate(value)


@pytest.mark.parametrize(
    "mutation",
    [
        {"scene_type": "HANDWRITING_PRACTICE"},
        {"contract_version": 2},
        {"required": "true"},
        {"condition": {"script": "execute"}},
        {"config": {"vocabulary_ref": {"binding": "SQL"}}},
    ],
)
def test_invalid_scene_contracts(mutation):
    value = load_library(CONTENT).templates[0].model_dump()
    value["scenes"][0].update(mutation)
    with pytest.raises(ValidationError):
        TemplateDefinition.model_validate(value)


@pytest.mark.parametrize("problem", ["position", "key", "order", "unknown_config"])
def test_scene_identity_and_order(problem):
    value = load_library(CONTENT).templates[0].model_dump()
    if problem == "position":
        value["scenes"][1]["position"] = value["scenes"][0]["position"]
    elif problem == "key":
        value["scenes"][1]["scene_key"] = value["scenes"][0]["scene_key"]
    elif problem == "order":
        value["scenes"].reverse()
    else:
        value["scenes"][0]["config"]["script"] = "arbitrary code"
    with pytest.raises(ValidationError):
        TemplateDefinition.model_validate(value)


def test_repeated_character_offsets_and_variation_selectors():
    value = load_library(CONTENT).vocabulary[0].model_dump()
    value["simplified"] = "你你"
    value["occurrences"] = [
        {"position": 0, "character": "character-ni"},
        {"position": 1, "character": "character-ni"},
    ]
    word = VocabularyDefinition.model_validate(value)
    assert len(word.characters) == 1 and len(word.occurrences) == 2
    value["occurrences"][1]["position"] = 0
    with pytest.raises(ValidationError, match="source offsets"):
        VocabularyDefinition.model_validate(value)
    assert hanzi_occurrences("你\U000e0100你") == [(0, "你\U000e0100"), (2, "你")]
    with pytest.raises(ValueError):
        hanzi_occurrences("\U000e0100你")


def test_missing_character_and_nfc_normalization():
    value = load_library(CONTENT).vocabulary[0].model_dump()
    value["pinyin"] = "ni\u030c"
    assert VocabularyDefinition.model_validate(value).pinyin == "nǐ"
    value["occurrences"][0]["character"] = "missing"
    with pytest.raises(ValidationError, match="missing character"):
        VocabularyDefinition.model_validate(value)


@pytest.mark.parametrize("reference", ["template", "vocabulary", "asset"])
def test_missing_graph_references(content_copy, reference):
    if reference == "asset":
        path = content_copy / "vocabulary/ni.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["audio_asset"] = "missing"
    else:
        path = content_copy / "lessons/lesson-ni.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        if reference == "template":
            value["template"]["version"] = 99
        else:
            value["vocabulary"][0]["vocabulary"] = "missing"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ContentError, match="missing"):
        load_library(content_copy)


def test_duplicate_files_and_json_keys(content_copy):
    source = content_copy / "lessons/lesson-ni.json"
    duplicate = source.with_name("duplicate.json")
    duplicate.write_bytes(source.read_bytes())
    with pytest.raises(ContentError, match="duplicate lesson"):
        load_library(content_copy)
    duplicate.write_text('{"id":"one","id":"two"}', encoding="utf-8")
    with pytest.raises(ContentError, match="duplicate JSON"):
        load_library(content_copy)


def test_malformed_input_does_not_echo_payload(content_copy):
    (content_copy / "lessons/lesson-ni.json").write_text("secret-invalid-json", encoding="utf-8")
    with pytest.raises(ContentError) as error:
        load_library(content_copy)
    assert "secret-invalid-json" not in str(error.value)


def test_alias_and_explicit_uuid_stability():
    assert content_id("vocabulary", "v-ni") == content_id("vocabulary", "v-ni")
    assert content_id("lesson", "v-ni") != content_id("vocabulary", "v-ni")
    explicit = uuid4()
    assert content_id("vocabulary", str(explicit)) == explicit
    assert version_id("lesson", "lesson-ni", 1) != version_id("lesson", "lesson-ni", 2)


def test_bundle_storage_hash_immutability_and_corruption(tmp_path):
    storage = LocalContentStorage(tmp_path)
    original = {"b": "你", "a": [1, 2]}
    data = canonical_bundle(original)
    assert data == canonical_bundle({"a": [1, 2], "b": "你"})
    key = storage.put_bundle(data)
    assert key == storage.put_bundle(data)
    assert verify_object(storage, key, hashlib.sha256(data).hexdigest(), len(data)) == data
    changed = copy.deepcopy(original)
    changed["a"].append(3)
    assert storage.put_bundle(canonical_bundle(changed)) != key
    assert storage.read(key) == data
    (tmp_path / key).write_bytes(b"corrupt")
    with pytest.raises(ContentError, match="corrupt"):
        storage.put_bundle(data)
    with pytest.raises(ContentError, match="SHA-256"):
        verify_object(storage, key, hashlib.sha256(data).hexdigest(), len(data))


@pytest.mark.parametrize("key", ["../escape", "https://signed-url", "sha256/../escape", "C:/data"])
def test_unsafe_storage_keys(tmp_path, key):
    with pytest.raises(ContentError):
        LocalContentStorage(tmp_path).read(key)


def test_asset_key_and_hash_must_agree():
    with pytest.raises(ValidationError, match="declared SHA-256"):
        AssetDefinition.model_validate(
            {
                "schema_version": 1,
                "id": "asset",
                "storage_key": f"sha256/{'a' * 64}.png",
                "sha256": "b" * 64,
                "byte_length": 3,
                "media_type": "image/png",
                "metadata": {},
            }
        )
