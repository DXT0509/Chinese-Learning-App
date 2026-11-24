# HSK 0 v4 educational sign-off

Current status: separately authorized Phase 6.3C local development deployment is complete.
See the [deployment and preservation report](hsk0-v4-deployment-20261102.md).
The sign-off-only deployment boundary below is preserved as history for this earlier phase.

Reviewer: **dxt**. Review reference: **HSK0-EDU-REVIEW-20261102**.

The owner explicitly authorized recording the exact previously reviewed version-4 items
under those supplied values. After reading the current payloads, verifying all bindings,
and checking the existing editorial/asset evidence, the 17 local review attestations were
recorded through the existing schema. No reviewer name, ticket, timestamp, additional
inspection or expert verification was invented. Automated tests were supporting integrity
checks, not the authority for approval.

| Status | Count |
| --- | ---: |
| APPROVED | 17 |
| READY_FOR_APPROVAL | 0 |
| REQUEST_CHANGES | 0 |
| BLOCKED | 0 |

The six media inspections remain identified as **owner-reported listening/viewing**.
Their earlier filename-based inspection record is preserved; the new, explicit approval
authority is recorded separately in `owner-authorization.json`. It is not represented as
an independent expert acoustic, linguistic or stroke-order certification.

## Accepted content and exact hashes

The accepted educational definition is unchanged from `final-review-v4/bundle.json`:
我 → 你 → 好 → REVIEW, 22 activities, nine private quiz keys, three pinned vocabulary
identities/revisions and six original media assets. The 女/子 and third-tone corrections
remain exactly as reviewed. There were no new educational edits during sign-off.

Canonical educational-definition SHA-256:

```text
5431957cc5be3205393d1c5d47456f92afef5079d6cbe7741f4756eac2edcfcf
```

Canonical signed-plan SHA-256 (includes all review metadata):

```text
260175d421db791f3b5e3e2692fabe8996f66d382a32ac11312d4c71c6f814f9
```

Signed `bundle.json` file SHA-256:

```text
ab0271ebe11e217ba7107966313139b5204813b677e0a3f595c160311980110f
```

The first hash uses the project's canonical JSON checksum of the existing roadmap
definition, excluding external review sidecars. The second covers the exact signed
preparation plan. The third hashes the actual bundle file bytes, including its newline.
All three purposes are distinct. The original unsigned v4 artifacts are preserved.

## Approval and dependency records

Authoritative signed artifacts are under:
`backend/content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/`.

- `plan.json`: all 17 existing Review objects have status REVIEWED, reviewer `dxt`,
  evidence `HSK0-EDU-REVIEW-20261102`, and a validated exact content SHA-256.
- `review-status.json`, `review-status.md`, `review-bindings.json`: per-item decisions
  and current exact payload hashes.
- `owner-authorization.json`: owner-supplied authorization, its source-request file hash,
  overall content-bound educational acceptance, and explicit deployment prohibition.
- `owner-notes-signoffs.json`: actual supplied decisions applied after child reviews.
- `content/manifest.json`, `content/assets.json`, `content/objects/`: validated normal
  draft output, complete provenance and unchanged original CAS bytes.
- `content/publication-candidate.json`: filesystem-only candidate; no DB import/publication.
- `catalog-preflight.json`: fresh READ ONLY reconciliation bound to the signed plan hash.
- `signoff-verification.json`: consolidated final hashes, checks and warning dispositions.

The 14 asset/component/example approvals were recorded first in `signed-children-v4/`.
Only then were the three pending notes hashes recalculated against those actual child
review objects and approved. Only review metadata and its dependent hashes changed.
No v3 approval records or v3 review hashes were used to approve the v4 items. Existing
asset provenance remains cross-checked against its original frozen source records.

The generated `signoff-form.json` is a reusable input template, not the overall acceptance
receipt. Likewise, generic generator fields such as `overall_pack_approval: null` and
`publication_ready: false` do not ingest the separate owner authorization. The explicit
overall acceptance receipt is `owner-authorization.json`; deployment authorization is
still absent. No generic guard or validator was changed to force readiness.

## Evidence and validation

