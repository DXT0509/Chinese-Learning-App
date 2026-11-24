"""Real six-source packet remains unapproved; review preview can never pass release gates."""

import hashlib
from pathlib import Path

import pytest

from app.services.content_files import ContentError
from app.services.roadmap_media_validation import inspect_vorbis
from app.services.roadmap_preparation import (
    compile_drafts,
    generate,
    load_catalog,
    load_json,
    validate_generated,
)
from scripts.prepare_hsk0_pack import CATALOG, PACK, audit_original, build_plan


def test_all_original_activities_have_individual_decisions_and_shorter_pack():
    plan, catalog = build_plan(), load_catalog([CATALOG])
    audit = audit_original(plan, catalog)
    assert len(audit) == 31 and len({a["id"] for a in audit}) == 31
    assert all(a["answer_key_valid"] and a["human_review"] == "PENDING" for a in audit)
    definition, report, prepared = compile_drafts(plan, catalog, PACK, operator_preview=True)
    assert sum(len(n.lesson.activities) for n in definition.nodes) == 22
    assert [len(n.lesson.activities) for n in definition.nodes] == [6, 6, 6, 4]
    assert sum(a.repetitions for n in definition.nodes for a in n.lesson.activities) == 25
    assert len(prepared) == 6 and not report.payload()["draft_valid"]
    assert {i["code"] for i in report.issues if i["severity"] == "ERROR"} == {
        "HUMAN_REVIEW_REQUIRED"
    }
    assert len([i for i in report.issues if i["code"] == "HUMAN_REVIEW_REQUIRED"]) == 17
    for node in definition.nodes[:3]:
        assert len(node.lesson.vocabulary) == 1
        assert node.lesson.examples.status == node.lesson.audio.status == "AVAILABLE"
        assert all(a.kind != "COMPONENTS" for a in node.lesson.activities)
    assert not definition.nodes[-1].lesson.activities[0].required
    assert definition.nodes[-1].lesson.vocabulary == [
        n.lesson.vocabulary[0] for n in definition.nodes[:3]
    ]


def test_native_sources_ogg_crc_and_upstream_sha_are_exact():
    sources = load_json(PACK / "sources/sources.json")
    assert len(sources) == 6
    for source in sources:
        raw = (PACK / "sources" / source["file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source["sha256"]
        assert hashlib.sha1(raw).hexdigest() == source["upstream_sha1"]
        assert source["human_approval"] is None
        if source["file"].endswith(".ogg"):
            inspection = inspect_vorbis(raw)
            assert 500 <= inspection["duration_ms"] <= 2000 and inspection["crc_verified"]
            corrupt = bytearray(raw)
            corrupt[-10] ^= 1
            with pytest.raises(ValueError, match="CRC"):
                inspect_vorbis(bytes(corrupt))
            with pytest.raises(ValueError):
                inspect_vorbis(raw[:-100])


def test_tone_choices_and_scope_have_one_correct_target():
    from app.core.pinyin import tone_marks

    plan, catalog = build_plan(), load_catalog([CATALOG])
    definition, _, _ = compile_drafts(plan, catalog, PACK, operator_preview=True)
    for node in definition.nodes[:3]:
        target = catalog[node.lesson.vocabulary[0].vocabulary_id]
        quiz = next(a for a in node.lesson.activities if a.kind == "QUIZ")
        assert len(set(quiz.options)) == 3
        assert quiz.options[quiz.correct_option] == target.pinyin
        possible_tones = {tone_marks(target.pinyin_numbered[:-1] + str(i)) for i in range(1, 5)}
        assert set(quiz.options) <= possible_tones
    assert all(
        a.kind == "QUIZ" and set(a.options) == {"我", "你", "好"}
        for a in definition.nodes[-1].lesson.activities[1:]
    )


def test_pending_enrichment_is_never_approved_by_preview_or_candidate(tmp_path):
    plan, catalog = build_plan(), load_catalog([CATALOG])
    before = plan.model_dump(mode="json")
    generate(plan, catalog, PACK, tmp_path / "preview", operator_preview=True)
    assert load_json(tmp_path / "preview/manifest.json")["purpose"] == "OPERATOR_REVIEW_ONLY"
    assert plan.model_dump(mode="json") == before
    assert not validate_generated(plan, catalog, PACK, tmp_path / "preview")[1].payload()[
        "draft_valid"
    ]
    normal, _, _ = compile_drafts(plan, catalog, PACK)
    assert all(n.lesson.audio.status == "UNAVAILABLE" for n in normal.nodes)
    assert all(a.kind != "PRONUNCIATION" for n in normal.nodes for a in n.lesson.activities)
    assert all(a.review.status == "UNREVIEWED" for a in plan.assets)


def test_additive_templates_preserve_existing_63a_manifest():
    from app.schemas.roadmap_preparation import PreparationPlan
    from app.services.roadmap_preparation import generation_manifest
    from scripts.prepare_hsk0_pack import HERE

    plan = PreparationPlan.model_validate(
        load_json(HERE / "content/roadmaps/preparation/hsk-0.plan.json")
    )
    definition, _, prepared = compile_drafts(plan, load_catalog([CATALOG]), Path("."))
    assert generation_manifest(plan, load_catalog([CATALOG]), definition, prepared) == load_json(
        HERE / "content/roadmaps/preparation/hsk-0-v1/manifest.json"
    )


async def test_operator_preview_import_is_refused_before_db_write(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from scripts import roadmap
    from scripts.prepare_hsk0_pack import REVIEW_DIR

    monkeypatch.setattr(roadmap, "import_draft", AsyncMock())
    args = SimpleNamespace(command="import", file=REVIEW_DIR / "roadmap.json")
    with pytest.raises(ContentError, match="operator review previews cannot be imported"):
        await roadmap.run(args)
    roadmap.import_draft.assert_not_awaited()


def test_cas_staging_dry_run_and_explicit_copy_are_integrity_checked(tmp_path, capsys):
    from types import SimpleNamespace

    from app.schemas.roadmap_preparation import PreparationPlan
    from app.services.content_storage import LocalContentStorage
    from scripts import roadmap
    from scripts.prepare_hsk0_pack import HERE
    from tests.test_roadmap_preparation import audio_asset

    source_plan = HERE / "content/roadmaps/preparation/hsk-0.plan.json"
    plan = PreparationPlan.model_validate(load_json(source_plan))
    asset, raw = audio_asset(plan, tmp_path)
    plan.assets = [asset]
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(plan.model_dump_json(), encoding="utf-8")
    generate(plan, load_catalog([CATALOG]), tmp_path, tmp_path / "output")
    args = SimpleNamespace(
        command="stage-assets",
        plan=plan_file,
        catalog=[CATALOG],
        asset_root=tmp_path,
        output=tmp_path / "output",
        storage_dir=tmp_path / "api-storage",
        apply=False,
    )
    assert roadmap.preparation_run(args) == 0
    assert not args.storage_dir.exists()
    args.apply = True
    assert roadmap.preparation_run(args) == 0
    key = load_json(args.output / "assets.json")[0]["storage_key"]
    assert LocalContentStorage(args.storage_dir).read(key) == raw
    (args.storage_dir / key).write_bytes(b"corrupt")
    with pytest.raises(ContentError, match="corrupt"):
        roadmap.preparation_run(args)
