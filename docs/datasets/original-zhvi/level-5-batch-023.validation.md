# Level 5 — Batch 023 Validation Report

Artifact: `level-5-batch-023.jsonl`
Schema version: 1
Learning level: 5
Batch number: 23

## Summary
- Target unique lexical items in this batch: 50
- Validated records count: 50
- Cumulative unique lexical items across catalog: 2400
- Raw-byte SHA-256: `22c8103080e5a935809550c78be195ba8ab5215e6c1bbd245b87badc71dd75b9`
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
