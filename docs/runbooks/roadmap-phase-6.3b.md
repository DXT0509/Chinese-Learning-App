# HSK 0 technical verification and future publication

Date: 2 November 2026. Proposal version 3 remains **unpublished and inactive in development**.
See [the pack design](../roadmap-phase-6.3b.md) and
[the educational approval checklist](roadmap-phase-6.3b-review.md).

## Executed safety checks

The three development catalog references were reconciled using an explicitly READ ONLY
PostgreSQL transaction. Revision `0015_roadmap_engine`, current version 1, all checksums
and configured visibility matched. No catalog corrections were needed or written.
This uses the existing LOCAL_CODEX_REVIEWED visibility policy, not a fabricated human review.

The six Commons original bytes were downloaded only after source license checks. Their
upstream SHA-1/length and local SHA-256 match `sources/sources.json`. All Ogg pages pass
CRC/sequence/completeness checks. Windows' native GIF decoder also decoded 30, 33 and 36
frames, and the resulting frame sheets were visually inspected for character and sequence.
No TTS, paid provider, generated pronunciation, invented stroke paths or new dependency
was used. Source files and the attribution notice are part of the private packet.

Commands run from `backend/`:

```powershell
.venv/Scripts/python -m scripts.fetch_hsk0_assets --output content/roadmaps/preparation/hsk-0-pack/sources
.venv/Scripts/python -m scripts.prepare_hsk0_pack
.venv/Scripts/python -m scripts.hsk0_catalog_preflight --output content/roadmaps/preparation/hsk-0-pack/catalog-preflight.json
.venv/Scripts/python -m ruff check app scripts tests
.venv/Scripts/python -m scripts.roadmap_isolated_checks
```

Ruff passes. The full final isolated run (`20261102032753`) passed **461 tests, 9 skipped,
4 warnings** in **100.41 seconds**, and isolated `alembic check` exited **0**. The runner
retains eight fresh databases, including its nonempty legacy, FSRS-v2 and roadmap migration
rehearsals. No development schema migration or publication was executed. The nine skips
still need dedicated historical migration/operator/reset URLs and are not claimed as passes.
Warnings are the pre-existing Starlette/httpx and SQLAlchemy reflection warnings.

The real-pack rehearsal uses a rollback-only PostgreSQL fixture. It imports the six assets
through the existing library, imports the generated exact lesson versions, publishes,
deactivates/reactivates, and traverses all four nodes through authenticated HTTP. It checks
answer-key removal, guarded exact media bytes/types, every required repetition, optional
review-introduction omission, first-completion EXP total **45**, retry EXP **0**, and unchanged
FSRS memory/attempt counts. Existing full-suite tests also cover nonempty learner-state and
review-history preservation. Synthetic fixture approval and the publication annotation
`ISOLATED TECHNICAL TEST; not human educational approval` exist only inside the rolled-back
test. They are not release attestations for the source packet.

An earlier full run caught the rehearsal's media route reading default storage instead of
its temporary object directory (460 passed, one failed). The final successful run above
includes the corrected isolated storage configuration. Library fixture copying was also
limited to the legacy folders actually read by its loader: unrelated roadmap CAS trees
had exceeded Windows path limits. This does not skip legacy lesson validation.

The later `stage-assets` command has an additional focused test for dry-run no-writes,
explicit CAS copying and refusal to overwrite corrupt existing objects. Its exact focused
result is recorded with the final results below; the 461 full-suite count predates that
additional staging test.

## Android checks

Build/test commands, from `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin -PISOLATED_HSK0_TEST=true --console=plain
.\gradlew.bat connectedDebugAndroidTest -PISOLATED_HSK0_TEST=true '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.Hsk0PackUiTest,com.example.chineselearningapp.RoadmapUiTest' --console=plain
```

The opt-in suffix creates **com.example.chineselearningapp.hsk0validation** and a separate
test package. Instrumentation cleanup targets those packages, preserving the main app.
The APK metadata was checked for that exact application ID. Tests use local immutable
fixtures/synthetic repositories; they do not connect to a learner API or capture microphone
audio. The user unlocked the connected Samsung SM-A225F (Android 12) for UI validation.

Two new JVM tests map the real four-node learner payloads, verify the 22-activity structure,
exact review identities, Sino-Vietnamese/Pinyin, asset bindings, speaking repetitions,
optional review introduction, answer-key removal and CHOICE wire shape. Existing ViewModel
tests retain server authority over receipts, EXP, skip/replay and completion.

Five new device tests exercise real word presentation, valid stroke acknowledgement,
tone-choice submission, pronunciation entry behavior, and all six native-media sources.
Nine existing roadmap Compose tests cover the remaining renderers, including original
canvas strokes, missing media, components and explicit quiz/intro participation.
Native tests establish platform decoding, preparation and muted playback completion,
not linguistic correctness or speaker quality. The exact final results are recorded below.

Initial locked-screen UI execution was invalid and is not counted as a passing run. A
test-only cache path was corrected to use the target context. After unlocking, 13 of 14
tests passed; the remaining quiz test had mounted multiple controls without the production
Column container, causing overlap. Its fixture layout was corrected before the final run.
No application redesign or handwriting/pronunciation grading was introduced.

## Remaining release gates

- All **17** source review objects remain UNREVIEWED: six assets, five components, three
  examples and three notes. Approve the exact checksum-bound items in the educational checklist.
