"""Package this session's manually authored records/notes; this script does not review.

Run once from backend with PYTHONPATH set. Existing evidence is never overwritten.
"""

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid5

from app.core.pinyin import tone_marks
from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_import import NAMESPACE, digest, record_checksum
from app.services.local_codex_review import ASPECTS, load_checkpoint

ROOT = Path(__file__).resolve().parent
SINO = dict(
    pair.split(":", 1)
    for pair in [
        "女:nữ",
        "口:khẩu",
        "男:nam",
        "中:trung",
        "左:tả",
        "右:hữu",
        "前:tiền",
        "后:hậu",
        "东:đông",
        "西:tây",
        "北:bắc",
        "百:bách",
        "千:thiên",
        "万:vạn",
        "两:lưỡng",
        "天:thiên",
        "分:phân",
        "早:tảo",
        "晚:vãn",
        "半:bán",
        "木:mộc",
        "金:kim",
        "土:thổ",
        "石:thạch",
        "田:điền",
        "雨:vũ",
        "电:điện",
        "气:khí",
        "面:diện",
        "肉:nhục",
        "虫:trùng",
        "鸡:kê",
        "鸭:áp",
        "猪:trư",
        "兔:thố",
        "龙:long",
        "鼠:thử",
        "虎:hổ",
        "蛇:xà",
        "牙:nha",
        "心:tâm",
        "皮:bì",
        "血:huyết",
        "见:kiến",
        "学:học",
        "答:đáp",
        "认:nhận",
        "站:trạm",
        "用:dụng",
        "打:đả",
        "让:nhượng",
        "帮:bang",
        "唱:xướng",
        "睡:thụy",
        "醒:tỉnh",
        "又:hựu",
        "最:tối",
        "被:bị",
        "杯:bôi",
        "瓶:bình",
        "元:nguyên",
        "角:giác",
        "里:lý",
        "坏:hoại",
        "轻:khinh",
        "重:trọng",
        "病:bệnh",
        "房:phòng",
        "窗:song",
        "床:sàng",
        "笔:bút",
        "纸:chỉ",
        "车:xa",
        "店:điếm",
        "名:danh",
        "课:khóa",
        "班:ban",
        "力:lực",
        "今:kim",
        "作:tác",
        "儿:nhi",
        "午:ngọ",
        "友:hữu",
        "喜:hỉ",
        "国:quốc",
        "子:tử",
        "孙:tôn",
        "工:công",
        "市:thị",
        "师:sư",
        "文:văn",
        "时:thời",
        "明:minh",
        "易:dị",
        "星:tinh",
        "昨:tạc",
        "朋:bằng",
        "校:hiệu",
        "桌:trác",
        "椅:ỷ",
        "欢:hoan",
        "汉:hán",
        "生:sinh",
        "目:mục",
        "眼:nhãn",
        "知:tri",
        "老:lão",
        "耳:nhĩ",
        "识:thức",
        "语:ngữ",
        "起:khởi",
        "足:túc",
        "身:thân",
        "道:đạo",
        "鼻:tị",
    ]
)
SINO.update(
    {
        "时间": "thời gian",
        "生日": "sinh nhật",
        "学校": "học hiệu",
        "中文": "trung văn",
        "汉字": "hán tự",
        "拼音": "bính âm",
        "声调": "thanh điệu",
        "发音": "phát âm",
        "越南": "việt nam",
        "河内": "hà nội",
        "英语": "anh ngữ",
        "越南语": "việt nam ngữ",
        "电话": "điện thoại",
        "地铁": "địa thiết",
        "汽车": "khí xa",
        "火车": "hỏa xa",
        "身体": "thân thể",
        "感冒": "cảm mạo",
        "今年": "kim niên",
        "白天": "bạch thiên",
        "以后": "dĩ hậu",
        "以前": "dĩ tiền",
        "复习": "phục tập",
        "作业": "tác nghiệp",
        "进入": "tiến nhập",
        "必须": "tất tu",
        "应该": "ưng cai",
        "可以": "khả dĩ",
        "可能": "khả năng",
        "可爱": "khả ái",
        "昂贵": "ngang quý",
        "快乐": "khoái lạc",
        "然后": "nhiên hậu",
        "不同": "bất đồng",
        "帮忙": "bang mang",
        "旅行": "lữ hành",
    }
)


