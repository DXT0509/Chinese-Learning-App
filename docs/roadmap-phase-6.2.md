# Phase 6.2: Android vocabulary roadmap and lesson player

Implemented on 1 November 2026. Development content remains unpublished and inactive.
The Android feature is ready for content validation; **the development roadmap is not
playable until a real reviewed release is published and activated**. No development
catalog, learner progress, EXP, FSRS attempts or schema was written by this work.

## User experience and navigation

Learning → Roadmap uses the existing authenticated navigation shell and its single
bottom bar. Dictionary, personal vocabulary, daily Review, Profile, authentication
and preview lessons retain their routes. The identity-keyed protected graph owns the
roadmap ViewModel; logout/account changes destroy its private state.

The mint path uses lazy rows, alternating offsets and curved connectors. Round word
nodes and rounded-square group-review nodes show server statuses, including locked,
available, in-progress, completed and skipped states. The current node is emphasized.
Locked taps show a short Vietnamese snackbar. Empty discovery shows “Chưa có bài học”
without creating content. Map and section selectors use server-provided positions;
the current-node action loads a nearby window rather than walking all prior pages.

The INTRODUCTION activity now reveals the pinned word on one screen: Hanzi first,
then Pinyin with a user-triggered Mandarin TTS button, Vietnamese meanings, and an
optional Hán-Việt reading. Each Continue tap reveals one field with a fade and 16dp
upward slide. A further tap switches the CTA to “Đã nhớ ✓”; that explicit tap alone
submits ACKNOWLEDGE and lets the existing activity sequence advance (normally to
COMPONENTS). Missing or blank Hán-Việt skips the empty step. Reveal state survives
recreation and is keyed by run, activity and word version. The word area scrolls;
the reusable MascotChatBar and CTA stay fixed above the bottom inset. Attribution
and enrichment details remain in detail presentations, outside introduction.
TTS reports unavailable Chinese voice support and stops on background/disposal.

Other activities show the pinned Hanzi, Pinyin, Vietnamese meanings and optional
Hán-Việt reading. Reviewed examples, notes and components expand on demand. Optional
missing audio is explicit. The model mapper strips text/asset IDs from UNAVAILABLE
and UNREVIEWED enrichment even if a malformed response contains them.

Each renderer receives a published activity definition, its UUID, required flag and
repetitions. No default activity sequence or local answer key is installed:

| Activity | Android behavior and receipt |
| --- | --- |
| INTRODUCTION | Pinned word presentation and explicit reading acknowledgement → ACKNOWLEDGE |
| COMPONENTS | Character-position groups, reviewed roles and explanations → ACKNOWLEDGE |
| STROKE_ORDER | Guided writing state (3A): referenced animation with replay, faint character/grid and timed ink canvas; explicit ACKNOWLEDGE after media loads |
| HANDWRITING | Independent writing state (3B): word chip, shared canvas, ML Kit first-candidate comparison; matching ink → normalized FREEHAND evidence after 1200 ms feedback |
| QUIZ | Server prompt/options, explicit index selection, server accepted/rejected feedback → CHOICE |
| PRONUNCIATION | Reference audio, user-triggered microphone permission, visible recording/stop and explicit submission → SPEAKING duration |

The shared WritingScreen derives guided/independent mode from the pinned activity.
DrawingCanvas reuses DrawingGridCanvas gesture collection and rendering; original
x/y/timestamp strokes survive recreation through the existing identity-scoped draft.
Undo and clear are explicit. Digital Ink receives strokes, never a bitmap or an
external image request. Only the first raw candidate is compared to the complete
pinned word; a later matching candidate cannot pass. Empty input disables Check.
Mismatch shows a 2000 ms error without clearing ink; model/inference errors also
retain ink. Matching input shows success for 1200 ms before submitting the original
evidence and advancing through server-accepted activities. Late results from another
activity/run/ink snapshot are ignored. The existing minimum 1000 ms participation
requirement remains: matching shorter input asks the learner to write more before
showing success. The server still records writing participation rather than a
recognition grade; the client comparison is practice feedback, not stroke-order or
writing-quality assessment. No backend/schema changes are needed.

