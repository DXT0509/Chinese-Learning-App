# Level 0 — Batch 001 validation report

Artifact: `level-0-batch-001.jsonl`. Schema version: 1. Application level: 0.

## Executed mechanical checks

- PASS: strict UTF-8 without BOM, NFC, LF, final newline, no blank records or control/format characters.
- PASS: exactly 50 parsed JSON objects; duplicate JSON object properties rejected.
- PASS: required and unexpected fields, batch-specific types, supported POS and classification values.
- PASS: 50 distinct UUIDv5 lexical keys and frozen identity seeds; deterministic recomputation.
- PASS: no duplicate simplified-form/numbered-reading candidates within this original batch, including alternate readings.
- PASS: primary forms/readings, unique local keys, Vietnamese meanings, sense/reading/example references.
- PASS: one example per entry (50 total); target Hanzi occurs in each example.
- PASS: Hanzi-only forms in the batch's supported BMP range; example punctuation allow-list.
- PASS: numbered-Pinyin tokens use tones 1–5 and belong to an explicitly authored batch syllable inventory.
- PASS: deterministic tone-mark rendering agrees with supplied marked Pinyin, ignoring case, word spacing and punctuation.
- PASS: review issue paths resolve; flagged entries use NEEDS_REVIEW; no HUMAN_APPROVED records.
- PASS: all official HSK membership and evidence values are null.
- PASS: re-read and revalidated the actual on-disk JSONL; computed SHA-256 from its exact bytes.

Review counts: `{"GENERATED_UNREVIEWED": 46, "NEEDS_REVIEW": 4}`.

SHA-256: `ddeb6f2a4b2188355363c8d7cc2b4a3bfdbcc1473aa435ff0502f3a5f4249006`

These checks are implemented in `build_batch_001.py` using only the Python standard library. They do not load application configuration, access the network, read third-party dictionaries or connect to PostgreSQL. The validator is scoped to this batch; it is not a complete general JSON Schema or Mandarin pronunciation validator.

## Blocking editorial findings

- 不客气 (cv_2a762c3b-0e16-5d57-a380-f5816d944d33): `NEUTRAL_TONE_VARIATION` at `/readings/0` — Draft uses a neutral final syllable. A human must confirm this teaching choice and whether to add a full-tone regional or careful-speech variant.
- 没关系 (cv_83757cef-10b8-5235-84a4-2d985be998b1): `NEUTRAL_TONE_VARIATION` at `/readings/0` — Draft uses a neutral final syllable. A human must confirm this teaching choice and whether to add a full-tone regional or careful-speech variant.
- 谁 (cv_ef3df994-fd44-5e20-812c-4c92df1f2c91): `READING_VARIANT_POLICY` at `/readings` — Both shéi and shuí are represented. Human review must confirm primary-reading selection and beginner presentation.
- 什么 (cv_79096eb0-272d-50a3-8abe-47697059f8b2): `TRADITIONAL_VARIANT_POLICY` at `/forms` — Human reviewer must confirm the chosen traditional-form preference and regional usage notes for 什麼 / 甚麼.

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
