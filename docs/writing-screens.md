# Writing steps 3A and 3B

The roadmap `STROKE_ORDER` and `HANDWRITING` activities use two modes of
`WritingScreen`, sharing the controlled `DrawingCanvas`.

- Guided mode gives 40% of the working area to the reviewed stroke animation and
  caption, and 60% to the guided canvas and Undo/Clear toolbar. Replay restarts the
  animation. Continue requires a successfully rendered published asset.
- Independent mode shows the word, Pinyin and Vietnamese meanings above the canvas,
  without an animation or guide character. Check requires completed ink and is
  disabled during a gesture, recognition or pending delivery.
- The existing ML Kit Digital Ink adapter consumes timed strokes, as selected for
  this implementation. Only the first raw suggestion is compared to the full target.
  A mismatch preserves ink and shows feedback for 2 seconds. A match shows success
  for 1.2 seconds before submitting participation evidence and advancing. Existing
  server participation requirements and retry semantics remain authoritative.
- The roadmap contract does not supply stroke counts. The caption shows the replay
  instruction alone until reviewed count data is available; no counts are inferred.

`DrawingCanvas` accepts nullable `guideCharacter`, `showGrid`, `onStrokeAdded` and
`onCanvasExport`. Increment `exportRequest` after layout and after completing a
gesture to request an opaque white Bitmap containing completed ink only. The
recipient owns the returned Bitmap. Guides and UI decoration are excluded. ML Kit
does not need the Bitmap, so the writing screen does not allocate one on Check.

The working area scrolls on short screens while the mascot and primary action stay
outside that scroll area. Draft ink and activity selection retain the existing
identity-scoped ViewModel restoration behavior.

Verification: `RoadmapTest` covers first-suggestion grading, empty canvas, mismatch,
recognition failure, duplicate checks, success timing and evidence submission.
`DrawingCanvasUiTest` covers Bitmap coordinates, dots, explicit export, exclusion of
guides and cleared ink. Instrumentation tests require a device or emulator.

Executed validation (2026-11-09):

- `testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin`: passed;
  167 unit tests, no failures, and no lint errors (warnings remain).
- Isolated `connectedDebugAndroidTest` with `-PISOLATED_HSK0_TEST=true` on
  SM-A225F / Android 12: 4 tests passed, comprising `DrawingCanvasUiTest` and the
  `RoadmapUiTest` methods `independentWritingShowsWordAndDisablesCheckAfterUndoAndClear`
  and `guidedWritingShowsAnimationAreaAndRequiresAvailableMedia`.
  These UI tests use synthetic content; real ML Kit model inference and published
  animation playback were not exercised by this device run.