The roadmap word projection has no authoritative stroke-count field. The animation
caption therefore reads “Nhấn ▶ để xem lại” without inventing a count. Header and
MascotChatBar/CTA remain visible while the main writing area scrolls on small screens.

Speaking is participation only. Speaking captures PCM into a short-lived
buffer, discards each buffer immediately, and derives duration from captured samples.
No recording is written to disk, retained for replay or uploaded. Permission denial,
missing hardware and capture failure prevent submission and provide concise feedback.
Backgrounding/disposal releases playback and cancels capture.

Review Nodes show the group words, activity/repetition progress, server feedback and
completion/EXP result. They use only roadmap APIs. Android does not inject a daily
ReviewRepository or invoke an FSRS endpoint from this feature.

Skip requires “Đã biết từ này?” confirmation and is offered only for unfinished
NEW_WORD lessons. Skipped nodes resume their original owned run. Completion requires
all server-accepted required repetitions; no `completed=true` request exists. A
historical completion opens with zero new EXP. Deliberate replay gets a new UUID;
retries and restoration retain that replay UUID. The completion response alone supplies
EXP; the client never increments a balance or writes vocabulary/FSRS state.

## Integration and minimal backend additions

`RoadmapApi` uses the same Retrofit/OkHttp instance and `RemoteSessionRepository.authorized`
Bearer/refresh wrapper as existing features. Wire DTOs map to framework-free domain
models through `RemoteRoadmapRepository`; composables access neither Retrofit nor Room.

All existing Phase 6.1 paths and semantics remain. Additions are backward compatible,
with no schema or migration change:

| Contract | Addition |
| --- | --- |
| GET /api/v1/roadmaps/{id}/nodes | `current_position` and `section_positions` for direct window/section navigation |
| POST /api/v1/roadmap-nodes/{id}/start | `accepted_repetitions: {activity_uuid: [zero_based_repetition]}` alongside the original accepted activity IDs |
| GET /api/v1/roadmap-nodes/{id}/assets/{asset_id} | Authenticated bytes for exactly an AVAILABLE reference in the accessible pinned lesson; existing content storage verifies length/SHA-256 |

The asset route calls the same node access checks, refuses unrelated assets, verifies
stored bytes outside the event loop and responds with `Cache-Control: no-store`.
The API must be reloaded/restarted before using the new Android build. No migration is
needed. SQL section aggregation is a constant number of queries per node page, not
one detail/vocabulary query per node.

## Performance and recovery

- Node pages contain at most 50 rows. LazyColumn renders visible rows. Near-end loading
  appends/deduplicates pages; direct jumps fetch a window near the authoritative position.
- Catalog discovery is paginated too. Sections use server minimum positions, not guessed
  progression rules. Every node request pins the selected roadmap version.
- Loaded pages and scroll position live in the graph ViewModel through normal rotation
  and tab/detail navigation. SavedState retains the visible anchor for reconstruction.
- A two-entry cache holds immutable node lessons; prefetch selects only a later node
  already marked accessible by the server. Locked future lessons are never prefetched.
- A bounded 16 MiB media cache belongs to that same graph; each asset download is bounded
  to 16 MiB. Published version/asset identities are cache keys, never private progress.
- Activity receipt responses update the run state directly. There is no full-map/detail
  reload between repetitions. Returning to the map refreshes loaded windows in page
  batches, preserving server authority and existing loaded coverage.
- In-flight actions guard rapid taps. An uncertain receipt retains its complete evidence
  and UUID; editing/submitting new evidence is disabled until retry resolves it. Resume
  can replay that exact pending body even when start already reports it accepted.
- SavedState keeps the active node, replay key, pending evidence, selected activity/word,
  completion presentation and compact original ink. The most recent visited node draft
  is retained on return; draft history is deliberately bounded. Ink is limited to 3,000
  points / 100 strokes with visible overflow feedback; original points are not snapped.
  Long gestures split only at shared original points for the server's 1,000-point limit.
- Cancellation propagates. Auth expiry requests the existing session reload flow.
  VERSION_UNAVAILABLE offers catalog refresh while preserving the recent draft. Owned
  historical runs continue to request their original pinned detail/version.

