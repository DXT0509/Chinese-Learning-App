# Completed Codex vocabulary review — local acceptance preparation

**All 2,501 pronunciation-specific records across all 50 batches have been reviewed.**
The original 2,500 written learning items and stable lexical identities remain intact.
The continuation resumed at L4-B004 and completed all remaining 1,700 records through
L5-B025. It made no development database writes or paid AI API calls.

| Result | Count |
| --- | ---: |
| Individually reviewed | 2,501 / 2,501 |
| Completed batches | 50 / 50 |
| Linguistically passing, including retained editorial holds | 2,488 |
| Ready for local acceptance | 2,482 |
| Records with corrected linguistic content | 640 |
| Corrected candidates passing recheck | 634 |
| Corrected drafts with another retained issue | 6 |
| Unresolved pronunciation/sense/identity findings | 13 |
| Protected editorial holds retained | 6 |
| Excluded total | 19 |
| Unreviewed / next unfinished batch | 0 / none |
| Strict production AI results created | 0 |
| Development writes / paid API calls | 0 / 0 |

| App level | Reviewed / total | Local candidates | Excluded | Corrected content | Batches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 101 / 101 | 95 | 6 | 1 | 2 |
| 1 | 100 / 100 | 100 | 0 | 9 | 2 |
| 2 | 150 / 150 | 148 | 2 | 10 | 3 |
| 3 | 300 / 300 | 294 | 6 | 32 | 6 |
| 4 | 600 / 600 | 599 | 1 | 153 | 12 |
| 5 | 1,250 / 1,250 | 1,246 | 4 | 435 | 25 |

Level 0 has 100 written items and 101 pronunciation records because 谁 retains both
readings. App levels are retained; no claim of official HSK certification is made.

## Approval rules and evidence

The existing versioned **local-codex-session-v1** path requires an actual PASS or
CORRECTED_PASS, all nine linguistic areas checked, a specific note, an example, no
pending reason or editorial hold, and matching source/current byte hashes, record
checksums and versions. Corrections are validated through the repository JSONL
contracts and re-read by the same session. It has **no confidence threshold**.

On an explicitly confirmed development import, the existing command automatically
records local evidence and assigns **LOCAL_CODEX_REVIEWED**. There is no manual
word-by-word approval step. Before import these are candidates, not DB approvals.
The separate local mechanism honestly identifies operator-attested Codex session
notes; exact model/version/confidence remain null. No provider receipt, authenticated
reviewer identity or second independent model is fabricated. Production
**zhvi-semantic-v1 / AI_APPROVED remains unchanged**, including confidence >= 0.95.
No Anthropic credential or paid provider configuration is needed for the local path.

All original source files remain unchanged. `batch_notes_12.py`–`45.py` record the
continuation's explicit findings; the scripts are serializers, not AI reviewers.
The final targeted recheck caught three residual example transcription errors
(流域 in 成效/将近; 湖泊 in 瑶池) and 碳's Hán-Việt reading in 碳纤维. Their earlier
evidence is preserved under `superseded/`; new versions/checksums record the repairs.
The initially missed 引起 headword error likewise has preserved first-pass evidence.

Representative corrections include 干部 **gàngbù → gànbù**, 机关 **jīgī → jīguān**,
高质量 **gāo pǐnzhì → gāo zhìliàng**, missing/extra example syllables, duplicated
Chinese phrases, inaccurate Hán-Việt readings, Vietnamese mistranslations, and POS
labels inconsistent with existing senses. Scientific examples also needed genuine
semantic repairs: 染色体 was conflated with a DNA double helix, 质子治疗 incorrectly
claimed nanoscale explosions, and 智能驾驶 implied unconditional autonomy. Corrected
examples were re-read; no vocabulary was regenerated.

