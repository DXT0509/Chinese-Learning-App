"""Deterministic draft compiler. No sessions, provider calls, publication or learner writes."""

import hashlib
import io
import json
import os
import re
import tempfile
import unicodedata
import wave
from collections import Counter
from pathlib import Path
from uuid import uuid5

from app.core.pinyin import tone_marks
from app.schemas.content import AssetDefinition
from app.schemas.curated_vocabulary import CuratedRecord, is_hanzi, simplified_only
from app.schemas.roadmap import RoadmapDefinition
from app.schemas.roadmap_preparation import PreparationPlan, StructuredStrokes
from app.services.content_files import ContentError, unique_json_object
from app.services.content_storage import LocalContentStorage
from app.services.curated_import import NAMESPACE, record_checksum

COMPILER_VERSION = "roadmap-preparation-1"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def checksum(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_json(path):
    path = Path(path)
    if path.stat().st_size > 20_000_000:
        raise ContentError("authoring input exceeds 20 MB")
    return json.loads(
        path.read_text("utf-8"),
        object_pairs_hook=unique_json_object,
        parse_constant=lambda _: (_ for _ in ()).throw(ContentError("non-finite JSON number")),
    )


def load_catalog(paths):
    """Read existing converted curated records, retaining exact revision/checksum identity."""
    records = {}
    for path in paths:
        with Path(path).open(encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    record = CuratedRecord.model_validate(
                        json.loads(line, object_pairs_hook=unique_json_object)
                    )
                except ValueError as error:
                    raise ContentError(
                        f"invalid curated record at {Path(path).name}:{number}"
                    ) from error
                identifier = uuid5(NAMESPACE, record.lexical_key)
                if identifier in records and records[identifier] != record:
                    raise ContentError(
                        "conflicting catalog identities; select one explicit revision"
                    )
                records[identifier] = record
    if not records:
        raise ContentError("catalog contains no records")
    return records


class QualityReport:
    def __init__(self):
        self.issues = []

    def add(self, severity, code, location, message):
        self.issues.append(
            {"severity": severity, "code": code, "location": location, "message": message}
        )

    def payload(self):
        counts = Counter(i["severity"] for i in self.issues)
        return {
            "schema_version": 1,
            "counts": {k: counts[k] for k in ("ERROR", "WARNING", "OPTIONAL_MISSING")},
            "draft_valid": not counts["ERROR"],
            "publication_ready": False,
            "publication_prerequisites": [
                "Read-only database preview must confirm current approved catalog revisions.",
                "Import referenced prepared assets only after separate write authorization.",
                "Resolve errors and review every warning and educational activity.",
                "A real operator must review and explicitly authorize publication/activation.",
            ],
            "issues": self.issues,
        }

    def markdown(self):
        report = self.payload()
        lines = ["# Draft content quality", "", "Publication ready: **no**", ""]
        lines += [f"- {k}: {v}" for k, v in report["counts"].items()]
        lines += ["", "## Findings", ""]
        lines += [
            f"- {i['severity']} `{i['code']}` ({i['location']}): {i['message']}"
            for i in self.issues
        ]
        lines += ["", "## Publication prerequisites", ""]
        lines += [f"- {p}" for p in report["publication_prerequisites"]]
        return "\n".join(lines) + "\n"


def reviewed(item, report, location, *, operator_preview=False):
    review = item.review if hasattr(item, "review") else item.notes_review
    excluded = {"review", "notes_review"}
    payload = item.model_dump(mode="json", exclude=excluded)
    if review.status != "REVIEWED":
        if operator_preview:
            report.add(
                "ERROR",
                "HUMAN_REVIEW_REQUIRED",
                location,
                "Private review preview only: content remains UNREVIEWED; publication blocked.",
            )
            return True
        report.add("WARNING", "UNREVIEWED", location, "Omitted pending educational review.")
        return False
    if review.content_sha256 != checksum(payload):
        report.add("ERROR", "STALE_REVIEW", location, "Review does not bind these exact bytes.")
        return False
    return True


def normalized(value):
    return unicodedata.normalize("NFC", value).strip().casefold()


def ref_key(ref):
    return ref.vocabulary_id, ref.content_version


def asset_reference_id(asset):
    # Existing lesson contract has one UUID: bind it to stable source, version AND exact bytes.
    return uuid5(asset.id, f"{asset.version}:{asset.sha256}")


def validate_asset(asset, record, root, report, *, operator_preview=False):
    location = f"asset:{asset.id}"
    valid = reviewed(asset, report, location, operator_preview=operator_preview)

    def error(code, message):
        nonlocal valid
        valid = False
        report.add("ERROR", code, location, message)

    if asset.simplified != record.simplified:
        error(
            "ASSET_CHARACTER",
            "Asset must cover the exact ordered Simplified word, including repeats.",
        )
    if asset.purpose == "AUDIO":
        if asset.pinyin_numbered != record.pinyin_numbered:
            error(
                "AUDIO_PRONUNCIATION", "Audio must match the pinned pronunciation, including tones."
            )
        if asset.origin not in {"HUMAN_RECORDED", "TTS"}:
            error("AUDIO_ORIGIN", "Specify human recording or TTS honestly.")
        if asset.origin == "TTS" and not asset.provider:
            error(
                "TTS_PROVIDER",
                "TTS requires actual provider and reviewed deployment/license evidence.",
            )
    elif asset.origin not in {"AUTHORED", "DATASET"}:
        error("STROKE_ORIGIN", "Stroke assets require authored or dataset provenance.")
    if not asset.redistribution_allowed:
        error("ASSET_LICENSE", "Redistribution rights have not been confirmed.")
    root = Path(root).resolve()
    path = (root / asset.file).resolve()
    if not path.is_relative_to(root):
        error("ASSET_PATH", "Asset path escapes the supplied asset root.")
        return None
    try:
        if path.stat().st_size > 16_777_216:
            raise ContentError("asset exceeds Android's 16 MiB limit")
        data = path.read_bytes()
    except (OSError, ContentError):
        error("ASSET_MISSING", "Asset is absent, unreadable or too large.")
        return None
    if len(data) != asset.byte_length or hashlib.sha256(data).hexdigest() != asset.sha256:
        error("ASSET_INTEGRITY", "Length/SHA-256 differs from the versioned manifest.")
    media = asset.media_type
    if asset.purpose == "STRUCTURED_STROKES":
        try:
            strokes = StructuredStrokes.model_validate_json(data)
            if (
                media != "application/json"
                or "".join(c.character for c in strokes.characters) != record.simplified
            ):
                raise ValueError("character sequence mismatch")
            for character in strokes.characters:
                simplified_only(character.character)
        except ValueError:
            error("STROKE_DATA", "Invalid ordered stroke data or wrong character sequence.")
        report.add(
            "WARNING",
            "STRUCTURED_RENDERER_PENDING",
            location,
            "Prepared only; Android v1 cannot animate JSON. Supply a reviewed image/animation.",
        )
    else:
        signatures = {
            "audio/wav": data.startswith(b"RIFF") and data[8:12] == b"WAVE",
            "audio/mpeg": data.startswith(b"ID3")
            or (len(data) > 2 and data[0] == 255 and data[1] & 224 == 224),
            "audio/ogg": data.startswith(b"OggS") and (b"vorbis" in data or b"OpusHead" in data),
            "image/gif": data.startswith((b"GIF87a", b"GIF89a")) and data.endswith(b";"),
            "image/png": data.startswith(b"\x89PNG\r\n\x1a\n") and b"IEND" in data[-12:],
            "image/jpeg": data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9"),
        }
        allowed = (
            {"audio/wav", "audio/mpeg", "audio/ogg"}
            if asset.purpose == "AUDIO"
            else {"image/gif", "image/png", "image/jpeg"}
        )
        if media not in allowed or not signatures.get(media, False):
            error("ASSET_FORMAT", "Bytes/type do not match a supported Android format.")
        if media == "audio/ogg":
            from app.services.roadmap_media_validation import inspect_vorbis

            try:
                inspect_vorbis(data)
            except ValueError:
                error("AUDIO_FORMAT", "Ogg must contain a complete CRC-verified Vorbis stream.")
        if media == "audio/wav":
            try:
                with wave.open(io.BytesIO(data)) as audio:
                    frames = audio.getnframes()
                    if not (
                        frames and audio.getnchannels() in (1, 2) and audio.getframerate() >= 8000
                    ):
                        raise ValueError("unsupported WAV parameters")
                    if len(audio.readframes(frames)) != (
                        frames * audio.getnchannels() * audio.getsampwidth()
                    ):
                        raise ValueError("truncated audio")
            except (wave.Error, EOFError, ValueError):
                error("AUDIO_FORMAT", "WAV must contain complete playable PCM frames.")
    return data if valid else None


def component_content(items, record, report, location, *, operator_preview=False):
    result, seen, explanations = [], set(), {}
    for item in items:
        key = (item.character_position, item.component, item.position)
        if (
            item.character_position >= len(record.simplified)
            or record.simplified[item.character_position] != item.character
            or not all(is_hanzi(c) for c in item.component)
        ):
            report.add(
                "ERROR", "COMPONENT_CHARACTER", location, "Component targets the wrong character."
            )
            continue
        if key in seen:
            report.add(
                "ERROR",
                "COMPONENT_CONTRADICTION",
                location,
                "Duplicate/conflicting component slot.",
            )
            continue
        seen.add(key)
        explanation = normalized(item.explanation_vi)
        previous = explanations.get((item.character_position, explanation))
        if previous is not None and previous != item.role:
            report.add(
                "ERROR",
                "COMPONENT_CONTRADICTION",
                location,
                "Same explanation asserts conflicting roles.",
            )
            continue
        explanations[item.character_position, explanation] = item.role
        if reviewed(item, report, location, operator_preview=operator_preview):
            labels = {
                "MODERN_MNEMONIC": "Gợi nhớ hiện đại; không khẳng định nguồn gốc lịch sử",
                "ORIGIN_UNAVAILABLE": "Chưa có giải thích nguồn gốc lịch sử được xác minh",
                "HISTORICAL": "Giải thích lịch sử có nguồn",
            }
            text = f"{labels[item.interpretation]} ({item.position}): {item.explanation_vi}"
            if item.historical_source:
                text += f" — {item.historical_source}"
            result.append(
                {
                    "character_position": item.character_position,
                    "component": item.component,
                    "role": item.role,
                    "explanation": {"status": "AVAILABLE", "text": text},
                }
            )
    return result


def example_content(items, record, report, location, *, operator_preview=False):
    results = []
    for example in items:
        content = example.content
        start = example.target_character_position
        hanzi = "".join(c for c in content.simplified if is_hanzi(c))
        numbered = example.pinyin_numbered
        if (
            content.simplified[start : start + len(record.simplified)] != record.simplified
            or not re.fullmatch(r"[a-zü]+[1-5](?: [a-zü]+[1-5])*", numbered)
            or len(numbered.split()) != len(hanzi)
        ):
            report.add(
                "ERROR", "EXAMPLE_TARGET", location, "Example target/syllable identity is invalid."
            )
            continue
        syllable_start = sum(is_hanzi(c) for c in content.simplified[:start])
        if (
            " ".join(numbered.split()[syllable_start : syllable_start + len(record.simplified)])
            != record.pinyin_numbered
        ):
            report.add(
                "ERROR",
                "EXAMPLE_SENSE",
                location,
                "Target pronunciation differs from the catalog sense.",
            )
            continue
        pinyin_letters = lambda text: "".join(c.casefold() for c in text if c.isalpha())
        if pinyin_letters(tone_marks(numbered)) != pinyin_letters(content.pinyin):
            report.add(
                "ERROR",
                "EXAMPLE_PINYIN",
                location,
                "Tone-marked and numbered example Pinyin disagree.",
            )
            continue
        if example.difficulty > record.learning_level:
            report.add(
                "ERROR",
                "EXAMPLE_DIFFICULTY",
                location,
                "Example exceeds the target learning level.",
            )
            continue
        if example.audio:
            report.add(
                "ERROR",
                "EXAMPLE_AUDIO_UNSUPPORTED",
                location,
                "V1 has no per-example audio binding; omit or extend renderer first.",
            )
            continue
        if reviewed(example, report, location, operator_preview=operator_preview):
            results.append(f"{content.simplified}\n{content.pinyin}\n{content.vietnamese}")
    return "\n\n".join(results)


def quiz(kind, target, pool, count, activity_id, *, tone_distractors=False):
    """Conservative lexical ambiguity checks; human review still owns semantic correctness."""

    def answer(word):
        if kind == "PINYIN":
            return word.pinyin
        if kind == "WORD_TO_MEANING":
            return word.vietnamese_meanings[0]
        return word.simplified

    meanings = {normalized(v) for v in target.vietnamese_meanings}
    correct = answer(target)
    choices, used = [correct], {normalized(correct)}
    if kind == "PINYIN" and tone_distractors:
        if len(target.pinyin_numbered.split()) != 1 or count > 4:
            return None
        syllable = target.pinyin_numbered[:-1]
        alternatives = [tone_marks(syllable + str(tone)) for tone in range(1, 5)]
        alternatives = sorted(
            set(alternatives) - {correct}, key=lambda v: checksum([str(activity_id), v])
        )
        choices.extend(alternatives[: count - 1])
        pool = []
    for other in sorted(pool, key=lambda r: r.lexical_key):
        if (
            other.simplified == target.simplified
            or other.pinyin_numbered == target.pinyin_numbered
            or meanings.intersection(normalized(v) for v in other.vietnamese_meanings)
            or normalized(answer(other)) in used
        ):
            continue
        choices.append(answer(other))
        used.add(normalized(answer(other)))
        if len(choices) == count:
            break
    if len(choices) != count:
        return None
    choices.sort(key=lambda label: checksum([str(activity_id), label]))
    prompts = {
        "CHARACTER": f"Chọn từ có cách đọc {target.pinyin} ({target.vietnamese_meanings[0]}).",
        "PINYIN": f"Chọn Pinyin của {target.simplified} ({target.vietnamese_meanings[0]}).",
        "WORD_TO_MEANING": f"Chọn nghĩa của {target.simplified} ({target.pinyin}).",
        "MEANING_TO_WORD": f"Chọn từ có nghĩa: {target.vietnamese_meanings[0]}.",
    }
    return {
        "id": str(activity_id),
        "kind": "QUIZ",
        "required": True,
        "prompt": prompts[kind],
        "evaluation": "EXACT_CHOICE",
        "options": choices,
        "correct_option": choices.index(correct),
    }


def compile_drafts(plan: PreparationPlan, catalog, asset_root, *, operator_preview=False):
    report = QualityReport()
    selected = {}
    for group in plan.groups:
        for ref in group.vocabulary:
            record = catalog.get(ref.vocabulary_id)
            if record is None or record.content_version != ref.content_version:
                report.add(
                    "ERROR",
                    "CATALOG_REVISION",
                    str(ref.vocabulary_id),
                    "Missing exact curated revision.",
                )
            else:
                selected[ref.vocabulary_id] = record
    enrichment = {e.reference.vocabulary_id: e for e in plan.enrichments}
    assets, prepared = {}, []
    for asset in plan.assets:
        record = selected.get(asset.reference.vocabulary_id)
        if not record or record.content_version != asset.reference.content_version:
            report.add(
                "ERROR", "ASSET_REFERENCE", str(asset.id), "Asset targets an unselected revision."
            )
            continue
        data = validate_asset(asset, record, asset_root, report, operator_preview=operator_preview)
        slot = (asset.reference.vocabulary_id, asset.purpose)
        if slot in assets:
            report.add(
                "ERROR",
                "ASSET_DUPLICATE",
                str(asset.id),
                "Select one asset version per word/purpose.",
            )
            continue
        assets[slot] = asset if data is not None else None
        if data is not None:
            prepared.append((asset, data))
    nodes = []

    def activities(node_id, scope, pool, lesson, is_review):
        result = []

        def add(key, kind, prompt, **extra):
            result.append(dict(id=str(uuid5(node_id, key)), kind=kind, prompt=prompt, **extra))

        add(
            "introduction",
            "INTRODUCTION",
            "Đọc và ôn các từ." if is_review else "Đọc từ và nghĩa tiếng Việt.",
            required=not is_review or plan.templates.review_introduction_required,
        )
        if not is_review:
            if lesson.get("components") and plan.templates.components_activity:
                add("components", "COMPONENTS", "Đọc giải thích các thành phần chữ.")
            if lesson.get("stroke_order"):
                add("stroke-order", "STROKE_ORDER", "Quan sát thứ tự nét của toàn bộ từ.")
            if plan.templates.handwriting:
                add(
                    "handwriting", "HANDWRITING", "Viết tự do từng chữ; giữ nguyên các nét đã viết."
                )
            if plan.templates.pronunciation and lesson.get("audio"):
                add(
                    "pronunciation",
                    "PRONUNCIATION",
                    "Nghe mẫu rồi đọc lại; hoạt động chỉ ghi nhận tham gia.",
                    repetitions=plan.templates.pronunciation_repetitions,
                )
        for ref in scope:
            record = selected.get(ref.vocabulary_id)
            if record is None:
                continue
            quiz_kinds = (
                plan.templates.review_quizzes
                if is_review and plan.templates.review_quizzes is not None
                else plan.templates.quizzes
            )
            for kind in quiz_kinds:
                identifier = uuid5(node_id, f"quiz:{ref.vocabulary_id}:{kind}")
                activity = quiz(
                    kind,
                    record,
                    pool,
                    plan.templates.choice_count,
                    identifier,
                    tone_distractors=plan.templates.pinyin_tone_distractors,
                )
                if activity:
                    result.append(activity)
                else:
                    report.add(
                        "WARNING",
                        "QUIZ_DISTRACTORS",
                        str(identifier),
                        "Template omitted: insufficient unambiguous in-scope distractors.",
                    )
        return result

    for group in plan.groups:
        for offset in range(0, len(group.vocabulary), plan.review_interval):
            scope = group.vocabulary[offset : offset + plan.review_interval]
            pool = [selected[r.vocabulary_id] for r in scope if r.vocabulary_id in selected]
            for ref in scope:
                node_id = uuid5(plan.id, f"word:{ref.vocabulary_id}")
                record = selected.get(ref.vocabulary_id)
                lesson = {"vocabulary": [ref.model_dump(mode="json")]}
                location = str(ref.vocabulary_id)
                extra = enrichment.get(ref.vocabulary_id)
                if extra and ref_key(extra.reference) != ref_key(ref):
                    report.add(
                        "ERROR", "ENRICHMENT_REVISION", location, "Enrichment revision is stale."
                    )
                    extra = None
                if extra and record:
                    lesson["components"] = component_content(
                        extra.components,
                        record,
                        report,
                        location,
                        operator_preview=operator_preview,
                    )
                    examples = example_content(
                        extra.examples, record, report, location, operator_preview=operator_preview
                    )
                    if examples:
                        lesson["examples"] = {"status": "AVAILABLE", "text": examples}
                    if extra.notes_vi and reviewed(
                        extra, report, location, operator_preview=operator_preview
                    ):
                        lesson["notes"] = {"status": "AVAILABLE", "text": extra.notes_vi}
                for purpose, field in (("AUDIO", "audio"), ("STROKE_ORDER", "stroke_order")):
                    asset = assets.get((ref.vocabulary_id, purpose))
                    if asset:
                        lesson[field] = {
                            "status": "AVAILABLE",
                            "asset_id": str(asset_reference_id(asset)),
                        }
                for field in ("audio", "stroke_order", "components", "examples", "notes"):
                    if not lesson.get(field):
                        report.add(
                            "OPTIONAL_MISSING",
                            f"MISSING_{field.upper()}",
                            location,
                            f"No reviewed {field} supplied; explicitly omitted.",
                        )
                lesson["activities"] = activities(node_id, [ref], pool, lesson, False)
                nodes.append(
                    {
                        "id": str(node_id),
                        "position": len(nodes),
                        "node_type": "NEW_WORD",
                        "title": record.simplified if record else "Thiếu từ vựng",
                        "section": group.section,
                        "lesson": lesson,
                    }
                )
            # Include explicit group key and ordered stable identities, never revision in identity.
            review_id = uuid5(
                plan.id, f"review:{group.key}:" + ",".join(str(r.vocabulary_id) for r in scope)
            )
            lesson = {"vocabulary": [r.model_dump(mode="json") for r in scope]}
            lesson["activities"] = activities(review_id, scope, pool, lesson, True)
            nodes.append(
                {
                    "id": str(review_id),
                    "position": len(nodes),
                    "node_type": "REVIEW",
                    "title": "Ôn tập",
                    "section": group.section,
                    "lesson": lesson,
                }
            )
    definition = RoadmapDefinition.model_validate(
        {
            "id": plan.id,
            "code": plan.code,
            "version": plan.version,
            "title": plan.title,
            "review_interval": plan.review_interval,
            "nodes": nodes,
        }
    )
    report.add(
        "WARNING",
        "EDUCATIONAL_REVIEW",
        "roadmap",
        "Generated quizzes and activity requirements need individual operator review; automatic checks cannot verify translation, etymology or pronunciation quality.",
    )
    report.add(
        "WARNING",
        "DATABASE_BINDING_UNCHECKED",
        "catalog",
        "Filesystem identity/revisions verified; current database approval and revision must be checked using existing read-only preview before publication.",
    )
    return definition, report, prepared


def write_artifact(path, payload, immutable=False):
    """Atomic per-file checkpoints; reruns skip unchanged bytes and resume missing files."""
    path = Path(path)
    data = payload.encode() if isinstance(payload, str) else canonical(payload) + b"\n"
    if path.exists():
        if path.read_bytes() == data:
            return False
        if immutable:
            raise ContentError("version output differs; use a new roadmap version/output directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
    return True


def generation_manifest(plan, catalog, definition, prepared):
    payload = definition.model_dump(mode="json")
    selected_ids = {r.vocabulary_id for g in plan.groups for r in g.vocabulary}
    bindings = [
        {
            "vocabulary_id": str(identifier),
            "content_version": record.content_version,
            "checksum": record_checksum(record),
        }
        for identifier, record in sorted(catalog.items(), key=lambda pair: str(pair[0]))
        if identifier in selected_ids
    ]
    return {
        "compiler": COMPILER_VERSION,
        "plan_sha256": checksum(plan_fingerprint_payload(plan)),
        "definition_sha256": checksum(payload),
        "catalog_bindings": bindings,
        "asset_bindings": [a.model_dump(mode="json") for a, _ in prepared],
    }


def plan_fingerprint_payload(plan):
    payload = plan.model_dump(mode="json")
    # Preserve 6.3A immutable manifests when additive template options keep old behavior.
    for key, default in (
        ("review_quizzes", None),
        ("components_activity", True),
        ("review_introduction_required", True),
        ("pinyin_tone_distractors", False),
    ):
        if payload["templates"][key] == default:
            payload["templates"].pop(key)
    return payload


def prepared_asset_manifest(prepared):
    return [
        {
            "id": str(asset_reference_id(asset)),
            "storage_key": f"sha256/{asset.sha256}.json",
            "media_type": asset.media_type,
            "sha256": asset.sha256,
            "byte_length": asset.byte_length,
            "metadata": asset.model_dump(mode="json", exclude={"file"}),
        }
        for asset, _ in prepared
    ]


def legacy_asset_definition(asset):
    """Use the existing assets-only library importer, preserving provenance in the sidecar."""
    return AssetDefinition.model_validate(
        {
            "schema_version": 1,
            "id": asset["id"],
            "storage_key": asset["storage_key"],
            "media_type": asset["media_type"],
            "sha256": asset["sha256"],
            "byte_length": asset["byte_length"],
            "metadata": {"format": asset["media_type"]},
        }
    ).model_dump(mode="json")


def generate(plan, catalog, asset_root, output, *, operator_preview=False):
    definition, report, prepared = compile_drafts(
        plan, catalog, asset_root, operator_preview=operator_preview
    )
    output = Path(output)
    payload = definition.model_dump(mode="json")
    manifest = generation_manifest(plan, catalog, definition, prepared)
    if operator_preview:
        manifest["purpose"] = "OPERATOR_REVIEW_ONLY"
    # Reserve immutable input/content identity first. A crash can safely resume all remaining files.
    write_artifact(output / "manifest.json", manifest, immutable=True)
    write_artifact(output / "roadmap.json", payload, immutable=True)
    for node in payload["nodes"]:
        write_artifact(output / "lessons" / f"{node['id']}.json", node, immutable=True)
    storage = LocalContentStorage(output / "objects")
    asset_manifest = prepared_asset_manifest(prepared)
    for _, data in prepared:
        storage.put_bundle(data)
    write_artifact(output / "assets.json", asset_manifest, immutable=True)
    (output / "asset-library" / "assets").mkdir(parents=True, exist_ok=True)
    for asset in asset_manifest:
        write_artifact(
            output / "asset-library" / "assets" / f"{asset['id']}.json",
            legacy_asset_definition(asset),
            immutable=True,
        )
    write_artifact(output / "quality.json", report.payload())
    write_artifact(output / "quality.md", report.markdown())
    write_artifact(
        output / "missing-assets.json",
        [i for i in report.issues if i["severity"] == "OPTIONAL_MISSING"],
    )
    return definition, report


def validate_generated(plan, catalog, asset_root, output):
    expected, report, prepared = compile_drafts(plan, catalog, asset_root)
    output = Path(output)
    try:
        actual = RoadmapDefinition.model_validate(load_json(output / "roadmap.json"))
        manifest = load_json(output / "manifest.json")
        if actual != expected or manifest != generation_manifest(plan, catalog, expected, prepared):
            raise ContentError("generated content differs from bound authoring inputs")
        for node in actual.nodes:
            if load_json(output / "lessons" / f"{node.id}.json") != node.model_dump(mode="json"):
                raise ContentError("per-lesson checkpoint differs from roadmap")
        asset_manifest = load_json(output / "assets.json")
        if asset_manifest != prepared_asset_manifest(prepared):
            raise ContentError("prepared asset manifest differs from the reviewed inputs")
        from app.services.content_storage import verify_object

        for asset in asset_manifest:
            if load_json(
                output / "asset-library" / "assets" / f"{asset['id']}.json"
            ) != legacy_asset_definition(asset):
                raise ContentError("asset importer checkpoint differs from the prepared manifest")
            verify_object(
                LocalContentStorage(output / "objects"),
                asset["storage_key"],
                asset["sha256"],
                asset["byte_length"],
            )
    except (ValueError, OSError, KeyError, ContentError) as error:
        report.add("ERROR", "GENERATED_INTEGRITY", "output", str(error))
    return expected, report
