# Codex vocabulary review and local approval — current checkpoint

Policy **local-codex-session-v1** is implemented. It accepts real passing Codex
session notes without a numerical confidence requirement. It uses the distinct
**LOCAL_CODEX_REVIEWED** status because this session cannot verify an exact reviewer
snapshot/version. Unknown identity fields remain null. The production
`zhvi-semantic-v1` / AI_APPROVED contract remains unchanged, including confidence
>= 0.95. No paid Anthropic call is required or made.

Follow [the operator runbook](runbooks/local-codex-vocabulary.md) for exact rules,
PowerShell validation/preview, backup, explicit migration/import confirmations,
automatic local approval, failure recovery and Android search verification.

| Coverage | Actual result |
| --- | --- |
| Source | 2,500 written items; 2,501 pronunciation identities; 50 batches |
| Individually reviewed | 801 records, 16 batches |
| Completed | All Levels 0–3, plus L4-B001–L4-B003 |
| Resumed this implementation | 150 records; 38 corrected and rechecked |
| Linguistically passing | 793, including six retained editorial holds |
| Local acceptance candidates | 787 |
| Total corrected records | 90; some earlier corrected records retain a separate issue |
| Unresolved linguistic findings | 8 |
| Pre-existing editorial holds retained | 6 |
| Unreviewed | 1,700 records, 34 batches |
| Rejected | 0 |
| Strict production AI results created | 0 |
| Development DB writes / paid API calls | 0 / 0 |
| Next actual review batch | **L4-B004** |
| Full review complete | **No** |

Each completed batch has actual explicit per-record notes covering all nine linguistic
areas, source and reviewed content checksums/versions, corrections/reasons and pending
reasons. Complete examples were read; corrected content was re-read by the same Codex
session. No script inferred a linguistic pass from structural validation, and no second
independent model review is claimed. Checkpoint timestamps identify local file writes,
not provider invocations. Deterministic local receipt IDs are not external response IDs.

The three resumed batches are preserved in `batch_notes_09.py`–`11.py` and
`L4-B001/`–`L4-B003/`. Those scripts record already-authored findings and refuse to
replace an existing checkpoint. `checkpoint.py` can safely rebuild aggregate reports
and verify reviewed copies. Use the repository JSONL validator, not a fabricated
strict ReviewResult, to validate these canonical copies.

Examples of new corrected findings:

- 材料: 收集 **shòují → shōují** in the example.
- 干警: Sino-Vietnamese **can cảnh → cán cảnh**.
- 超过: **vượt bậc → vượt qua** for transitive surpassing.
- 传真: remove **máy fax**, which is 传真机; retain bản fax.
- 打招呼: remove misleading welcoming gloss; retain greeting senses.
- 根: replace an example using 根 for a drawn line with **一根细树枝**.
- 光: align Vietnamese light/only/all-gone senses with existing English, and use
  natural **大家把桌上的饭菜都吃光了。**
- 打折/高度/地址/低头/风景/打扰: correct unnatural or redundant example phrasing and
  recheck complete pinyin/Vietnamese. 高度 also corrects yì wàn to spoken yí wàn.
- 甜点: clarify **món tráng miệng**, not ambiguous điểm tâm; 住宿费用 means lodging
  costs without implicitly adding meals.
- Add missing noun/adjective/adverb categories where existing senses or examples
  require them, without generating new vocabulary or changing lexical identities.

The exact 90 changed records, versions, checksums, fields and reasons are in
[corrections.json](datasets/codex-review-4.0.3/corrections.json). Earlier findings
include Sino-Vietnamese errors in 些/咖啡/游泳/泳衣/碰/肥皂/袜子/棵/尤其/几乎,
Vietnamese typos, the missing 谁|shui2 example, and missing example syllables.

The [pending ledger](datasets/codex-review-4.0.3/pending.json) separates actual
uncertainties from retained decisions:

| Type | Identities |
| --- | --- |
| Existing source holds | 不客气\|bu4 ke4 qi5, 没关系\|mei2 guan1 xi5, 谁\|shei2, 谁\|shui2, 什么\|shen2 me5 |
| Existing DB hold | 厕所\|ce4 suo3 |
| Pronunciation/sense ambiguity | 过去\|guo4 qu5, 生发\|sheng1 fa1, 活泼\|huo2 po5, 场\|chang3 |
| Citation/spoken-sandhi identity decision | 一直\|yi4 zhi2, 一般\|yi4 ban1, 一共\|yi2 gong4, 不但\|bu2 dan4 |

No missing numerical score creates a new NEEDS_REVIEW decision under the local policy.
Existing source/database holds are preserved under the earlier explicit instruction
not to bypass them; linguistic correctness alone cannot silently remove that history.
A future explicit editorial resolution must document the reason and any new version.

Read-only development inspection found 0009 applied, with the existing 51 records
unchanged: 45 generated and six held. The fresh local plan lists **742 inserts and
45 local status acceptances**. It excludes the 14 pending copies and 1,700 unreviewed
records. After an operator explicitly applies additive migration 0010, a new plan and
confirmation are required before importing/accepting the 787 candidates. No source
JSONL or historical migration was edited. The original full-catalog
`import-plan-read-only.json` is historical/provisional; use `local-plan.json` for this
implemented path.

The original conflict remains protected: 厕所|ce4 suo3, UUID
b58c0607-76a4-527c-a6ea-d77170d7dfd8, DB version 1 NEEDS_REVIEW versus source version 1
GENERATED_UNREVIEWED. Its local draft version 2 retains NEEDS_REVIEW. This local importer
excludes it, so it does not change the DB version/status or reset learner state.

Implementation adds separate append-only local receipts, a development-only setting,
consistent search/detail/save visibility, an extended collection guard in **new**
migration 0010, and a Chinese dictionary detail label identifying local Codex review.
Turning the setting off hides this local content without deleting saved entries,
mastery or scheduling. Configuration rejects local enablement outside development.

Executed verification: **212 backend tests passed, 7 skipped** against an isolated
PostgreSQL database; a nonempty migration preservation rehearsal through 0010 and
`alembic check` passed. Historical database rows/mastery/schedules were preserved.
An additional isolated operator rehearsal passed: missing/stale confirmation was
refused, a simulated interruption after receipt creation rolled back the entire
import, and a freshly confirmed replay retained exactly one receipt per record.
The source audit and all 2,501 provisional records pass the repository JSONL validator.
Android testDebugUnitTest, assembleDebug and lintDebug passed using the cached
Gradle 9.2.1 distribution offline. Physical device validation and development
publication have not been performed.
