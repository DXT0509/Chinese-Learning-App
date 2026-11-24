"""Preparation is filesystem-only; fixtures never assert educational review of real assets."""

import hashlib
import io
import json
import wave
from pathlib import Path
from uuid import UUID, uuid5

import pytest
from pydantic import ValidationError

from app.schemas.roadmap import ActivitySubmission, RoadmapDefinition
from app.schemas.roadmap_preparation import (
    Analysis,
    AssetInput,
    EnrichmentInput,
    Example,
    PreparationPlan,
    Review,
    StructuredStrokes,
)
from app.services.content_files import ContentError
from app.services.curated_import import NAMESPACE
from app.services.roadmap import evaluate
from app.services.roadmap_preparation import (
    QualityReport,
    checksum,
    compile_drafts,
    generate,
    load_catalog,
    load_json,
    quiz,
    validate_asset,
    validate_generated,
)

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "backend/content/roadmaps/preparation/hsk-0.plan.json"
SOURCE = ROOT / "docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl"


@pytest.fixture
def inputs():
    return PreparationPlan.model_validate(load_json(PLAN)), load_catalog([SOURCE])


def codes(report):
    return {i["code"] for i in report.issues}


def attest(item):
    # Synthetic test review only, bound exactly like an external operator sidecar.
    item.review = Review(
        status="REVIEWED",
        reviewer="synthetic test reviewer",
        evidence="synthetic test fixture, no real educational approval",
        content_sha256=checksum(item.model_dump(mode="json", exclude={"review"})),
    )
    return item


def test_real_catalog_identity_and_one_word_contract(inputs, tmp_path):
    plan, catalog = inputs
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert [n.node_type for n in definition.nodes] == ["NEW_WORD"] * 3 + ["REVIEW"]
    assert [
        catalog[n.lesson.vocabulary[0].vocabulary_id].simplified for n in definition.nodes[:3]
    ] == ["我", "你", "好"]
    assert definition.nodes[-1].lesson.vocabulary == [
        n.lesson.vocabulary[0] for n in definition.nodes[:3]
    ]
    assert all(len(n.lesson.vocabulary) == 1 for n in definition.nodes[:3])
    assert report.payload()["counts"]["ERROR"] == 0
    assert report.payload()["publication_ready"] is False
    assert len([i for i in report.issues if i["severity"] == "OPTIONAL_MISSING"]) == 15
    assert all(n.lesson.audio.status == "UNAVAILABLE" for n in definition.nodes)
    assert all(a.kind != "PRONUNCIATION" for n in definition.nodes for a in n.lesson.activities)
    assert all(
        a.preserve_freehand and not a.automatic_snapping
        for n in definition.nodes
        for a in n.lesson.activities
    )


def test_deterministic_idempotent_resume_and_immutable_version(inputs, tmp_path):
    plan, catalog = inputs
    generate(plan, catalog, tmp_path, tmp_path / "out")
    files = list((tmp_path / "out").rglob("*.json"))
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
    generate(plan, dict(reversed(list(catalog.items()))), tmp_path, tmp_path / "out")
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
    lesson = next((tmp_path / "out/lessons").glob("*.json"))
    lesson.unlink()
    generate(plan, catalog, tmp_path, tmp_path / "out")
    assert lesson.read_bytes() == before[lesson][0]
    plan.title = "Changed same version"
    with pytest.raises(ContentError, match="new roadmap version"):
        generate(plan, catalog, tmp_path, tmp_path / "out")


def test_stable_ids_across_versions_and_exact_short_reviews(inputs, tmp_path):
    plan, catalog = inputs
    old, _, _ = compile_drafts(plan, catalog, tmp_path)
    plan.version = 2
    new, _, _ = compile_drafts(plan, catalog, tmp_path)
    assert [n.id for n in old.nodes] == [n.id for n in new.nodes]
    assert [a.id for n in old.nodes for a in n.lesson.activities] == [
        a.id for n in new.nodes for a in n.lesson.activities
    ]
    plan.review_interval = 2
    new, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert [len(n.lesson.vocabulary) for n in new.nodes if n.node_type == "REVIEW"] == [2, 1]
    assert "QUIZ_DISTRACTORS" in codes(report)
    for node in new.nodes:
        if node.node_type == "REVIEW":
            assert all(a.kind == "INTRODUCTION" for a in node.lesson.activities)


@pytest.mark.parametrize("mutation", ["duplicate", "unknown", "revision"])
def test_duplicate_and_revision_safety(inputs, tmp_path, mutation):
    plan, catalog = inputs
    if mutation == "duplicate":
        payload = plan.model_dump(mode="json")
        payload["groups"][0]["vocabulary"].append(payload["groups"][0]["vocabulary"][0])
        with pytest.raises(ValidationError, match="duplicate vocabulary"):
            PreparationPlan.model_validate(payload)
    else:
        ref = plan.groups[0].vocabulary[0]
        if mutation == "revision":
            ref.content_version += 1
        else:
            catalog.pop(ref.vocabulary_id)
        _, report, _ = compile_drafts(plan, catalog, tmp_path)
        assert "CATALOG_REVISION" in codes(report)
        assert not report.payload()["draft_valid"]