- Listen to actual recordings, watch full stroke loops and approve beginner legibility,
  grammar, translation, tone instruction, roles and per-word license credits.
- Review the overall 22-activity pedagogy and all nine final choices. Do not turn a test
  attestation or a successful decoder check into a human educational approval.
- Rerun live read-only catalog reconciliation and asset-integrity checks immediately
  before a release. Earlier matching checksums are a snapshot.
- Obtain separate explicit development authorization covering object staging, asset
  registration, draft import and publication/activation. No such write commands below
  have been run against development.

## Exact future development procedure — not executed

1. Complete the checklist. Copy `plan-v3.json` to an operator-controlled `approved-plan-v4.json`,
   set roadmap version 4, enter real REVIEWED decisions with named reviewer/evidence and exact
   payload hashes, and apply any requested content corrections. Preserve source credits and
   both selected license links in the visible notes. Child reviews must be finalized before
   calculating the notes review hash. Never rewrite existing catalog revisions to fix a lesson.
2. Generate/validate an ordinary reviewed release directory, **without** the operator-preview
   option. For the exact path selected below, from `backend/`:

   ```powershell
   $releaseArgs = @(
     '--plan', 'content/roadmaps/preparation/hsk-0-pack/approved-plan-v4.json',
     '--catalog', '../docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl',
     '--asset-root', 'content/roadmaps/preparation/hsk-0-pack',
     '--output', 'content/roadmaps/preparation/hsk-0-pack/release-v4'
   )
   .venv/Scripts/python -m scripts.roadmap generate-drafts @releaseArgs
   .venv/Scripts/python -m scripts.roadmap check-content @releaseArgs
   .venv/Scripts/python -m scripts.roadmap preview-file @releaseArgs
   .venv/Scripts/python -m scripts.roadmap prepare-bundle @releaseArgs
   .venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs
   .venv/Scripts/python -m scripts.hsk0_catalog_preflight --output content/roadmaps/preparation/hsk-0-pack/catalog-before-release.json
   ```

   Stop on errors, stale hashes or revision mismatches. Confirm exactly three NEW_WORD nodes
   and their exact REVIEW, 22 activities, six referenced assets and no omitted intended
   enrichment. `stage-assets` is a dry run by default. Candidate `publication_ready=false`
   continues to represent the separate operator release gate, not approval to run writes.
   If the live catalog changed, revise references using the existing versioned procedures;
   do not bypass reconciliation or assume this fixed source still applies.
3. Obtain explicit authorization for the following development operations. Confirm the
   configured database and content-storage target without exposing credentials. The existing
   deployment is already at 0015, so **no migration is required**. Stage immutable objects
   into the API's configured storage and register assets using that same storage:

   ```powershell
   .venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs --apply
   $apiStorage = .venv/Scripts/python -c "from app.core.config import get_settings; print(get_settings().content_storage_dir)"
   .venv/Scripts/python -m scripts.validate_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/release-v4/asset-library --storage-dir $apiStorage
   .venv/Scripts/python -m scripts.import_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/release-v4/asset-library --storage-dir $apiStorage
   .venv/Scripts/python -m scripts.roadmap import content/roadmaps/preparation/hsk-0-pack/release-v4/roadmap.json
   ```

   Record the version UUID printed by import. No learner, catalog or FSRS table should be
   changed by these commands. Preserve the complete package, source/approval evidence and
   registration manifests. Directly importing `review-preview-v3/roadmap.json` is refused.
4. Run `.venv/Scripts/python -m scripts.roadmap preview <returned-version-UUID>` and review
   all exact lesson/catalog/media bindings. Only after publication **and activation** are
   explicitly authorized, run:

   ```powershell
   .venv/Scripts/python -m scripts.roadmap publish <returned-version-UUID> --reviewed-by '<real reviewer identity and approved review ticket>'
   ```

   **The existing publish operation atomically publishes and activates.** It is not a
   publish-only staging step. Do not run it with only draft-import authorization.
5. Verify authenticated roadmap discovery and all four pinned nodes. Confirm unrelated
   accounts' EXP, mastery, schedules and review history are unchanged. If withdrawing a
   faulty release, use `roadmap depublish 5a8aa397-65fb-5582-b6a1-93a90ad9ebe8` only after
   authorization; this preserves published versions and existing runs. Do not delete
   versions, downgrade the schema, reset data or remove storage volumes.

## Final results

The corrected complete device run passed **14/14 tests**, zero failures/skips, on the
Samsung SM-A225F running Android 12 (1 minute). A subsequent focused native-media run
passed **1/1** after strengthening the check to start every real recording, decode/play
it to completion with volume muted, and validate all three changing GIF animations.
It completed in 47 seconds including build/install/cleanup. Those are 14 distinct device
tests, not 15. Audible speaker quality and linguistic pronunciation review remain pending.

Android JVM result: **161 tests passed, 0 failed**. Debug assembly, lint and instrumentation
compilation passed; lint reports **0 errors, 106 warnings**, including existing suggestions
and platform Movie deprecation/compatibility warnings. The normal debug variant is rebuilt
at the end so its default application ID is restored; no primary-app installation is done.

Focused latest backend/CLI verification passed **70 tests** in 9.15 seconds, including the
new staging test, preparation gates and existing content commands. This overlaps the
461-test full suite and must not be added to that count. Ruff passes across app/scripts/tests;
all 11 changed Python files pass formatting checks.