def write_new(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def run():
    if (ROOT / "checkpoint").exists() or (ROOT / "original-zhvi").exists():
        raise ValueError("Refusing to overwrite source/checkpoint evidence")
    scan = json.loads((ROOT / "coverage-scan.json").read_text(encoding="utf-8"))
    missing = {w for values in scan["missing_forms"].values() for w in values}
    core = set(scan["candidate_groups"]["characters"])
    advanced = {"昂贵", "膝盖", "胳膊", "喜", "目", "耳", "足", "作", "识", "道"}
    records, notes, seen = [], {}, set()
    for line in (ROOT / "authored.psv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        form, numbered, meaning, pos, chinese, pinyin, vietnamese, note = line.split("|")
        assert form in missing and form not in seen
        seen.add(form)
        record = CuratedRecord(
            schema_version=1,
            lexical_key=form + "|" + numbered,
            simplified=form,
            pinyin=tone_marks(numbered),
            pinyin_numbered=numbered,
            sino_vietnamese=SINO.get(form),
            part_of_speech=pos,
            learning_level=2 if form in advanced else 0 if form in core else 1,
            review_status="GENERATED_UNREVIEWED",
            content_version=1,
            vietnamese_meanings=meaning.split("; "),
            examples=[{"simplified": chinese, "pinyin": pinyin, "vietnamese": vietnamese}],
        )
        assert form in chinese, "Headword must occur in its example: " + form
        records.append(record)
        notes[record.lexical_key] = note
    assert seen == missing and len(records) == 322
    timestamp = datetime.now(UTC).isoformat()
    generator = {
        "author_label": "Codex session",
        "author_model": None,
        "author_version": None,
        "method": "Manually composed in the active Codex conversation; not Gemini output",
        "source": "authored.psv",
        "source_sha256": digest((ROOT / "authored.psv").read_bytes()),
        "review": "All fields/examples and individual notes assessed by this same session; no independent model claimed",
        "timestamp": timestamp,
        "paid_api_calls": 0,
    }
    batches = []
    for level in range(3):
        selected = [r for r in records if r.learning_level == level]
        for index, offset in enumerate(range(0, len(selected), 50), start=1):
            batch_records = selected[offset : offset + 50]
            key = f"L{level}-B{index:03}"
            filename = f"level-{level}-batch-{index:03}.authored.jsonl"
            payload = "\n".join(r.model_dump_json() for r in batch_records) + "\n"
            sha = digest(payload.encode("utf-8"))
            write_new(ROOT / "original-zhvi" / filename, payload)
            write_new(ROOT / "checkpoint" / key / "deployment.jsonl", payload)
            findings = [
                {
                    "lexical_key": r.lexical_key,
                    "id": str(uuid5(NAMESPACE, r.lexical_key)),
                    "source_content_version": 1,
                    "source_checksum": record_checksum(r),
                    "reviewed_content_version": 1,
                    "reviewed_checksum": record_checksum(r),
                    "linguistic_outcome": "PASS",
                    "checked_aspects": sorted(ASPECTS),
                    "note": notes[r.lexical_key],
                    "correction": None,
                    "pending_reason": None,
                    "local_development_candidate": True,
                    "eligible_for_AI_APPROVED": False,
                    "evidence_limitations": [
                        "Same-session authoring/review; no authenticated provider receipt or exact model snapshot",
                        "Optional Sino-Vietnamese omitted where not confidently verified",
                    ],
                }
                for r in batch_records
            ]
            batch_notes = {
                "artifact_kind": "CODEX_SESSION_LINGUISTIC_NOTES_NOT_REVIEWRESULT",
                "batch": key,
                "source_file": filename,
                "source_sha256": sha,
                "deployment_sha256": sha,
                "checkpoint_written_at": timestamp,
                "reviewer_label": "Codex session",
                "reviewer_model": None,
                "reviewer_version": None,
                "confidence": None,
                "paid_api_calls": 0,
                "scope": "Session-authored supplementary entries; every field and complete example reviewed",
                "supporting_sources": [
                    "https://dict.concised.moe.edu.tw/dictView.jsp?ID=1450&la=0&powerMode=0"
                ]
                if any(r.simplified == "别人" for r in batch_records)
                else [],
                "author_provenance": generator,
                "records": findings,
            }
            write_new(
                ROOT / "checkpoint" / key / "review-notes.json",
                json.dumps(batch_notes, ensure_ascii=False, indent=2) + "\n",
            )
            batches.append(
                {"batch_key": key, "artifact_file": filename, "records_count": len(batch_records)}
            )
    write_new(
        ROOT / "original-zhvi" / "coverage-manifest.json",
        json.dumps(
            {
                "provenance": generator,
                "scope": "322 missing beginner words/character elements from a bounded 709-form audit",
                "batches": batches,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write_new(
        ROOT / "source-provenance.json", json.dumps(generator, ensure_ascii=False, indent=2) + "\n"
    )
    write_new(ROOT / "supplement.jsonl", "\n".join(r.model_dump_json() for r in records) + "\n")
    accepted, _evidence, coverage = load_checkpoint(ROOT / "checkpoint")
    assert len(accepted) == 322 and coverage["unreviewed"] == 0 and not coverage["excluded"]
    write_new(
        ROOT / "validation.json",
        json.dumps(
            {
                "coverage": coverage,
                "levels": dict(Counter(r.learning_level for r in accepted)),
                "bytes_sha256": digest((ROOT / "supplement.jsonl").read_bytes()),
                "database_writes": 0,
                "production_AI_APPROVED_created": 0,
                "authored_and_reviewed_by_same_session": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    print(
        json.dumps(
            {
                "reviewed": len(accepted),
                "batches": len(batches),
                "levels": dict(Counter(r.learning_level for r in accepted)),
                "excluded": 0,
                "database_writes": 0,
            }
        )
    )


if __name__ == "__main__":
    run()