def test_tone_consistency_and_conflicting_catalog(inputs, tmp_path):
    _, catalog = inputs
    word = next(iter(catalog.values())).model_dump()
    word["pinyin"] = "wrong"
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps(word), encoding="utf-8")
    with pytest.raises(ContentError, match="invalid curated record"):
        load_catalog([path])
    word = next(iter(catalog.values())).model_dump()
    word["content_version"] += 1
    path.write_text(json.dumps(word), encoding="utf-8")
    with pytest.raises(ContentError, match="conflicting catalog"):
        load_catalog([SOURCE, path])


def test_quizzes_are_server_owned_and_review_has_no_future_words(inputs, tmp_path):
    plan, catalog = inputs
    definition, _, _ = compile_drafts(plan, catalog, tmp_path)
    review = definition.nodes[-1]
    assert len(review.lesson.activities) == 13
    for node in definition.nodes:
        for activity in node.lesson.activities:
            if activity.kind != "QUIZ":
                continue
            assert len(activity.options) == len(set(activity.options)) == 3
            body = ActivitySubmission(
                request_id=UUID(int=1),
                activity_id=activity.id,
                kind="CHOICE",
                choice=activity.correct_option,
            )
            assert evaluate(activity, body)
            body.choice = (activity.correct_option + 1) % 3
            assert not evaluate(activity, body)


def test_synonyms_and_polyphonic_distractors_are_rejected(inputs):
    plan, catalog = inputs
    target = catalog[plan.groups[0].vocabulary[0].vocabulary_id]
    synonym = target.model_copy(
        update={"simplified": "俺", "pinyin_numbered": "an3", "pinyin": "ǎn"}
    )
    homograph = target.model_copy(update={"pinyin_numbered": "wo4", "pinyin": "wò"})
    for kind in plan.templates.quizzes:
        assert quiz(kind, target, [target, synonym, homograph], 2, UUID(int=1)) is None


def analysis(**overrides):
    return Analysis(
        character_position=0,
        character="你",
        component="亻",
        position="LEFT",
        role="STRUCTURAL",
        explanation_vi="Giải thích thử nghiệm, chưa duyệt.",
        interpretation="MODERN_MNEMONIC",
        **overrides,
    )


def test_components_multicharacter_positions_and_review_binding(inputs, tmp_path):
    plan, catalog = inputs
    word_id = uuid5(NAMESPACE, "你好|ni3 hao3")
    ref = plan.groups[0].vocabulary[0].model_copy(update={"vocabulary_id": word_id})
    plan.groups[0].vocabulary = [ref]
    item = attest(analysis())
    plan.enrichments = [EnrichmentInput(reference=ref, components=[item])]
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert len(definition.nodes[0].lesson.components) == 1
    assert (
        "không khẳng định nguồn gốc lịch sử"
        in definition.nodes[0].lesson.components[0].explanation.text
    )
    item.character_position = 1
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "COMPONENT_CHARACTER" in codes(report)
    item.character_position = 0
    item.explanation_vi = "Changed since review"
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "STALE_REVIEW" in codes(report)


def test_component_invalid_positions_history_and_conflicts(inputs, tmp_path):
    with pytest.raises(ValidationError):
        Analysis.model_validate({**analysis().model_dump(), "position": "SOMEWHERE"})
    with pytest.raises(ValidationError, match="cited source"):
        Analysis.model_validate({**analysis().model_dump(), "interpretation": "HISTORICAL"})
    plan, catalog = inputs
    ref = plan.groups[0].vocabulary[1]
    item = attest(analysis())
    plan.enrichments = [EnrichmentInput(reference=ref, components=[item, item])]
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "COMPONENT_CONTRADICTION" in codes(report)


def test_examples_require_bound_review_tones_sense_and_difficulty(inputs, tmp_path):
    plan, catalog = inputs
    ref = plan.groups[0].vocabulary[0]
    example = Example(
        content={"simplified": "我", "pinyin": "wǒ", "vietnamese": "tôi"},
        pinyin_numbered="wo3",
        target_character_position=0,
        difficulty=0,
    )
    plan.enrichments = [EnrichmentInput(reference=ref, examples=[example])]
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert definition.nodes[0].lesson.examples.status == "UNAVAILABLE"
    assert "UNREVIEWED" in codes(report)
    attest(example)
    definition, _, _ = compile_drafts(plan, catalog, tmp_path)
    assert definition.nodes[0].lesson.examples.status == "AVAILABLE"
    example.pinyin_numbered = "wo4"
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "EXAMPLE_SENSE" in codes(report)
    example.pinyin_numbered = "wo3"
    example.content.pinyin = "wò"
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "EXAMPLE_PINYIN" in codes(report)
    example.content.pinyin = "wǒ"
    example.difficulty = 1
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "EXAMPLE_DIFFICULTY" in codes(report)