## Verification

Android command, from `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin --console=plain
```

Final Android result: **159 unit tests passed, 0 failed/skipped**, including **25 new
roadmap tests**. Debug assembly, lint and instrumentation Kotlin compilation passed
in the final combined run (1 minute 55 seconds). Lint reported **0 errors, 106 warnings**;
these include dependency/resource suggestions and media-view compatibility/style
warnings. No release assembly or instrumentation execution is claimed. New tests cover DTO
parsing/authenticated paths, pagination/anchors/sections, node access, empty discovery,
pinned words/enrichment filtering, required/optional repetitions, quiz evidence/feedback,
normalized original ink, draft restoration, microphone submission rules, skip/revisit,
replay UUIDs, uncertain delivery/completion, positive-EXP presentation and identity expiry.
Nine Compose device tests cover empty/word presentation, all six activity renderers and
node labels. **Instrumentation compilation is not device execution.**

Backend commands used the existing venv:

```powershell
.venv/Scripts/python -m ruff check app/schemas/roadmap.py app/api/v1/endpoints/roadmap.py app/services/roadmap.py tests/test_roadmap_android_contract.py
.venv/Scripts/python -m scripts.roadmap_isolated_checks
```

Full isolated backend result: **423 passed, 9 skipped**, 117.01 seconds; isolated
`alembic check` exit 0. Existing exactly-once grants, concurrent completion, no duplicate
collection saves, preserved FSRS memory/history and migrations are included. The added
tests cover receipt reconstruction, independent owners, section/current anchors,
locked/unreferenced assets and content integrity failure. The nine skips require
separate historical migration/reset databases and do not count as passing tests.
The runner explicitly executed its original, FSRS and roadmap nonempty rehearsals.

Fresh test databases with suffix `20261101133739` are intentionally retained. An earlier
run (`20261101133246`) caught the section SQL grouping issue and failed two tests; the
final run above includes its correction. No tests targeted development. Existing
Starlette/SQLAlchemy warnings remain. No dependencies were added or updated.

## Known limits

- No emulator or physical-device execution has been performed for this change. Native
  audio, permissions, ML Kit download, animation and touch/lifecycle behavior still need
  the device checks below.
- SavedState supports normal Android restoration; this does not promise force-stop,
  task-removal, reboot or durable offline draft persistence. There is no new local
  progress database and no offline sync queue.
- A response lost after the first EXP grant may return zero when completion is retried,
  per the existing server contract. Android displays that authoritative zero; it does
  not guess the lost grant. Refreshing/revisiting never re-presents an old positive grant.
- Stroke assets support GIF on API 24+, platform-decodable images and animated WebP on
  API 28+. PNG/JPEG can display a reviewed static diagram. SVG, HTML, video and arbitrary
  stroke-data JSON are not implemented and fail visibly without enabling acknowledgement.
  The contract has one lesson-level stroke asset, not per-character asset mappings. The
  character selector changes the target display; it does not invent separate animations.
- Text enrichment can render reviewed inline text or referenced UTF-8 `text/plain`;
  image enrichment uses the same renderer. Unsupported media is explicit. For a complete
  first release, choose the supported formats below and physically verify them.
- Audio uses Android platform decoders; publish device-compatible audio such as reviewed
  MP3/AAC, not an untested codec. Text-only audio enrichment cannot supply playback.
- Speaking requires a usable microphone and at least one captured second for a receipt.
  A required speaking activity cannot be bypassed after denial/hardware failure; it can
  be retried later. There is no tone/phoneme/handwriting-quality scoring.
- Roadmap Review Nodes do not change FSRS. NEW_WORD collection insertion/deduplication
  remains exclusively the existing server completion transaction.

## Physical-device checklist

Use an isolated emulator/test phone and an isolated backend with synthetic accounts and
explicitly authorized test content. Do not submit practice to real learner accounts.
`connectedDebugAndroidTest` uninstalls the app in this setup; do not run it on a phone
holding the user's sign-in or drafts. Use `adb install -r` for ordinary APK updates.

1. With the empty development catalog, check Learning → Roadmap, the Vietnamese empty
   state, Back, all four main tabs, dictionary, saved words and logout/account switching.
