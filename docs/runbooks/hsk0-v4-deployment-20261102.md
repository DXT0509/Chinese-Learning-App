# HSK 0 v4 local development deployment — 2 November 2026

The exact approved HSK 0 v4 pack is **published and active** in local development.
The existing Android roadmap can now load its four executable nodes. No real learner
playthrough, graded review, progress mutation or EXP grant was performed during deployment.

This deployment follows the owner's separate Phase 6.3C authorization. The earlier
[educational sign-off](hsk0-v4-educational-signoff.md) and
[final review](roadmap-phase-6.3b-final-review.md) remain historical records.

## Target, approval and backup

| Check | Actual result |
| --- | --- |
| Environment | `development` |
| Server / database | `127.0.0.1:5432/chinese_learning` |
| Actual Alembic revision | `0015_roadmap_engine` |
| Read-only publication preflight | Passed; exact vocabulary identities/revisions, review bindings, media and release identity matched |
| Read-only Alembic drift check | Passed; no upgrade operations detected; no migrations executed |
| Educational approval | 17/17, reviewer `dxt`, reference `HSK0-EDU-REVIEW-20261102`; no pending/blocked/change requests |

Verified canonical educational-definition SHA-256:

```text
5431957cc5be3205393d1c5d47456f92afef5079d6cbe7741f4756eac2edcfcf
```

Source: `backend/content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/`.
The bundle, plan, manifest, candidate and all individual approval bindings were verified.
Educational content, quiz keys, vocabulary identities and grading policies were unchanged.

Before writing, a custom-format PostgreSQL backup was created at:

```text
backend/.vocabulary-backups/hsk0-v4-20261102-quiesced/before-hsk0-v4.dump
```

Size: **3,848,865 bytes**. SHA-256:
`38100ca7a840632b2016e943177aa7d5b681e662d335b7d967e0d77183e704d3`.
`pg_restore --list` exited 0. No restore was performed. The backup and private audit
artifacts are ignored by Git and remain local.

An initial attempt stopped before registering/importing content because saved-word rows
changed concurrently after its baseline. The API was stopped, including its orphaned
reload worker, and a fresh baseline/backup retained all **58** saved-word rows. Nothing
was reset, reverted or removed. The initial baseline had 54 rows; an intermediate reading
of 57 was superseded by the final quiesced baseline of 58.

## Import, publication and activation

The guarded wrapper uses existing asset import, roadmap draft import and publication
services. Publication atomically activated the release with operator attestation
`dxt / HSK0-EDU-REVIEW-20261102`.

| Identity | Value |
| --- | --- |
| Code | `hsk-0-preparation` |
| Roadmap UUID | `5a8aa397-65fb-5582-b6a1-93a90ad9ebe8` |
| Published/active version | **4** |
| Version UUID | `c1d32c1d-f63b-5ec3-a75b-2751b9e1aacd` |

Exactly four ordered nodes exist. The database positions are zero based.

| Position | Type / scope | Stable node UUID | Node version UUID | Lesson version UUID | Activities |
| ---: | --- | --- | --- | --- | ---: |
| 0 | NEW_WORD 我 | `a2d1b452-81f0-55d9-af27-55d1ca76d94c` | `092c84ff-c012-5e44-9d0d-9c77bcd2250c` | `15c4ee07-667f-55c2-9a4d-9bf9f88a673e` | 6 |
| 1 | NEW_WORD 你 | `9bc4cfdf-3aa8-5313-b9ce-4baf5e2e0c1d` | `7c33056a-afd7-579d-9ee1-6e524e3654ba` | `d4d38307-8a74-5b27-90a5-3628d85db79b` | 6 |
| 2 | NEW_WORD 好 | `d666409e-79bc-5f1a-b137-65f900dcfcfd` | `1780eeb1-78f6-5891-97f3-ec57000b31e3` | `7ba1fc26-ed0c-5ed6-9146-83ba617fa1b9` | 6 |
| 3 | REVIEW 我, 你, 好 | `f5b0ea02-c209-57c5-9f95-89c496eca589` | `db76623e-e156-5125-b1bc-0d7f75e5c9ab` | `0102a9a0-fbb2-5121-94ce-4e67a44b462c` | 4 |

The exact pinned vocabulary references remain revision 1 of
`4ae81805-45f9-5d4f-a576-2a03b4ba27c9` (我),
`e611f2a1-17bb-5215-8862-7f69f32ca0fb` (你), and
`48fd5063-1606-5d90-9943-74d05d8dfc48` (好).
The REVIEW scope is exactly these three, in that order. All four published lesson
definitions, 22 activities, and five publication JSON objects match the approved source.

## Assets and retry safety

All six original media objects are registered and their stored bytes pass SHA-256/length
verification. Existing provenance and licensing metadata were retained.

| Word | Media | Registered asset UUID | Bytes |
| --- | --- | --- | ---: |
| 我 | Ogg audio | `ff7d57dc-5b57-58e4-8072-1caabca2ffad` | 13,186 |
| 我 | Stroke-order GIF | `76680e01-e174-5fa9-a9ea-c7e2aae7c11c` | 10,572 |
| 你 | Ogg audio | `c5a5f1e0-e5fe-503a-a7e2-06e5b5360278` | 15,096 |
| 你 | Stroke-order GIF | `f09090d2-0629-5b9b-b9ef-388b406e6a28` | 10,794 |
| 好 | Ogg audio | `e495a62c-2b69-5772-85aa-9aea529ee6da` | 13,835 |
| 好 | Stroke-order GIF | `a334cb71-17d4-5ca5-9518-6eb41ee51d4e` | 13,224 |