def audio_asset(plan, tmp_path):
    stream = io.BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 160)
    data = stream.getvalue()
    (tmp_path / "synthetic.wav").write_bytes(data)
    asset = AssetInput(
        id=UUID(int=100),
        version=1,
        purpose="AUDIO",
        reference=plan.groups[0].vocabulary[0],
        simplified="我",
        pinyin_numbered="wo3",
        file="synthetic.wav",
        sha256=hashlib.sha256(data).hexdigest(),
        byte_length=len(data),
        media_type="audio/wav",
        source="synthetic fixture; silence is not educational pronunciation",
        attribution="test",
        license="test only",
        redistribution_allowed=True,
        origin="HUMAN_RECORDED",
    )
    return attest(asset), data


@pytest.mark.parametrize(
    "change,code",
    [
        ({"simplified": "你"}, "ASSET_CHARACTER"),
        ({"pinyin_numbered": "wo4"}, "AUDIO_PRONUNCIATION"),
        ({"sha256": "0" * 64}, "ASSET_INTEGRITY"),
        ({"redistribution_allowed": False}, "ASSET_LICENSE"),
        ({"origin": "TTS"}, "TTS_PROVIDER"),
        ({"file": "../outside.wav"}, "ASSET_PATH"),
        ({"media_type": "audio/mpeg"}, "ASSET_FORMAT"),
    ],
)
def test_audio_metadata_integrity_and_license(inputs, tmp_path, change, code):
    plan, catalog = inputs
    asset, _ = audio_asset(plan, tmp_path)
    for key, value in change.items():
        setattr(asset, key, value)
    attest(asset)
    report = QualityReport()
    assert validate_asset(asset, catalog[asset.reference.vocabulary_id], tmp_path, report) is None
    assert code in codes(report)


def test_prepared_assets_are_cas_and_pronunciation_is_participation_only(inputs, tmp_path):
    plan, catalog = inputs
    asset, data = audio_asset(plan, tmp_path)
    plan.assets = [asset]
    definition, report = generate(plan, catalog, tmp_path, tmp_path / "out")
    assert report.payload()["draft_valid"]
    pronunciation = next(
        a for a in definition.nodes[0].lesson.activities if a.kind == "PRONUNCIATION"
    )
    assert pronunciation.evaluation == "PARTICIPATION"
    assert pronunciation.repetitions == 2
    manifest = load_json(tmp_path / "out/assets.json")
    assert (tmp_path / "out/objects" / manifest[0]["storage_key"]).read_bytes() == data
    from app.services.content_files import load_library

    library = load_library(tmp_path / "out/asset-library", assets_only=True)
    assert len(library.assets) == 1
    assert str(library.assets[0].id) == str(definition.nodes[0].lesson.audio.asset_id)
    with pytest.raises(ContentError, match="at least one lesson"):
        load_library(tmp_path / "out/asset-library")
    assert validate_generated(plan, catalog, tmp_path, tmp_path / "out")[1].payload()["draft_valid"]
    (tmp_path / "out/objects" / manifest[0]["storage_key"]).write_bytes(b"corrupt")
    assert "GENERATED_INTEGRITY" in codes(
        validate_generated(plan, catalog, tmp_path, tmp_path / "out")[1]
    )


def test_reviewed_stroke_image_generation_missing_file_and_wrong_word(inputs, tmp_path):
    import base64

    plan, catalog = inputs
    asset, _ = audio_asset(plan, tmp_path)
    # A synthetic 1px image exercises transport only; it is NOT a stroke-order illustration.
    raw = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j4YQAAAAASUVORK5CYII="
    )
    asset.purpose, asset.origin, asset.media_type = "STROKE_ORDER", "AUTHORED", "image/png"
    asset.pinyin_numbered = None
    asset.file, asset.sha256, asset.byte_length = (
        "synthetic.png",
        hashlib.sha256(raw).hexdigest(),
        len(raw),
    )
    (tmp_path / asset.file).write_bytes(raw)
    attest(asset)
    plan.assets = [asset]
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert report.payload()["draft_valid"]
    assert definition.nodes[0].lesson.stroke_order.status == "AVAILABLE"
    assert "STROKE_ORDER" in [a.kind for a in definition.nodes[0].lesson.activities]
    (tmp_path / asset.file).unlink()
    _, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert "ASSET_MISSING" in codes(report)
    assert not report.payload()["draft_valid"]


