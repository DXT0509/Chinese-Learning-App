# Level 4 — Batch 011 Validation Report

Artifact: `level-4-batch-011.jsonl`
Schema version: 1
Learning level: 4
Batch number: 11

## Summary
- Target unique lexical items in this batch: 50
- Validated records count: 50
- Cumulative unique lexical items across catalog: 1200
- Raw-byte SHA-256: `29cb73163f3e2f3ead553b07fa8edaf6ed87bfd376b2b75a769dbc3efc84a24b`
- Validation status: PASSED (checked via backend `CuratedRecord` and `load_records`)

## Verification Checklist
- [x] Strict UTF-8, NFC normalized, LF line endings, no BOM, no blank records.
- [x] Exactly 50 JSON objects conforming to `CuratedRecord` schema.
- [x] Simplified-only characters (verified with OpenCC `t2s`).
- [x] Accurate Mandarin numbered Pinyin with tones 1–5; 1-to-1 syllable-to-character correspondence.
- [x] Pinyin tone-marking strictly matches canonical renderer (`tone_marks`).
- [x] Natural Vietnamese word definitions for beginner flashcards.
- [x] Accurate optional Sino-Vietnamese readings where conventional; null for colloquial/opaque terms.
- [x] Each record contains an illustrative beginner example with Simplified Hanzi, tone-marked Pinyin, and Vietnamese translation.
- [x] Zero duplicate keys or duplicate words against all prior catalog batches.
- [x] Staged with `review_status: GENERATED_UNREVIEWED`; zero unearned approval claims.