All three lexical identities, citation Pinyin, meanings, Hán Việt readings, examples,
five component explanations, three notes and nine quiz keys were rechecked against the
exact v4 evidence. There is one correct option per question and exact review scope.
All stored per-item checksums match the current approved payloads. Stable vocabulary,
node, activity and lesson-asset identities are preserved. All six original media files
retain their bytes, SHA-256, source URL, creator credit, selected license and visible
attribution in the notes. No new educational, provenance or licensing discrepancy was found.

The fresh catalog query was explicitly PostgreSQL READ ONLY. All selected current versions,
revision checksums and configured visibility matched. No catalog review status or record
was modified. Normal content validation reports **0 errors, 0 optional omissions**.
Two generic warnings remain in the reusable compiler report:

| Generic warning | Exact supporting disposition |
| --- | --- |
| EDUCATIONAL_REVIEW | Satisfied for this exact definition by `owner-authorization.json` and all 17 signed item records under the supplied reference |
| DATABASE_BINDING_UNCHECKED | Satisfied for this check by `catalog-preflight.json`, whose plan hash equals the signed plan hash; rerun before actual deployment |

No warning was waived, removed, or treated as automatic approval. Release authorization
remains a separate gate.

Relevant regressions: **70 passed, 1 skipped**, 20.52 seconds. They include the actual
signed artifact, stale-signature rejection, parent dependency handling, normal preparation,
all three publication-rehearsal variants (v3, pending v4 and signed v4), exact media access,
answer-key removal, progress, saves, EXP retries and FSRS preservation. The skip requires
the separately configured `ROADMAP_CONCURRENCY_TEST_DATABASE_URL`; it is not a pass.
Tests used the existing isolated `chinese_roadmap_test_20261102101729` database with rollback
fixtures. No migration was applied. An Alembic drift check on that isolated database exited
0. Ruff passed across app/scripts/tests. Android contracts/content presentation were not
changed or retested in this metadata-only step; previous exact-asset device evidence remains.

## Readiness and separately authorized next steps

**Educational sign-off is complete. The pack is ready for a separately authorized
development deployment. It is not imported, published or activated by this request.**
No development assets, users, progress, EXP, mastery, FSRS memory/schedules or real review
attempts were written. There is no authorization here to apply migrations or deploy content.

Before deployment, obtain explicit authorization covering object staging, asset registration,
roadmap draft import, publication **and activation**. Revalidate the exact signed plan,
its review bindings and source bytes, and rerun the read-only catalog check:

```powershell
# From backend/; these are local/read-only checks.
$releaseArgs = @(
  '--plan', 'content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/plan.json',
  '--catalog', '../docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl',
  '--asset-root', 'content/roadmaps/preparation/hsk-0-pack',
  '--output', 'content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content'
)
.venv/Scripts/python -m scripts.roadmap check-content @releaseArgs
.venv/Scripts/python -m scripts.hsk0_catalog_preflight --plan content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/plan.json --output catalog-before-publication.json
.venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs
```

Only after the separate deployment authorization, the exact write sequence is:

```powershell
.venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs --apply
$apiStorage = .venv/Scripts/python -c "from app.core.config import get_settings; print(get_settings().content_storage_dir)"
.venv/Scripts/python -m scripts.validate_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/asset-library --storage-dir $apiStorage
.venv/Scripts/python -m scripts.import_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/asset-library --storage-dir $apiStorage
.venv/Scripts/python -m scripts.roadmap import content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/roadmap.json
# Confirm import returned this exact precomputed version UUID before proceeding.
$versionId = 'c1d32c1d-f63b-5ec3-a75b-2751b9e1aacd'
.venv/Scripts/python -m scripts.roadmap preview $versionId
.venv/Scripts/python -m scripts.roadmap publish $versionId --reviewed-by 'dxt / HSK0-EDU-REVIEW-20261102'
```

**Publish atomically activates the roadmap.** It must not be run under import-only
authorization. No schema migration is needed. The post-publication Android/QA checklist
in [the v4 runbook](roadmap-phase-6.3b-final-review.md) remains the required follow-up after
any separately authorized deployment. A genuine content change invalidates the affected
approval and requires new content-specific review; signed hashes must never be silently refreshed.