def test_example_target_and_unreviewed_audio_are_omitted(inputs, tmp_path):
    plan, catalog = inputs
    asset, _ = audio_asset(plan, tmp_path)
    asset.review = Review()
    plan.assets = [asset]
    ref = plan.groups[0].vocabulary[0]
    example = Example(
        content={"simplified": "你", "pinyin": "nǐ", "vietnamese": "bạn"},
        pinyin_numbered="ni3",
        target_character_position=0,
        difficulty=0,
    )
    plan.enrichments = [EnrichmentInput(reference=ref, examples=[example])]
    definition, report, _ = compile_drafts(plan, catalog, tmp_path)
    assert definition.nodes[0].lesson.audio.status == "UNAVAILABLE"
    assert "UNREVIEWED" in codes(report) and "EXAMPLE_TARGET" in codes(report)


def test_structured_strokes_require_exact_multicharacter_order(inputs, tmp_path):
    plan, catalog = inputs
    word_id = uuid5(NAMESPACE, "你好|ni3 hao3")
    asset, _ = audio_asset(plan, tmp_path)
    asset.reference = asset.reference.model_copy(update={"vocabulary_id": word_id})
    asset.simplified = "你好"
    asset.purpose, asset.origin, asset.media_type = (
        "STRUCTURED_STROKES",
        "DATASET",
        "application/json",
    )
    data = {"characters": [{"character": c, "strokes": [[[0, 0], [1, 1]]]} for c in "你好"]}
    raw = json.dumps(data).encode()
    asset.file, asset.sha256, asset.byte_length = (
        "strokes.json",
        hashlib.sha256(raw).hexdigest(),
        len(raw),
    )
    (tmp_path / asset.file).write_bytes(raw)
    attest(asset)
    report = QualityReport()
    assert validate_asset(asset, catalog[word_id], tmp_path, report) == raw
    assert "STRUCTURED_RENDERER_PENDING" in codes(report)
    data["characters"].reverse()
    raw = json.dumps(data).encode()
    (tmp_path / asset.file).write_bytes(raw)
    asset.sha256, asset.byte_length = hashlib.sha256(raw).hexdigest(), len(raw)
    attest(asset)
    report = QualityReport()
    assert validate_asset(asset, catalog[word_id], tmp_path, report) is None
    assert "STROKE_DATA" in codes(report)
    with pytest.raises(ValidationError):
        StructuredStrokes(
            characters=[{"character": "你", "strokes": [[[float("nan"), 0], [1, 1]]]}]
        )


@pytest.mark.parametrize("target", ["roadmap", "lesson", "binding", "assets"])
def test_output_tampering_blocks_candidate(inputs, tmp_path, target):
    plan, catalog = inputs
    generate(plan, catalog, tmp_path, tmp_path / "out")
    if target == "roadmap":
        path = tmp_path / "out/roadmap.json"
        payload = load_json(path)
        payload["title"] = "tampered"
    elif target == "lesson":
        path = next((tmp_path / "out/lessons").glob("*.json"))
        payload = load_json(path)
        payload["title"] = "tampered"
    elif target == "binding":
        path = tmp_path / "out/manifest.json"
        payload = load_json(path)
        payload["catalog_bindings"] = []
    else:
        path = tmp_path / "out/assets.json"
        payload = [{"id": "unrelated"}]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert "GENERATED_INTEGRITY" in codes(
        validate_generated(plan, catalog, tmp_path, tmp_path / "out")[1]
    )


def test_filesystem_commands_never_open_database_and_preview_hides_keys(
    inputs, tmp_path, monkeypatch, capsys
):
    from types import SimpleNamespace

    from scripts import roadmap

    def forbidden():
        raise AssertionError("offline commands must not open database sessions")

    monkeypatch.setattr(roadmap, "session_factory", forbidden)
    args = SimpleNamespace(
        command="generate-drafts",
        plan=PLAN,
        catalog=[SOURCE],
        asset_root=tmp_path,
        output=tmp_path / "out",
    )
    assert roadmap.preparation_run(args) == 0
    capsys.readouterr()
    args.command = "preview-file"
    assert roadmap.preparation_run(args) == 0
    preview = capsys.readouterr().out
    assert "correct_option" not in preview
    args.command = "prepare-bundle"
    assert roadmap.preparation_run(args) == 0
    candidate = load_json(args.output / "publication-candidate.json")
    assert candidate["status"] == "DRAFT" and not candidate["publication_ready"]
    assert RoadmapDefinition.model_validate(candidate["definition"])
    assert not (tmp_path / ".content-storage").exists()


def test_assets_only_mode_refuses_mixed_library():
    from app.services.content_files import load_library

    with pytest.raises(ContentError, match="assets-only import refuses"):
        load_library(ROOT / "backend/content", assets_only=True)
