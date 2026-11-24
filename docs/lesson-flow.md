# Sequential lesson flow

The roadmap lesson entry renders `RoadmapLessonFlow`. The old word/details panel,
practice count, activity chips and legacy activity renderers have been removed.
The separate CONTENT_PREVIEW player retains its existing preview semantics.

The fixed order is WordIntroductionScreen → CharacterStructureScreen → guided
WritingScreen → independent WritingScreen → PinyinInputScreen →
PronunciationScreen → MultipleChoiceScreen → TranslationScreen → SpeakingScreen
→ LessonSummaryScreen. AppBar and system Back return to the preceding step;
Back at the introduction returns to the roadmap. Navigation is blocked while
required evidence is being delivered. Returning to accepted steps does not create
new server receipts.

One `LessonViewModel`, keyed by pinned node and run inside the identity-scoped
navigation owner, retains the cursor, drafts and score across screens and normal
restoration. It starts at 100, deducts 10 per incorrect content attempt with a floor
of 10, and records mistake/answer counts. Accuracy is correct attempts divided by
graded attempts; infrastructure and permission errors are not content mistakes.
Time runs from the first lesson entry, including background time, and freezes on
the summary. Returning to practice resumes it. A new replay run starts a fresh
score/timer. Group-review words retain the same cumulative score/timer.

Pinyin accepts marked or numbered syllables while preserving tone distinctions;
the answer appears after two mistakes. The speech screens allow three content
attempts each, retaining the limit on Back. They compare recognized Chinese text
with the pinned target, ignoring punctuation; this is not phonetic quality grading.
After success or three content attempts, Continue submits real speech participation.
Permission denial, missing service, short/silent capture, service failures and
timeouts remain retryable and cannot generate a successful participation receipt.
The microphone requests permission only after a tap and stops on background/exit.

Speech recognition uses Android's system SpeechRecognizer in zh-CN. Depending on
the installed service, processing may use its network provider. The app does not
persist audio. The service is canceled/destroyed on exit, and late/duplicate
callbacks are ignored. See the official [SpeechRecognizer lifecycle contract](https://developer.android.com/reference/android/speech/SpeechRecognizer).

Multiple choice uses the server-authored options in a two-column grid (2×2 when
four options are provided); indices are preserved and no distractors are invented.
Feedback comes from the authenticated receipt. Every authored question/repetition
is retained. Additional required repetitions stay within their screen instead of
reappearing as activity chips. A correct result remains visible until Continue.

Translation uses a reviewed pinned example's Vietnamese sentence. Typing and
per-character ML Kit Digital Ink reuse the shared DrawingCanvas; a recognition
mismatch preserves ink. If no reviewed example exists, translation shows that
state explicitly and permits Continue; sentence speaking explicitly falls back
to the lesson word, allowing real remaining speech participation without inventing
a sentence. Required stroke media cannot be acknowledged before rendering.

The flow cursor is separate from server activity selection. INTRODUCTION,
COMPONENTS, STROKE_ORDER, HANDWRITING, QUIZ and PRONUNCIATION retain their existing
evidence contracts. Local Pinyin/translation checks add no backend grades or SRS
writes. Pronunciation submits one real speaking repetition; the final speaking
screen completes remaining repetitions. Server retries reuse the original request
identity. Receipt IDs prevent duplicate local scoring after restoration/retry.
XP is displayed only from server completion, never calculated from the local score.
The final summary automatically requests completion when required receipts are
ready, and otherwise links to the missing required step. No schema change or
content publication is part of this UI change.

Validation targets:

- `LessonViewModelTest`: ordering/Back, scoring floor, Pinyin, speech limits,
  restoration/timing, event deduplication, translation and cumulative group score.
- `RoadmapTest`: existing ownership, evidence, retry and handwriting safeguards,
  plus pinned selection and stable run identity for the sequential flow.
- `LessonFlowUiTest`: full flow, local mistakes, authored quiz feedback, two
  speaking participation submissions, summary completion, Back, drafts and absence of legacy UI.
  This uses synthetic repositories, handwriting results and speech callbacks;
  it does not validate recognition accuracy or a live backend.
- Updated `RoadmapUiTest` and `Hsk0PackUiTest` target the new screens and retain
  published asset decode/playback checks.

Device validation (2026-11-09): 25 tests passed on SM-A225F / Android 12 using
`-PISOLATED_HSK0_TEST=true` and the five classes LessonFlowUiTest, RoadmapUiTest,
Hsk0PackUiTest, DrawingCanvasUiTest and CharacterStructureUiTest. This includes the
complete ten-screen flow and Back through the final screens with the accumulated
score/draft intact. The run did not replace the primary installed application.
Live system speech transcription, pronunciation quality, real ML Kit accuracy and
backend connectivity are not established by the synthetic full-flow test.

Final default-build validation: `testDebugUnitTest assembleDebug lintDebug` passed
with 175 unit tests, zero failures and no lint errors. The generated default APK
uses `com.example.chineselearningapp`; it was not installed over the primary app.