2. Against isolated published fixtures, inspect all node states, review/word distinction,
   long titles, large fonts, TalkBack, sections, 1,000+ nodes, current jump and pagination.
3. Open a one-word fixture; verify every displayed field against the pinned catalog
   revision, optional missing media and hidden unreviewed material. Test multi-character
   word/character selectors and several reviewed components for one character.
4. Verify GIF/animated WebP play/pause/replay and audio pause/stop on backgrounding. Test
   missing, corrupt, unsupported and oversized assets plus retry.
5. Draw with a finger and stylus, several characters, undo/clear, recognition/model
   download failure, rotation during a gesture, background/foreground and returning
   from map. Confirm that the original ink remains and no quality score appears.
6. Deny/revoke microphone permission, deny permanently, test missing hardware and the
   system microphone privacy switch. Grant only after tapping Start; check recording
   indicators, stop, cancellation on background/Back, repetitions, and no audio files.
7. Submit an incorrect then correct quiz option; repeat with rapid taps, lost responses,
   offline retry and recreated activity. Inspect that retries use the identical UUID/body.
8. Skip/revisit/resume, complete once, rotate on the result, revisit it and replay twice.
   Confirm one EXP grant and one saved vocabulary identity using isolated assertions.
9. Complete/replay a Review Node; compare FSRS difficulty/stability, due dates and history
   before/after. They must be unchanged. Test auth expiry and a roadmap version change
   while a run is open; historical evidence must remain bound to the original version.

## Making the first real roadmap playable (operator steps, not executed)

1. Keep development at its already-deployed 0015 revision. Restart the API with the new
   backward-compatible routes/fields and install the verified debug APK. Use the existing
   USB `adb reverse tcp:8000 tcp:8000` workflow or an explicitly configured reachable
   debug URL. Confirm authenticated discovery is still empty before publication.
2. Select real HSK 0 vocabulary identities and their **current reviewed installed** catalog
   versions/checksums. Verify Hanzi, tone-marked Pinyin, meanings and optional Hán-Việt.
   Do not copy assumed version-1 IDs from the example file without catalog verification.
3. Author a new strict roadmap JSON using `app/schemas/roadmap.py`: stable roadmap/node/
   activity UUIDs, ordered positions, NEW_WORD with exactly one identity, explicit
   repetition/required flags and REVIEW scope equal to each preceding introduction group.
   Use server-owned CHOICE answers. The existing example is a structural reference only,
   not a reviewed full course or an all-six-activity lesson.
4. Obtain reviewed real audio and stroke animations and register their immutable Asset
   rows/objects through the existing content-authoring workflow. Use audio/mpeg (or
   device-verified AAC), GIF for broad stroke-animation support, correct SHA-256/length,
   and assets no larger than 16 MiB for this client. Provide reviewed inline examples,
   notes and component explanations with valid character positions. Set missing optional
   enrichment UNAVAILABLE; never publish UNREVIEWED. A required stroke activity needs a
   supported renderable asset. Test all six activity kinds in an isolated release first.
5. Obtain separate authorization for development content import/publication. From
   `backend/`, substitute the real reviewed draft path, returned version UUID, and an
   actual operator/ticket identity in these commands:

   ```powershell
   .venv/Scripts/python -m scripts.roadmap validate content/roadmaps/hsk-0.reviewed.json
   .venv/Scripts/python -m scripts.roadmap import content/roadmaps/hsk-0.reviewed.json
   .venv/Scripts/python -m scripts.roadmap preview <version-uuid-returned-by-import>
   .venv/Scripts/python -m scripts.roadmap publish <version-uuid> --reviewed-by '<real operator and review ticket>'
   ```

   Preview verifies exact catalog references and object integrity. Resolve every review/
   asset issue before publish. **Publish atomically activates that release**; a separate
   activate command is needed only when selecting an already published version later.
   Never edit a published version; corrections require a new version.
6. Confirm authenticated GET `/api/v1/roadmaps` contains that active release and node
   discovery returns its server-computed first available node. Complete the physical
   checklist on an isolated account/environment before any authorized real learner test.
   Only then describe that specific published development roadmap as playable.
