# Phase 4.1D — final policy preparation, 2026-10-28

Deployment update, 2026-10-29: **2,804 / 2,804 valid policies are now installed in
development** following explicit authorization. See the
[final deployment report](runbooks/srs-phase41d-deployment-20261029.md). The following
preparation snapshot is retained unchanged for provenance.

**All 242 remaining identities have individually reviewed policies. Proposed
coverage is 2,804 / 2,804 published identities (100%). Development remains at
2,148 installed policies; no development installation or learner write occurred.**

The final candidate is [srs-phase41d-complete-v2.json](datasets/srs-phase41d-complete-v2.json).
Its SHA-256 is `abae251396a78ffc12cfa535374751954f4cde060a330bbb8491e89e428e81e2`.
It preserves every one of the previous 2,562 policy payloads, including the 2,148
installed policies and 414 earlier prepared additions. It adds exactly 242.
There are **zero pending policies** for the currently published denominator.

| Level | Published | Currently installed valid | Final proposed valid | Proposed coverage |
| --- | ---: | ---: | ---: | ---: |
| 0 | 218 | 112 | 218 | 100% |
| 1 | 289 | 110 | 289 | 100% |
| 2 | 158 | 142 | 158 | 100% |
| 3 | 294 | 276 | 294 | 100% |
| 4 | 599 | 536 | 599 | 100% |
| 5 | 1,246 | 972 | 1,246 | 100% |
| Total | 2,804 | 2,148 | 2,804 | 100% |

There are still 2,810 catalog records. The six protected unpublished identities
remain untouched: `不客气|bu4 ke4 qi5`, `什么|shen2 me5`, `厕所|ce4 suo3`,
`没关系|mei2 guan1 xi5`, `谁|shei2`, `谁|shui2`. None is included as published,
silently removed, merged with another pronunciation, or given an installable policy.

The [complete machine-readable coverage inventory](srs-phase41d-complete-coverage-v2.json)
contains all 2,810 identities, including the protected records, source metadata,
bindings, previous reasons, installed/prepared distinction and final review findings.

## Individual review and linguistic findings

The work continued from the unchanged [242-record checkpoint](datasets/srs-phase41d-editorial-checkpoint.json).
Every entry's Chinese form, Vietnamese senses and complete Chinese source example
was read. [Authored decisions](../backend/scripts/phase41d_remaining_notes.py)
record one specific grammatical analysis and a short assessment sentence for every
identity. These sentences are **new policy assessment contexts**, not replacements
for published dictionary examples. The [bound linguistic review](srs-phase41d-linguistic-review-v2.json)
records exact identities, versions/checksums, original labels, original source
examples, assessment contexts, decisions, findings and empty pending-reason lists.

The original 215 `idiom` labels mix traditional 成语 and contemporary fixed
collocations. Policies retain `idiom` for 205, and conservatively use `expression`
for ten contemporary political/social collocations such as `依法治国`, `互利共赢`
and `优势互补`. Their original source labels remain recorded verbatim. This is a
policy-level lexical annotation, not an overwrite or a claim that all dictionaries
agree on the boundary of 成语. Their grammatical questions do not depend on that
boundary. No dictionary correction, content replacement or fabricated publication
receipt was needed. Exact published vocabulary metadata changes: `[]`.

The remaining 27 records are expressions, one quantity expression and four bound
word elements. None actually has a null source POS: the earlier missing coverage
came from broad/mixed structural labels that the old POS contract could not grade.

| Assessment among the 242 | Count | Decision |
| --- | ---: | --- |
| Contextual syntactic role | 215 | Ask the role of a marked expression in a reviewed sentence, keeping lexical classification separate. |
| Known ordinary grammatical function | 18 | Grade 14 verbal expressions/modal phrases, two nominal phrases, one adverbial expression and one quantity phrase directly. |
| Bound-morpheme classification | 4 | `今`, `午`, `昨`, `朋` are assessed within the actual modern compounds used by the source. |
| Communicative expression kind | 5 | `你好`, `您好`: greeting; `再见`: farewell; `对不起`: apology; `晚安`: wish. |

For idioms, assigning an intrinsic noun/verb/adjective POS from the source's word
`idiom` would be unreliable. The reviewed question instead asks **grammatical
function in a particular sentence**: subject, predicate/core of predicate, object
(including a preposition object), attribute, adverbial, complement or independent
clause. These are actual grammar questions with distinct distractors, not a test
whose answer is always “idiom.” For example:

- `他们配合得【天衣无缝】。` — degree complement after 得.
- `【一诺千金】是他的原则。` — subject of the judgement.
- `学生们【如饥似渴】地阅读经典。` — adverbial modifying reading.
- `【勤能补拙】，所以我们要坚持练习。` — the first independent clause.

