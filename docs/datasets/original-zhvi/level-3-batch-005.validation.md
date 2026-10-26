# Level 3 — Batch 005 Validation Report

Artifact: `level-3-batch-005.jsonl`
Schema version: 1
Learning level: 3
Batch number: 5

## Summary
- Target unique lexical items in this batch: 50
- Validated records count: 50
- Cumulative unique lexical items across catalog: 600
- Raw-byte SHA-256: `813030241df3f61002dfec04e9211c5afca1b8d46b33cd7f0413cb3ee0f1890d`
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