Only expected rows were inserted: 11 assets (six media plus four lesson JSON bundles and
one roadmap JSON bundle), one engine template/version pair, four lessons/versions,
four stable nodes/memberships, six vocabulary memberships, and one roadmap/version pair.
No pre-existing row was updated or deleted. No other content was published or activated.

An actual deployment retry reused the existing published release and all assets.
Every table fingerprint was identical before/after retry: **zero duplicate assets,
releases, progress records or EXP grants**.

## Preservation and API verification

Primary-key and complete-row SHA-256 fingerprints cover all **48 public tables**.
Only the exact approved content insert identities were permitted. All protected tables
matched the fresh baseline, including these representative counts:

| Data | Before / after |
| --- | ---: |
| Accounts / password credentials | 3 / 3 each |
| Auth sessions | 15 / 15 |
| Curated vocabulary / revisions | 2,810 / 2,810 each |
| Saved vocabulary | 58 / 58 |
| FSRS memories | 52 / 52 |
| Review attempts | 135 / 135 |
| Daily plans | 16 / 16 |
| Active-time records | 103 / 103 |
| SRS target policies | 2,804 / 2,804 |
| Roadmap runs, progress, activity receipts, EXP grants | 0 / 0 each |

Full-row comparisons include due dates, schedules, memory values, review history,
password/session fields and policies. These comparisons passed again after retry,
read-only API verification, backend restart and isolated regressions.

The backend was restarted using `python -m app`, bound to `127.0.0.1:8000`, with logs
in the ignored audit directory. Live `/health` and `/api/v1/health` returned 200;
OpenAPI returned 200 with all roadmap routes; unauthenticated roadmap requests returned 401.

Authenticated GET probes used the unchanged bearer-token verifier with rollback-only
credentials in `chinese_roadmap_test_20261102101729`. The probe's content dependencies
read the actual deployed database with PostgreSQL `default_transaction_read_only=on`.
No development account/session was created or borrowed. This was an **in-process API
probe**, not a live HTTP login as an existing learner.

The catalog exposed active v4; its node API exposed all four ordered nodes. A fresh QA
identity received the first lesson and both media with 200 responses, with private quiz
answers removed. Later lessons/media correctly returned 403 until predecessors complete.
All six media are stored and verified locally; their successful authenticated delivery
after progression was also exercised by the isolated signed-v4 playthrough. No production
or development learner was advanced to bypass these locks.

## Regression results and operational tools

- Selected backend/content/roadmap/deployment regressions: **79 passed, 1 skipped**.
- The skipped concurrency test was then run against the existing dedicated isolated
  `chinese_roadmap_concurrent_20261102101729`: **1 passed**. All 80 selected tests passed.
  Six simultaneous completion requests awarded EXP exactly once.
- The signed-v4 isolated functional test traversed all four lessons and all six media;
  repeat completion granted no duplicate EXP and preserved FSRS memories/review history.
- Read-only `alembic check` passed on development before deployment and on the isolated
  regression database afterward. Alembic emitted its existing `dialect_options` warning;
  no schema drift was detected.
- `ruff check app scripts tests` passed. Formatting checks passed for both new operational
  scripts and the deployment guard tests.

From `backend/`, the read-only guarded preflight is:

```powershell
.venv/Scripts/python -m scripts.deploy_hsk0_v4 --audit-dir .vocabulary-backups/hsk0-v4-20261102-quiesced
```

The same command with `--apply` performs the explicitly authorized retry-safe deployment;
it refuses another database, revision, approval binding or educational checksum. The
read-only API probe is `python -m scripts.verify_hsk0_v4_deployment --audit-dir <audit-dir>`
using the backend venv. It requires the previously migrated fixed isolated QA database.
Private evidence includes `before.json`, `after.json`, `backup.json`, `deployment.json`,
`retry-verification.json`, `api-verification.json`, `live-health.json` and
`final-preservation.json` in the ignored directory above.

## Android device check

No new Android build/install or device playthrough was performed for this deployment.
The previous phase's device tests are separate evidence. To inspect this deployed pack:

1. Keep the local backend running. For the existing debug app's default
   `http://127.0.0.1:8000/` URL, connect the unlocked phone over USB and run
   `adb reverse tcp:8000 tcp:8000` using the Android SDK platform-tools executable.
2. Open the existing app and sign in normally. Open its learning roadmap: expect
   我 → 你 → 好 → REVIEW, with only the first node initially available for a fresh account.
3. Opening the roadmap or available lesson is read-only. **Starting, submitting,
   completing or skipping lessons changes that account's progress.** Use a dedicated
   QA account connected to an isolated backend/database for a write-based device test.
4. In that isolated environment, check audio playback, animated stroke order, freehand
   writing, two pronunciation participation repetitions and both word quizzes; then
   complete the three-word REVIEW. First completion rewards remain 10/10/10/15 EXP;
   repeat completion must add zero. No handwriting/speech quality scores are implied.

There are no deployment blockers. A fresh device playthrough against this deployment
remains a manual check; existing real learner accounts were deliberately left untouched.
