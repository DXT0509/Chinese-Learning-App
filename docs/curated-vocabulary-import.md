# Curated vocabulary JSONL import

Phase 4.0.1 adds an opt-in AI_APPROVED policy and an independent offline review exchange.
See [AI publication workflow and exact commands](ai-vocabulary-publication.md). The human
approval instructions below remain available; references to human-only publication describe
the default policy. Import and mechanical validation still never grant approval.

This pipeline is independent of CC-CEDICT and character enrichment. Gemini output is
untrusted editorial staging content. Neither import nor validation marks it approved.
Use one UTF-8 JSON object per nonblank line; schema_version is currently 1. String values
are stripped and normalized to NFC; control characters and unknown fields are rejected.
Files are checksumed before parsing; conflicting/duplicate lexical keys reject the batch.
No network requests, generated translations, Traditional conversion or HSK inference occur.
Known Traditional forms are rejected using the pinned OpenCC t2s validation dependency.

```json
{"schema_version":1,"lexical_key":"学|xue2","simplified":"学","pinyin":"xué","pinyin_numbered":"xue2","sino_vietnamese":"học","part_of_speech":"verb","learning_level":0,"classification_standard":"APP_CURATED","difficulty_reference":"HSK_2_0","review_status":"GENERATED_UNREVIEWED","content_version":1,"vietnamese_meanings":["học"],"english_meanings":["to study"],"examples":[{"simplified":"我学中文。","pinyin":"wǒ xué zhōng wén.","vietnamese":"Tôi học tiếng Trung."}]}
```

The example explains format only; it is not an approved release vocabulary dataset.
Meaning lists are ordered, nonblank and duplicate-free. At least one Vietnamese meaning
is mandatory. Optional English, Sino-Vietnamese/POS and examples may be omitted. Each
example requires Simplified text, readable Pinyin and a Vietnamese translation. Examples
must be reviewed linguistically; this phase does not implement automatic sentence grading.

Numbered Pinyin uses lowercase syllables separated by single spaces, tones 1..5, `ü`
for the rounded vowel, and explicit neutral tone 5. The primary tone-marked rendering must
exactly match the provider-independent renderer. One syllable per Han character is required
for lexical words; punctuation/Latin forms, contracted erhua notation and alternate sandhi
spellings are not accepted. Use standard citation forms and separate pronunciation-specific
records. Multiple meanings for one pronunciation belong in the same record.

## Validation, staging and explicit review (from backend)

Apply 0008 explicitly first. Keep real generated batches outside the repository until
reviewed for content/licensing. The command never downloads or invokes Gemini.

```powershell
.venv\Scripts\python -m scripts.curated_vocabulary validate --file '<batch.jsonl>' --manifest '<new-review-manifest.json>'
.venv\Scripts\python -m scripts.curated_vocabulary import --file '<batch.jsonl>' --batch gemini-vi-2026-10-batch-001
```

Validation touches no database. Output includes raw-byte SHA-256, record count and the
unapproved publication mode. An optional manifest contains each curated UUID, lexical key,
content version and normalized-content checksum. Manifest files must be new; no overwrite.

The batch ID identifies immutable file bytes: same ID/checksum is a no-op; changed bytes
under that ID fail. Another batch containing identical normalized content also leaves
the lexical row untouched. Changed content requires a strictly larger content_version.
The transaction replaces current meanings/examples, retains version snapshots, and resets
quality to an unapproved state. Any conflict rolls back the entire batch. Missing words
are not implicitly deleted. Source batches remain in curated_vocabulary_batches.

After a HUMAN reviews Simplified forms, all readings, Vietnamese/English senses, examples,
Sino-Vietnamese reading and editorial difficulty, approve exactly one matching version:

```powershell
.venv\Scripts\python -m scripts.curated_vocabulary approve --id '<UUID-from-manifest>' --checksum '<record-checksum-from-manifest>' --reviewer '<human-reviewer-identity>'
```

Approval checks current content checksum and a usable Vietnamese meaning. Reviewer identity
and checksum are retained in revision evidence. The named reviewer is an operator assertion,
not an authentication provider or a web admin role. Protect maintenance access accordingly.
Importing `review_status: HUMAN_APPROVED` is always rejected, even if Gemini claims review.
The human CLI approves one record. The separate AI review CLI atomically submits batches
of checksum-bound semantic evidence. Corrections need a new version and renewed review.

Search/detail/save expose only approved Vietnamese content. Existing collection rows retain
their mastery when a later content version is staged; such content is marked inactive until
reapproved. Ordinary lookup/save never completes lessons or increments mastery. Due-review
evaluation, handwriting scoring, typed Pinyin grading and interval adjustment remain future
work against the same collection and reserved review-history table.

The new OpenCC dependency is constrained in pyproject.toml and pinned in
requirements-dev.lock. OpenCC identifies known script variants, not factual/linguistic
correctness, regional vocabulary, or verified HSK membership. Human review remains required.
