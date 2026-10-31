"""Reproduce and mechanically validate the original, unapproved L0-B001 draft.

Standard library only. No database, network, existing dictionary or app imports.
Run from any directory with Python 3.11+; output stays beside this script.
"""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata as ud
from uuid import NAMESPACE_URL, UUID, uuid5


ROOT = Path(__file__).resolve().parent
# Fixed application namespace; never change after allocating lexical keys.
NAMESPACE = uuid5(NAMESPACE_URL, "urn:chineselearningapp:original-zhvi:lexemes:v1")

# Original authoring rows, not sourced from an external dictionary.
# simplified | traditional | marked | numbered | Sino-Vietnamese (empty=null)
# | POS | Vietnamese | Chinese example | marked example | numbered example | Vietnamese example
ROWS = """你好|你好|nǐ hǎo|ni3 hao3||phrase|xin chào|你好！|Nǐ hǎo!|ni3 hao3|Xin chào!
您好|您好|nín hǎo|nin2 hao3||phrase|xin chào (lịch sự)|您好！|Nín hǎo!|nin2 hao3|Cháu chào bác ạ!
再见|再見|zàijiàn|zai4 jian4||phrase|tạm biệt|再见！|Zàijiàn!|zai4 jian4|Tạm biệt!
谢谢|謝謝|xièxie|xie4 xie5||phrase|cảm ơn|谢谢你！|Xièxie nǐ!|xie4 xie5 ni3|Cảm ơn bạn!
不客气|不客氣|bù kèqi|bu4 ke4 qi5||phrase|không có gì (đáp lời cảm ơn)|不客气！|Bù kèqi!|bu4 ke4 qi5|Không có gì!
对不起|對不起|duìbuqǐ|dui4 bu5 qi3||phrase|xin lỗi|对不起！|Duìbuqǐ!|dui4 bu5 qi3|Xin lỗi!
没关系|沒關係|méi guānxi|mei2 guan1 xi5||phrase|không sao (đáp lời xin lỗi)|没关系！|Méi guānxi!|mei2 guan1 xi5|Không sao đâu!
请|請|qǐng|qing3|thỉnh|verb|mời; xin (dùng để đề nghị lịch sự)|请喝茶。|Qǐng hē chá.|qing3 he1 cha2|Mời bạn uống trà.
我|我|wǒ|wo3|ngã|pronoun|tôi; mình|我在家。|Wǒ zài jiā.|wo3 zai4 jia1|Tôi ở nhà.
你|你|nǐ|ni3|nhĩ|pronoun|bạn; cậu (ngôi thứ hai số ít)|你喝茶吗？|Nǐ hē chá ma?|ni3 he1 cha2 ma5|Bạn có uống trà không?
您|您|nín|nin2||pronoun|ông; bà; anh; chị (cách xưng hô lịch sự)|您请。|Nín qǐng.|nin2 qing3|Xin mời ông/bà.
他|他|tā|ta1|tha|pronoun|anh ấy; ông ấy; cậu ấy|他在家。|Tā zài jiā.|ta1 zai4 jia1|Anh ấy ở nhà.
她|她|tā|ta1||pronoun|cô ấy; bà ấy; chị ấy|她喝水。|Tā hē shuǐ.|ta1 he1 shui3|Cô ấy uống nước.
我们|我們|wǒmen|wo3 men5||pronoun|chúng tôi; chúng ta|我们去。|Wǒmen qù.|wo3 men5 qu4|Chúng tôi đi.
你们|你們|nǐmen|ni3 men5||pronoun|các bạn; các anh; các chị|你们来吗？|Nǐmen lái ma?|ni3 men5 lai2 ma5|Các bạn có đến không?
这|這|zhè|zhe4||pronoun|đây; này (chỉ người hoặc vật ở gần)|这是水。|Zhè shì shuǐ.|zhe4 shi4 shui3|Đây là nước.
那|那|nà|na4||pronoun|kia; đó (chỉ người hoặc vật ở xa hơn)|那是茶。|Nà shì chá.|na4 shi4 cha2|Kia là trà.
谁|誰|shéi|shei2||pronoun|ai|他是谁？|Tā shì shéi?|ta1 shi4 shei2|Anh ấy là ai?
什么|什麼|shénme|shen2 me5||pronoun|gì; cái gì|这是什么？|Zhè shì shénme?|zhe4 shi4 shen2 me5|Đây là cái gì?
零|零|líng|ling2|linh|numeral|số không|这是零。|Zhè shì líng.|zhe4 shi4 ling2|Đây là số không.
一|一|yī|yi1|nhất|numeral|một|一加一是二。|Yī jiā yī shì èr.|yi1 jia1 yi1 shi4 er4|Một cộng một bằng hai.
二|二|èr|er4|nhị|numeral|hai (số đếm)|一加一是二。|Yī jiā yī shì èr.|yi1 jia1 yi1 shi4 er4|Một cộng một bằng hai.
三|三|sān|san1|tam|numeral|ba|一加二是三。|Yī jiā èr shì sān.|yi1 jia1 er4 shi4 san1|Một cộng hai bằng ba.
四|四|sì|si4|tứ|numeral|bốn|二加二是四。|Èr jiā èr shì sì.|er4 jia1 er4 shi4 si4|Hai cộng hai bằng bốn.
五|五|wǔ|wu3|ngũ|numeral|năm (số đếm)|二加三是五。|Èr jiā sān shì wǔ.|er4 jia1 san1 shi4 wu3|Hai cộng ba bằng năm.
六|六|liù|liu4|lục|numeral|sáu|三加三是六。|Sān jiā sān shì liù.|san1 jia1 san1 shi4 liu4|Ba cộng ba bằng sáu.
七|七|qī|qi1|thất|numeral|bảy|三加四是七。|Sān jiā sì shì qī.|san1 jia1 si4 shi4 qi1|Ba cộng bốn bằng bảy.
八|八|bā|ba1|bát|numeral|tám|四加四是八。|Sì jiā sì shì bā.|si4 jia1 si4 shi4 ba1|Bốn cộng bốn bằng tám.
九|九|jiǔ|jiu3|cửu|numeral|chín|四加五是九。|Sì jiā wǔ shì jiǔ.|si4 jia1 wu3 shi4 jiu3|Bốn cộng năm bằng chín.
十|十|shí|shi2|thập|numeral|mười|五加五是十。|Wǔ jiā wǔ shì shí.|wu3 jia1 wu3 shi4 shi2|Năm cộng năm bằng mười.
是|是|shì|shi4|thị|verb|là|这是茶。|Zhè shì chá.|zhe4 shi4 cha2|Đây là trà.
不|不|bù|bu4|bất|adverb|không (phủ định)|我不去。|Wǒ bù qù.|wo3 bu4 qu4|Tôi không đi.
有|有|yǒu|you3|hữu|verb|có|我有水。|Wǒ yǒu shuǐ.|wo3 you3 shui3|Tôi có nước.
没有|沒有|méiyǒu|mei2 you3||verb|không có|我没有茶。|Wǒ méiyǒu chá.|wo3 mei2 you3 cha2|Tôi không có trà.
好|好|hǎo|hao3|hảo|adjective|tốt; ổn; khỏe (khi nói về tình trạng sức khỏe)|我很好。|Wǒ hěn hǎo.|wo3 hen3 hao3|Tôi khỏe.
吗|嗎|ma|ma5||particle|trợ từ cuối câu hỏi có/không|你去吗？|Nǐ qù ma?|ni3 qu4 ma5|Bạn có đi không?
呢|呢|ne|ne5||particle|trợ từ dùng khi hỏi lại về người hoặc việc vừa nhắc đến|我喝茶，你呢？|Wǒ hē chá, nǐ ne?|wo3 he1 cha2 ni3 ne5|Tôi uống trà, còn bạn thì sao?
的|的|de|de5||particle|của (đánh dấu quan hệ sở hữu trong bài này)|这是我的。|Zhè shì wǒ de.|zhe4 shi4 wo3 de5|Đây là của tôi.
在|在|zài|zai4|tại|verb|ở; có mặt tại|我在家。|Wǒ zài jiā.|wo3 zai4 jia1|Tôi ở nhà.
人|人|rén|ren2|nhân|noun|người|那里有人。|Nàli yǒu rén.|na4 li5 you3 ren2|Ở đó có người.
水|水|shuǐ|shui3|thủy|noun|nước|我喝水。|Wǒ hē shuǐ.|wo3 he1 shui3|Tôi uống nước.
茶|茶|chá|cha2|trà|noun|trà; chè (đồ uống)|请喝茶。|Qǐng hē chá.|qing3 he1 cha2|Mời bạn uống trà.
米饭|米飯|mǐfàn|mi3 fan4||noun|cơm (cơm nấu từ gạo)|我吃米饭。|Wǒ chī mǐfàn.|wo3 chi1 mi3 fan4|Tôi ăn cơm.
吃|吃|chī|chi1||verb|ăn|你吃什么？|Nǐ chī shénme?|ni3 chi1 shen2 me5|Bạn ăn gì?
喝|喝|hē|he1||verb|uống|你喝什么？|Nǐ hē shénme?|ni3 he1 shen2 me5|Bạn uống gì?
要|要|yào|yao4||verb|muốn; muốn lấy (khi yêu cầu thứ gì)|我要水。|Wǒ yào shuǐ.|wo3 yao4 shui3|Tôi muốn lấy nước.
去|去|qù|qu4|khứ|verb|đi (rời chỗ đang nói hoặc hướng đến nơi khác)|我去。|Wǒ qù.|wo3 qu4|Tôi đi.
来|來|lái|lai2|lai|verb|đến; tới (hướng về chỗ người nói hoặc điểm quy chiếu)|你来吗？|Nǐ lái ma?|ni3 lai2 ma5|Bạn có đến không?
家|家|jiā|jia1|gia|noun|nhà; gia đình|我在家。|Wǒ zài jiā.|wo3 zai4 jia1|Tôi ở nhà.
厕所|廁所|cèsuǒ|ce4 suo3||noun|nhà vệ sinh|厕所在哪儿？|Cèsuǒ zài nǎr?|ce4 suo3 zai4 nar3|Nhà vệ sinh ở đâu?
"""