These are contextual analyses, not assertions that each idiom has one permanent
word class. Short reviewed sentences remove nesting and repeated-occurrence
ambiguities in several long source examples. The single marked span is explicit.
Traditional grammar terms and phrase/function distinctions were checked against
[Oxford CTCFL's grammar teaching material](https://www.ctcfl.ox.ac.uk/materials_lang-work_grammar-database_grammar-database/)
and [Cambridge's grammar terminology excerpt](https://assets.cambridge.org/97805217/85655/excerpt/9780521785655_excerpt.pdf).
The individual Chinese judgements are the recorded Codex session review; neither
reference is represented as certifying all 242 entries.

For ordinary items, reliable functions are graded directly: `打电话`, `买东西`
and `谢谢` have verbal function; `今天晚上` and `床上` have nominal phrase
function even when placed in an adverbial/prepositional construction; `还没`
has adverbial function. Negated modal-verb phrases keep their verbal function.
`一点儿` is explicitly a quantity phrase, never arbitrarily mapped to classifier.
The four word elements and five conventional formulas receive documented,
meaningful alternative classifications with competing choices and exact grading.

## Minimal compatible extension

[ContextualGrammar](../backend/app/services/contextual_grammar.py) is optional
review evidence in the existing policy JSON. It separates lexical category from
assessment type, binds the original POS label and actual source example, records
the authored assessment context and rationale, and defines the choice family.
It is permitted only for explicitly reviewed structural labels, not as a blanket
override for missing or conflicting ordinary POS metadata.

The installed policy table and pinned attempt targets already store JSONB, so no
migration or dependency change is needed. Legacy policy serialization omits the
new optional field entirely, preserving all previous JSON payloads. Old pinned
attempts continue using their existing question/options. No attempt is upgraded
in place. New contextual policies validate exact version/checksum, source POS,
source example and marked occurrence. Installation locks examples along with
catalog/publication evidence and refuses missing/stale evidence or immutable-row
conflicts. Runtime resolution also checks the source example remains present.

The sequence remains **Hanzi → tone-correct Pinyin → POS/function classification**.
All 242 policies retain all three stages. No `NOT_APPLICABLE`, POS skip, broad
alternate Hanzi/Pinyin acceptance, client correctness flag or schedule change was
introduced. A wrong or assisted applicable first answer still causes overall FAIL.

Before Hanzi, the learner sees Vietnamese meaning, character count, usable source
Hán-Việt and safe Vietnamese context/cues. No assessment Chinese, grammatical
answer key or Pinyin is exposed. The marked Chinese assessment sentence appears
**only at POS**, after Hanzi and Pinyin answers are sealed. Questions expose the
complete choice family, never a correct-answer flag or review rationale.

The HTTP shape stays the same: `prompt_vi`, `options`, `input_mode`, `simplified`.
Android adds Vietnamese labels for the new choice codes and broadens the stage
title to “Từ loại và cách dùng.” The existing single-/multi-select renderer,
handwriting panel, session ordering, token handling and ViewModel state remain.
Updated Android is required to label the new choices; old policies remain usable
with their existing codes. Coordinate the client/backend release before installing
the new policies. No APK/device installation or backend restart was performed.

## Validation and deployment boundary

The [verification receipt](srs-phase41d-complete-verification-v2.json) records the
actual database identity, full published denominator, per-level coverage, source
and candidate preservation, backup hash and isolated installation effects.

The exact read-only development preview is **2,804 validated; 2,148 unchanged;
656 proposed inserts; zero proposed updates; zero inserted**. After an approved
installation, those 656 comprise the earlier 414 plus the newly reviewed 242.

The fresh custom-format development archive was listed and fully restored to an
isolated database. The final candidate was imported there and reimported:
first import **656 inserted / 2,148 unchanged**; second import **zero inserted /
2,804 unchanged**. Every published identity was resolved through the runtime
resolver: **2,804 gradable**, with no pending policies. All 35 non-policy table
fingerprints and all original policy payloads were preserved. Development was
fingerprinted again read-only; learner, publication and policy data were unchanged.

Backend validation covers the complete real bundle, deterministic preparation,
prior policy preservation, source/version/checksum mismatches, unsupported answers,
mandatory stage retention, no Hanzi/key leakage, strict server grading, and a wrong
answer at each stage causing FAIL. Database tests use isolated synthetic learners.
Full backend and Android outcomes are in the verification receipt. Fresh isolated
migrations to head and `alembic check` passed; no new migration was required.
No emulator or physical-device validation is claimed.

Executed final checks: **365 backend tests passed, 13 optional checks skipped**;
**109 Android unit tests passed, zero failed/skipped**, debug assembly and Android
lint passed. Repository Ruff and changed-Python formatting checks passed. The
optional dedicated migration/race test database URLs were not configured; the
fresh isolated upgrades, schema checks and catalog restore/import rehearsal were
executed separately as described above.

The [safe deployment procedure](runbooks/srs-phase41d-complete-installation.md) requires an
updated backend/client, a renewed read-only preview and fresh verified backup if
source data changes, full preservation fingerprints and explicit authorization.
**Prepared coverage is complete; development deployment remains unperformed.**
