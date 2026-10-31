# Phase 4.1D deployment readiness — 2026-10-29, Asia/Bangkok

Historical pre-installation snapshot. Explicit authorization and deployment have
since completed; see the [final deployment report](srs-phase41d-deployment-20261029.md).
The original confirmation-gate evidence below is retained for auditability.

**Ready, awaiting explicit operator confirmation. No development installation or
database write has occurred. The backend is stopped for the maintenance interval.**

Prepared under [the exact complete-installation procedure](srs-phase41d-complete-installation.md).
The [fresh machine-readable preview](../srs-phase41d-installation-preview-20261029.json)
contains verified target, hashes, effects, preservation checks and isolated receipts.

## Exact approval scope

- Database: `chinese_learning`, `127.0.0.1:5432`, role `postgres`.
- Alembic: `0012_srs_review_engine`; no migration required or applied.
- Bundle: `docs/datasets/srs-phase41d-complete-v2.json`.
- Bundle SHA-256: `abae251396a78ffc12cfa535374751954f4cde060a330bbb8491e89e428e81e2`.
- Effects: **656 inserts, zero updates, zero deletions, zero conflicts**;
  all **2,148 installed policies preserved**.
- Published denominator: **2,804**, from **2,810** catalog records; all six
  unpublished records remain protected and excluded.

Offline reproduction generated a byte-identical candidate in a new private output
path. Fresh validation against development returned 2,804 validated, 2,148 unchanged,
656 proposed inserts, zero updates and zero actual inserts. The detailed live audit
reported 2,804 proposed covered and zero unresolved. Its lexical array ordering
differs from the approved UUID-ordered candidate; installation will use only the
exact candidate and hash above.

## Fresh backup and preservation

Backup: `backend/.vocabulary-backups/phase41d-deploy-4ed7b8af8b1f/before-installation.dump`.
Size: **3,115,721 bytes**.
SHA-256: `521f05da564830f6466a44c69119024c5bac49cbc5d0eff0255e22c21f91cf1b`.

The custom-format archive was listed and fully restored into a fresh isolated
database. All **36 source table fingerprints**, including policy rows and Alembic
metadata, matched the restored copy. Fingerprints include complete `to_jsonb(row)`
values, including attempt submission journals, with UTC fixed on every connection.
The development database's default `Asia/Bangkok` setting was not changed. An initial
reconnection comparison omitted UTC normalization; its formatting mismatch was
diagnosed, and the complete rehearsal was repeated on a fresh restore with UTC
enforced throughout.

The actual baseline includes **2,810 vocabulary rows, three users, 27 saved-word
rows and one existing SRS attempt**. All contents, mastery values, SRS schedules,
review history, authentication data, publication evidence and lesson state are
covered by the complete table fingerprints. No real graded attempt was submitted.
All 36 development fingerprints still matched after the rehearsal; the existing
2,148 policy payloads remained unchanged. Full private snapshots and process
receipts are in the ignored evidence directory beside the backup.

## Isolated installation rehearsal

Final rehearsal target: `chinese_p41d_deploy_4ed7b8af8b1f_verified`.

| Check | Result |
| --- | --- |
| Fresh restore / `alembic check` | Passed |
| First exact-bundle import | 656 inserted, 2,148 unchanged |
| Reimport | Zero inserted, 2,804 unchanged |
| Runtime published coverage | 2,804 / 2,804, every level 100% |
| Duplicate / stale policies | Zero / zero |
| Six unpublished identities | All excluded and ungradable |
| Original installed policy rows | All 2,148 unchanged, including row metadata |
| Non-policy table fingerprints | All 35 unchanged |

This is isolated rehearsal evidence, not a claim that development has 2,804
installed policies. Development still has 2,148.

## Backend and Android readiness

The verified repository Uvicorn reload launcher and its child worker were stopped;
the worker inherited the listening socket, so its shutdown was verified separately
with a failed health GET. There were no other application database connections at
the initial preservation check. The API remains stopped pending authorization.

Updated backend source supports contextual grammar and is import-validated by this
rehearsal. Source hashes are recorded for rechecking the approval boundary. After
authorization, restart with `.venv/Scripts/python -m app` from `backend/`, hidden,
using the existing safe logging and psycopg-compatible event-loop configuration.

The updated debug APK is present:
`android/app/build/outputs/apk/debug/app-debug.apk`, SHA-256
`e2c0fb33b3803fa6c78702d2a5831a544d59baa4cbd9620f4def48e6f06cfbe3`.
It contains the new Vietnamese classification labels. The preceding implementation
verification recorded **109 passing Android unit tests**, successful debug assembly
and lint. No fresh Android build was needed for these unchanged sources. Physical
device installation and validation have not been verified; use the updated APK
before reviewing the new classification questions.

## Gate and authorized follow-up

**STOP: explicit confirmation has not been received.** The requested confirmation
must name the exact target, bundle/hash, 656 inserts, no updates/deletions/conflicts,
preservation of all existing data, and this verified fresh backup.

After confirmation, recheck target, revision, source/bundle hashes and all source
fingerprints before running the exact runbook installation command once. If data
changed, refresh the backup and preview first. Then verify all installed policy
objects, 2,804 runtime-covered identities, no duplicates/stale bindings, six holds,
original policy rows and all non-policy fingerprints. Revalidate without installing.
Restart the backend and perform GET-only health/OpenAPI/authentication checks;
authenticated service reads must not create sessions, attempts or progress.
Run regression tests against explicitly isolated synthetic fixtures and publish a
separate final deployment receipt. No final deployment success is claimed here.