# Explicit inventory for this batch only, manually authored, not a complete
# Mandarin syllable standard or independent linguistic authority.
SYLLABLES = set("ni hao nin zai jian xie bu ke qi dui mei guan xi qing wo ta men zhe na shei shui shen me ling yi er san si wu liu ba jiu shi you ma ne de ren he cha mi fan chi yao qu lai jia ce suo hen nar li".split())
TONES = {v: marks for v, marks in zip("aeiouü", ("āáǎà", "ēéěè", "īíǐì", "ōóǒò", "ūúǔù", "ǖǘǚǜ"))}
POS = {"noun", "pronoun", "verb", "adjective", "adverb", "numeral", "classifier", "preposition", "conjunction", "particle", "interjection", "phrase"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def mark(token):
    match = re.fullmatch(r"([a-zü]+)([1-5])", token)
    assert match, f"Invalid numbered syllable: {token}"
    base, tone = match[1], int(match[2])
    assert base in SYLLABLES, f"Outside batch inventory: {base}"
    if tone == 5:
        return base
    if "a" in base:
        index = base.index("a")
    elif "e" in base:
        index = base.index("e")
    elif "ou" in base:
        index = base.index("o")
    else:
        index = max(i for i, ch in enumerate(base) if ch in TONES)
    return base[:index] + TONES[base[index]][tone - 1] + base[index + 1:]


def letters(value):
    return "".join(ch.lower() for ch in value if ud.category(ch).startswith("L"))


def issue(code, path, explanation):
    return {"code": code, "path": path, "explanation": explanation, "blocking": True}


def build_records():
    records = []
    for line in ROWS.strip().splitlines():
        s, t, py, numbered, sv, pos, vi, ex, ex_py, ex_num, ex_vi = line.split("|")
        seed = canonical(["zhvi-curated-v1", s, numbered, 1])
        notes = []
        findings = []
        if s in {"不客气", "没关系"}:
            findings.append(issue("NEUTRAL_TONE_VARIATION", "/readings/0", "Draft uses a neutral final syllable. A human must confirm this teaching choice and whether to add a full-tone regional or careful-speech variant."))
        if s == "谁":
            findings.append(issue("READING_VARIANT_POLICY", "/readings", "Both shéi and shuí are represented. Human review must confirm primary-reading selection and beginner presentation."))
        if s in {"一", "不", "你好", "您好", "对不起", "不客气", "好", "有", "水", "五", "九"}:
            notes.append("Pinyin records citation tones, not contextual tone sandhi. Spoken realization needs separate instruction.")
        if not sv:
            notes.append("Sino-Vietnamese is intentionally null: no useful conventional lexical reading is asserted; this does not assert that the characters lack historical readings.")
        if s == "什么":
            notes.append("什麼 is the selected primary traditional form; 甚麼 is retained as a written variant. Regional preference needs human review.")
        if s == "请":
            notes.append("Verb label covers inviting/requesting; the example teaches polite 请 + verb, not every usage.")
        if s == "要":
            notes.append("Only the request/want sense of yào is introduced. Other senses and yāo are outside this entry revision. Requests may need 请 or 谢谢 for politeness.")
        if s in {"好", "的", "在", "没有", "呢"}:
            notes.append("Only the displayed beginner sense and grammatical use are introduced; other readings or functions are not implied.")
        if s == "您":
            notes.append("Vietnamese address terms depend on relationship and age; ông/bà are illustrative alternatives, not a fixed equivalence.")
        forms = [{"key": "f-simp", "script": "SIMPLIFIED", "text": s, "primary": True, "usage_note": None}, {"key": "f-trad", "script": "TRADITIONAL", "text": t, "primary": True, "usage_note": None}]
        if s == "什么":
            forms.append({"key": "f-trad-alt", "script": "TRADITIONAL", "text": "甚麼", "primary": False, "usage_note": "Written variant; regional preference pending human review."})
            findings.append(issue("TRADITIONAL_VARIANT_POLICY", "/forms", "Human reviewer must confirm the chosen traditional-form preference and regional usage notes for 什麼 / 甚麼."))
        readings = [{"key": "r1", "pinyin": py, "pinyin_numbered": numbered, "sino_vietnamese": sv or None, "primary": True, "usage_note": None}]
        if s == "谁":
            readings.append({"key": "r2", "pinyin": "shuí", "pinyin_numbered": "shui2", "sino_vietnamese": None, "primary": False, "usage_note": "Alternative reading; primary teaching preference pending human review."})
        records.append({
            "schema_version": 1,
            "key": "cv_" + str(uuid5(NAMESPACE, seed)),
            "identity_seed": seed,
            "revision": 1,
            "supersedes_revision": None,
            "provenance": "ORIGINAL_AI_AUTHORED",
            "forms": forms,
            "readings": readings,
            "senses": [{"key": "s1", "part_of_speech": pos, "meanings_vi": [meaning.strip() for meaning in vi.split(";")], "meanings_en": [], "reading_keys": [r["key"] for r in readings], "usage_note": None}],
            "classification": {"learning_level": 0, "classification_standard": "APP_CURATED", "difficulty_reference": "HSK_2_0", "hsk_reference_level": None, "membership_evidence": None, "review_required": False, "rationale": "Application-defined introductory vocabulary for immediate communication; no official HSK membership is asserted."},
            "examples": [{"key": "e1", "sense_key": "s1", "reading_key": "r1", "chinese": ex, "pinyin": ex_py, "pinyin_numbered": ex_num, "vietnamese": ex_vi, "editorial_note": None}],
            "review_status": "NEEDS_REVIEW" if findings else "GENERATED_UNREVIEWED",
            "review_issues": findings,
            "editorial_notes": " ".join(notes) or None,
        })
    return records


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON object key: {key}"
        result[key] = value
    return result


def validate(data):
    assert not data.startswith(b"\xef\xbb\xbf"), "Unexpected BOM"
    text = data.decode("utf-8", errors="strict")
    assert text.endswith("\n")
    assert ud.normalize("NFC", text) == text
    assert all(ud.category(c) not in {"Cc", "Cf"} or c == "\n" for c in text)
    lines = text.splitlines()
    assert len(lines) == 50 and all(lines)
    records = [json.loads(line, object_pairs_hook=reject_duplicate_keys) for line in lines]
    expected = set(build_records()[0])
    keys, seeds, fingerprints = set(), set(), set()
    for record in records:
        assert set(record) == expected
        assert record["schema_version"] == 1 and type(record["schema_version"]) is int
        assert record["revision"] == 1 and type(record["revision"]) is int
        assert record["supersedes_revision"] is None
        assert record["provenance"] == "ORIGINAL_AI_AUTHORED"
        key, seed = record["key"], record["identity_seed"]
        assert key == "cv_" + str(uuid5(NAMESPACE, seed))
        assert UUID(key[3:]).version == 5
        assert key not in keys and seed not in seeds
        keys.add(key)
        seeds.add(seed)
        forms = record["forms"]
        assert len({f["key"] for f in forms}) == len(forms)
        for f in forms:
            assert set(f) == {"key", "script", "text", "primary", "usage_note"}
            assert f["script"] in {"SIMPLIFIED", "TRADITIONAL"}
            assert type(f["primary"]) is bool
            assert f["text"] and all("\u3400" <= c <= "\u9fff" for c in f["text"])
        assert len({(f["script"], f["text"]) for f in forms}) == len(forms)
        for script in ("SIMPLIFIED", "TRADITIONAL"):
            assert sum(f["primary"] for f in forms if f["script"] == script) == 1
        readings = record["readings"]
        assert sum(r["primary"] for r in readings) == 1
        assert len({r["key"] for r in readings}) == len(readings)
        assert len({r["pinyin_numbered"] for r in readings}) == len(readings)
        simplified = next(f["text"] for f in forms if f["script"] == "SIMPLIFIED" and f["primary"])
        primary = next(r for r in readings if r["primary"])
        assert seed == canonical(["zhvi-curated-v1", simplified, primary["pinyin_numbered"], 1])
        for r in readings:
            assert set(r) == {"key", "pinyin", "pinyin_numbered", "sino_vietnamese", "primary", "usage_note"}
            assert r["sino_vietnamese"] is None or isinstance(r["sino_vietnamese"], str) and r["sino_vietnamese"].strip()
            assert type(r["primary"]) is bool
            fp = (simplified, r["pinyin_numbered"])
            assert fp not in fingerprints
            fingerprints.add(fp)
        c = record["classification"]
        assert set(c) == {"learning_level", "classification_standard", "difficulty_reference", "hsk_reference_level", "membership_evidence", "review_required", "rationale"}
        assert c["learning_level"] == 0 and type(c["learning_level"]) is int
        assert c["classification_standard"] == "APP_CURATED"
        assert c["difficulty_reference"] == "HSK_2_0"
        assert c["hsk_reference_level"] is None and c["membership_evidence"] is None
        assert type(c["review_required"]) is bool and c["rationale"].strip()
        senses = record["senses"]
        assert senses and len({s["key"] for s in senses}) == len(senses)
        for s in senses:
            assert set(s) == {"key", "part_of_speech", "meanings_vi", "meanings_en", "reading_keys", "usage_note"}
            assert s["part_of_speech"] in POS
            assert s["meanings_vi"] and all(isinstance(v, str) and v.strip() for v in s["meanings_vi"])
            assert isinstance(s["meanings_en"], list)
            assert all(isinstance(v, str) and v.strip() for v in s["meanings_en"])
            assert s["reading_keys"] and set(s["reading_keys"]) <= {r["key"] for r in readings}
        examples = record["examples"]
        assert 1 <= len(examples) <= 2
        assert len({e["key"] for e in examples}) == len(examples)
        for e in examples:
            assert set(e) == {"key", "sense_key", "reading_key", "chinese", "pinyin", "pinyin_numbered", "vietnamese", "editorial_note"}
            sense = next(s for s in senses if s["key"] == e["sense_key"])
            assert e["reading_key"] in sense["reading_keys"]
            assert simplified in e["chinese"]
            assert e["vietnamese"].strip()
            assert all("\u3400" <= ch <= "\u9fff" or ch in "。！？，、；：" for ch in e["chinese"])
        for item in [*readings, *examples]:
            tokens = item["pinyin_numbered"].split(" ")
            assert tokens and all(tokens)
            assert letters(item["pinyin"]) == "".join(mark(t) for t in tokens), item
        assert record["review_status"] in {"GENERATED_UNREVIEWED", "NEEDS_REVIEW"}
        assert (record["review_status"] == "NEEDS_REVIEW") == bool(record["review_issues"])
        assert record["editorial_notes"] is None or isinstance(record["editorial_notes"], str)
        for finding in record["review_issues"]:
            assert set(finding) == {"code", "path", "explanation", "blocking"}
            assert finding["code"] and finding["explanation"] and type(finding["blocking"]) is bool
            target = record
            for part in finding["path"].split("/")[1:]:
                target = target[int(part)] if isinstance(target, list) else target[part]
    return records


def main():
    records = build_records()
    data = ("\n".join(canonical(r) for r in records) + "\n").encode("utf-8")
    records = validate(data)
    artifact = ROOT / "level-0-batch-001.jsonl"
    artifact.write_bytes(data)
    # Validate the actual disk artifact, not only the in-memory serialization.
    records = validate(artifact.read_bytes())
    digest = sha256(artifact.read_bytes()).hexdigest()
    counts = dict(Counter(r["review_status"] for r in records))
    registry = {
        "schema_version": 1, "namespace_uuid": str(NAMESPACE),
        "namespace_derivation": "UUIDv5(NAMESPACE_URL, urn:chineselearningapp:original-zhvi:lexemes:v1)",
        "seed_serialization": "NFC JSON array; ensure_ascii=false; separators=(',', ':'); no trailing newline; UUIDv5 UTF-8 encoding",
        "scope": "Original catalog L0-B001 only; existing third-party dictionary was not read or compared.",
        "entries": [{"key": r["key"], "identity_seed": r["identity_seed"], "batch_key": "L0-B001", "revision": 1} for r in records],
    }
    manifest = {
        "schema_version": 1, "batch_key": "L0-B001", "learning_level": 0,
        "batch_number": 1, "expected_count": 50, "actual_count": len(records),
        "provenance": "ORIGINAL_AI_AUTHORED", "classification_standard": "APP_CURATED",
        "difficulty_reference": "HSK_2_0", "namespace_uuid": str(NAMESPACE),
        "lexical_keys": [r["key"] for r in records],
        "artifact_file": artifact.name, "artifact_sha256": digest,
        "artifact_bytes": len(data), "encoding": "UTF-8", "unicode_normalization": "NFC",
        "line_endings": "LF", "structural_validation": "PASSED",
        "linguistic_review": "PENDING", "human_approved_count": 0,
        "review_status_counts": counts,
        "example_count": sum(len(r["examples"]) for r in records),
        "coverage_notes": [
            "Eight greeting/politeness expressions; seven personal pronouns; four demonstrative/interrogative entries; eleven numerals; twenty everyday entries.",
            "One short original example per entry; examples may share elementary patterns.",
            "Citation-tone Pinyin throughout; no contextual tone-sandhi transcription is claimed.",
            "Examples introduce support vocabulary 很, 加, 哪儿, 那里; teach these with example glosses before exercises.",
            "Not an exhaustive Level 0 or official HSK list. No database connection, import, publication, audio or stroke-order assets.",
        ],
    }
    for name, value in (("level-0-batch-001.manifest.json", manifest), ("lexical-key-registry.json", registry)):
        (ROOT / name).write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    findings = []
    for r in records:
        form = next(f["text"] for f in r["forms"] if f["script"] == "SIMPLIFIED" and f["primary"])
        for finding in r["review_issues"]:
            findings.append(f"- {form} ({r['key']}): `{finding['code']}` at `{finding['path']}` — {finding['explanation']}")
    report = f"""# Level 0 — Batch 001 validation report

Artifact: `{artifact.name}`. Schema version: 1. Application level: 0.

## Executed mechanical checks

- PASS: strict UTF-8 without BOM, NFC, LF, final newline, no blank records or control/format characters.
- PASS: exactly {len(records)} parsed JSON objects; duplicate JSON object properties rejected.
- PASS: required and unexpected fields, batch-specific types, supported POS and classification values.
- PASS: 50 distinct UUIDv5 lexical keys and frozen identity seeds; deterministic recomputation.
- PASS: no duplicate simplified-form/numbered-reading candidates within this original batch, including alternate readings.
- PASS: primary forms/readings, unique local keys, Vietnamese meanings, sense/reading/example references.
- PASS: one example per entry ({sum(len(r['examples']) for r in records)} total); target Hanzi occurs in each example.
- PASS: Hanzi-only forms in the batch's supported BMP range; example punctuation allow-list.
- PASS: numbered-Pinyin tokens use tones 1–5 and belong to an explicitly authored batch syllable inventory.
- PASS: deterministic tone-mark rendering agrees with supplied marked Pinyin, ignoring case, word spacing and punctuation.
- PASS: review issue paths resolve; flagged entries use NEEDS_REVIEW; no HUMAN_APPROVED records.
- PASS: all official HSK membership and evidence values are null.
- PASS: re-read and revalidated the actual on-disk JSONL; computed SHA-256 from its exact bytes.

Review counts: `{json.dumps(counts, ensure_ascii=False)}`.

SHA-256: `{digest}`

These checks are implemented in `build_batch_001.py` using only the Python standard library. They do not load application configuration, access the network, read third-party dictionaries or connect to PostgreSQL. The validator is scoped to this batch; it is not a complete general JSON Schema or Mandarin pronunciation validator.

## Blocking editorial findings

{chr(10).join(findings)}

## Human review still required for all 50 entries

No bilingual human review has occurred. Mechanically agreeing Pinyin fields can still share a wrong reading. Hanzi range checks do not prove word validity or simplified/traditional equivalence. Target-string matching does not prove sense alignment, word boundaries or grammatical correctness. The syllable inventory is manually authored and does not independently establish pronunciation correctness.

Review Mandarin grammar, example/Pinyin alignment, neutral-tone and regional variants, traditional forms, natural Vietnamese meanings and address terms, conventional Sino-Vietnamese readings, POS, sense boundaries and Level 0 suitability. Null Sino-Vietnamese fields mean no useful lexical reading is asserted, not that historical character readings are absent. Non-null Sino-Vietnamese readings also remain unapproved.

The whole batch uses citation tones. In particular 一, 不 and adjacent third tones may sound different in connected speech. No sandhi pronunciation or audio is supplied. Numerical examples introduce 加; other examples introduce 很, 哪儿 and 那里, which need glosses or prior explanation. Repeated elementary arithmetic patterns across number entries are intentional; examples are not claimed to be unique sentences across the catalog.

The registry covers this original batch only. No previous original batches were found in this workspace search. No duplicate comparison with the existing imported dictionary was performed; that dictionary was deliberately not used as a content source. Original AI authoring does not guarantee that ordinary expressions or short sentences never coincide with existing publications.

Publication remains blocked for every entry until an authenticated human approves the exact revision. This batch is a separate staging artifact, incompatible with the existing content importer until an explicit reviewed adapter is implemented. No database migration, import, release, SRS or mastery changes were made.

## Reproduction

From the repository root:

```powershell
backend/.venv/Scripts/python.exe docs/datasets/original-zhvi/build_batch_001.py
```

This rewrites only this batch's JSONL, manifest, local key registry and validation report beside the script. Retain the frozen namespace and seeds in later revisions. Stop generation after Batch 001.
"""
    (ROOT / "level-0-batch-001.validation.md").write_bytes(report.encode("utf-8"))
    # Verify manifest and registry against the actual disk artifact.
    saved_manifest = json.loads((ROOT / "level-0-batch-001.manifest.json").read_text(encoding="utf-8"))
    saved_registry = json.loads((ROOT / "lexical-key-registry.json").read_text(encoding="utf-8"))
    assert saved_manifest["actual_count"] == len(records) == len(saved_registry["entries"])
    assert saved_manifest["artifact_sha256"] == sha256(artifact.read_bytes()).hexdigest()
    assert saved_manifest["lexical_keys"] == [entry["key"] for entry in saved_registry["entries"]]
    print(json.dumps({"actual_count": len(records), "artifact_sha256": digest, "review_status_counts": counts, "validation": "PASSED"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
