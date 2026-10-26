# Level 0 — Batch 002 Validation Report

Artifact: `level-0-batch-002.jsonl`
Schema version: 1
Learning level: 0
Batch number: 2

## Summary
- Target unique lexical items in this batch: 50
- Validated records count: 50
- Cumulative unique lexical items for Level 0: 100 / 100 (Level 0 COMPLETE)
- Raw-byte SHA-256: `538c6f0e281dc31ecae8024b243151783f26b0336a1edb776680d5826fdcca4d`
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
- [x] Zero duplicate keys or duplicate words against Level 0 Batch 001.
- [x] Staged with `review_status: GENERATED_UNREVIEWED`; zero unearned approval claims.

## Cumulative Level 0 Status
- Batch 001: 50 unique lexical items (51 pronunciation rows: `谁|shei2` and `谁|shui2`)
- Batch 002: 50 unique lexical items (50 pronunciation rows)
- **Total Level 0 Unique Lexical Items**: 100 / 100 (Target met: 100%)
- **Total Level 0 Import Records**: 101 records