See the exact [640-record correction ledger](datasets/codex-review-4.0.3/corrections.json)
for all fields, reasons, source/final versions and checksums. Narrow specialist checks
used recorded dictionary/primary sources, including [Hán Nôm character readings](https://hvdic.thivien.net/whv/%E7%A2%B3),
[NCI proton radiation](https://www.cancer.gov/about-cancer/treatment/types/radiation-therapy/external-beam)
and [Academia Sinica's Taiwan 重力波 terminology](https://www.asiaa.sinica.edu.tw/IAAQ/pdf/2018Q1.pdf).

## Excluded findings

The [pending ledger](datasets/codex-review-4.0.3/pending.json) records exact reasons.
Missing confidence never creates a local hold.

| Type | Stable identities retained |
| --- | --- |
| Five original source holds | 不客气\|bu4 ke4 qi5; 没关系\|mei2 guan1 xi5; 谁\|shei2; 谁\|shui2; 什么\|shen2 me5 |
| Existing DB hold | 厕所\|ce4 suo3 |
| Four earlier pronunciation/sense ambiguities | 过去\|guo4 qu5; 生发\|sheng1 fa1; 活泼\|huo2 po5; 场\|chang3 |
| Four earlier citation/spoken identity decisions | 一直\|yi4 zhi2; 一般\|yi4 ban1; 一共\|yi2 gong4; 不但\|bu2 dan4 |
| Five newly found incorrect keys | 引起\|ying3 qi3; 贯彻\|guan1 che4; 克勤克俭\|ke4 qin2 ke4 jian4; 质子治疗\|zhi3 zi3 zhi4 liao2; 生物信息学\|sheng1 wu4 xin1 xi1 xue2 |

The five incorrect keys require **yin3 qi3**, **guan4 che4**, **ke4 qin2 ke4 jian3**,
**zhi4 zi3 zhi4 liao2**, and **sheng1 wu4 xin4 xi1 xue2**, respectively. They are not
silently renamed because pronunciation is part of the stable identity. Any identity
repair must explicitly preserve references/history. The eight older decisions remain
as recorded; valid contextual sandhi elsewhere is not automatically considered an error.
Their pending reasons specify citation-policy reconciliation or mixed lexical senses,
rather than lack of a confidence score. No old hold was cleared merely to reach 100%.

## Final validation and artifacts

The repository validator passes all 50 deployment batches and all 2,501 combined
records. Global checks retain exactly 2,500 written items and 2,501 unique lexical/
pronunciation keys, with no duplicates or missing examples. Strict contracts check
Simplified-only content and pinyin formatting. All source/current file hashes,
record checksums/versions, complete note coverage and candidate eligibility reconcile.

- [Final audit](datasets/codex-review-4.0.3/final-audit.json) and [validation](datasets/codex-review-4.0.3/validation.json).
- [Progress checkpoint](datasets/codex-review-4.0.3/progress.json).
- [Complete catalog](datasets/codex-review-4.0.3/provisional-deployment.jsonl), 2,501 records including holds;
  historical filename retained. SHA-256 `1e490609d214cd9b3fc3d038e60f31570cb3568f4795dcc20c5a3f0ab28fa8fc`.
- [Accepted subset](datasets/codex-review-4.0.3/accepted-deployment.jsonl), 2,482 candidates.
  SHA-256 `3c17f51cba7f558bb8c8648a5475bf59c4935a8c5822b2e8ed768bea9b91773e`.
- Per-batch `L*-B*/deployment.jsonl` and `review-notes.json` are the import evidence.
- [Fresh read-only DB plan](datasets/codex-review-4.0.3/local-plan.json),
  [validated eligibility](datasets/codex-review-4.0.3/local-acceptance-validation.json),
  [DB snapshot](datasets/codex-review-4.0.3/database-inspection-read-only.json).

## Development deployment still awaits explicit operator action

Read-only inspection on **2026-10-26 Asia/Bangkok** confirms local
`127.0.0.1:5432/chinese_learning` remains at **0009_vocabulary_ai_review**.
**0010_local_codex_review has not been applied**. The catalog still has 51 records:
45 GENERATED_UNREVIEWED and six NEEDS_REVIEW; the local evidence table does not exist.

The exact conflict is **厕所|ce4 suo3**, UUID
`b58c0607-76a4-527c-a6ea-d77170d7dfd8`: DB v1 NEEDS_REVIEW, checksum
`8cacc9b365454fb299bc079f50eb04cf3499ed3ea08c037628ee28229ee60026`.
Its source is v1 GENERATED_UNREVIEWED; the separate reviewed draft is v2 NEEDS_REVIEW.
Exact current, original incoming and reviewed draft records/checksums are in
[hold-conflict.json](datasets/codex-review-4.0.3/hold-conflict.json).
It is excluded, preserving the editorial decision and all learner data.

The fresh plan proposes **2,437 inserts + 45 local acceptances**, with no conflicts.
After a confirmed migration, fresh preview and confirmed import, the expected catalog
has **2,488 rows: 2,482 LOCAL_CODEX_REVIEWED and six unchanged held rows**.
The other thirteen pending drafts stay out of this import. Existing user accounts,
saved words, mastery, schedules and lesson progress are untouched.

Follow [the operator runbook](runbooks/local-codex-vocabulary.md) in order:
validate and preview; back up; explicitly confirm additive migration 0010; generate
a new preview/token; explicitly confirm atomic import/local approval; enable the
development-only API flag; verify authenticated API and Android dictionary search.
The command selects genuine passing notes automatically across all 50 batches.
Do not use the old historical full-catalog import plan or raw JSONL as approval evidence.
No further paid AI review is needed for this local mechanism.

Earlier implementation tests (not rerun for this dataset-only continuation): backend
212 passed / 7 skipped; isolated nonempty migration preservation/Alembic checks and
atomic rollback/replay rehearsal passed; Android unit tests, debug assembly and lint
passed offline. This continuation executed full artifact validation/reconciliation
and read-only development inspection/preview. Physical Android search and actual
development publication remain operator checks after authorized deployment.
