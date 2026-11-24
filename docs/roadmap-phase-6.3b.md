# Phase 6.3B: first HSK 0 pack preparation

Prepared 2 November 2026. **Not published, activated or playable in development.**
The complete private review packet has real source assets and 22 activities, but requires
17 content-bound human reviews plus an overall educational review and separate release
authorization. No development catalog, learner, EXP, mastery, schedule or review was written.

## Final proposed structure

The final proposal is `backend/content/roadmaps/preparation/hsk-0-pack/plan-v3.json`.
Version 3 adds visible asset credits to the optimized version 2 proposal. Existing
Phase 6.3A version 1 is preserved; all versions retain the four stable node identities.
Intermediate version 2 preparation files remain historical drafts.

| Node | Required activities | Optional/read-on-demand |
| --- | --- | --- |
| 我 | Introduction, stroke animation, original freehand, pronunciation ×2, tone-mark Pinyin quiz, meaning quiz | Example, usage note and component explanation in shared word details |
| 你 | Same six activities, exact `ni3` identity | Same details; distinguish a component's modern reading from the word's reading |
| 好 | Same six activities, exact `hao3` identity | Same details; distinguish `hǎo` from the separate `hào` reading/sense |
| REVIEW | Three meaning-to-word CHOICE quizzes, one for each preceding identity | Group introduction |

There are **22 activity definitions and 25 possible repetitions**, including the optional
review introduction. Required participation is 24 submissions. The old pack had 31
definitions/repetitions. Separate COMPONENTS screens are unnecessary because the existing
word presentation already expands those explanations. Each word still introduces exactly
one curated identity, with no new lesson table or activity kind.

`activity-audit.json` records an individual keep/remove/optional decision for **all 31 old
activity UUIDs**, including prompts and options. Original NEW_WORD character-recognition
and reverse-meaning quizzes are removed; reverse recall remains in REVIEW. Each word keeps
one meaning quiz and its Pinyin quiz now uses incorrect tones of the **same syllable** as
distractors. REVIEW drops nine redundant questions and retains exactly three reverse
meaning questions. Its introduction is optional, so only correct server receipts for
those three questions are needed. INTRODUCTION and HANDWRITING stable IDs are retained;
audio/stroke activities use the existing stable ID derivation.

`quiz-quality-v3.json` contains the nine final question audits and private server indices.
The supplied alternatives have distinct labels and one exact catalog answer; all three
review option sets contain only 我/你/好. Incorrect tone options are deliberately wrong
answers, not invented dictionary identities or pronunciation assets. Human semantic and
pedagogical review is still required. Learner API and Android fixtures contain no answer keys.

## Lexical and educational verification

A PostgreSQL transaction explicitly set **READ ONLY** reconciled all three identities
against the configured database at `0015_roadmap_engine`. `catalog-preflight.json` records
exact revision and checksum matches, with current visibility true. The existing records
are `LOCAL_CODEX_REVIEWED` under the configured catalog policy, **not human-approved**.
No revision correction, dictionary replacement or new catalog import was necessary.
Rerun reconciliation before any later release; this report is a snapshot, not a permanent guarantee.

| Word | Pinned revision | Mandarin | Hán Việt | Beginner meanings |
| --- | --- | --- | --- | --- |
| 我 | `4ae81805-45f9-5d4f-a576-2a03b4ba27c9`, v1 | wǒ / `wo3` | ngã | tôi; mình |
| 你 | `e611f2a1-17bb-5215-8862-7f69f32ca0fb`, v1 | nǐ / `ni3` | nhĩ | bạn; cậu, second-person singular |
| 好 | `48fd5063-1606-5d90-9943-74d05d8dfc48`, v1 | hǎo / `hao3` | hảo | tốt; ổn; khỏe in an appropriate health context |

The readings/radicals/counts were checked against the publishers' entries for
[我](https://zdic.net/hans/%E6%88%91), [你](https://zdic.net/hans/%E4%BD%A0) and
[好](https://zdic.net/hans/%E5%A5%BD). Hán Việt readings were cross-checked against
[我](https://hvdic.thivien.net/whv/%E6%88%91), [你](https://hvdic.thivien.net/whv/%E4%BD%A0)
and [好](https://hvdic.thivien.net/whv/%E5%A5%BD) in Thi Viện's Hán Nôm dictionary.
These are reading checks, not wholesale dictionary copies. Existing catalog fields remain
the source of runtime lexical data. Other historical/Hán Việt readings are not added to
the selected lexical sense without the existing versioned catalog correction process.

The review packet reuses the catalog's natural short examples as separately reviewable
enrichment: 我在家。/Wǒ zài jiā./Tôi ở nhà.; 你喝茶吗？/Nǐ hē chá ma?/Bạn có uống trà
không?; 我很好。/Wǒ hěn hǎo./Tôi khỏe. The target occurrence, numbered/marked Pinyin,
translation, level and pinned sense are checked structurally. The sentence vocabulary
adds context, not new roadmap introduction identities or review targets. Citation-tone
Pinyin is preserved; it is not a phonetic transcription of tone sandhi. Notes explain
that dictionary Pinyin and connected-speech realization differ, including nǐ hǎo.

The five proposed component explanations are original concise Vietnamese text. 我 identifies
the visible 戈 and its dictionary-radical use without inventing a meaning-composition story.
你 identifies left 亻 and right 尔; this beginner description does not turn 尔's modern
pronunciation into a rule for reading 你. 好 identifies left 女 and right 子 without an
invented historical narrative. The current proposal conservatively labels 尔/子 as structural;
the existing model still supports PHONETIC with appropriately sourced/reviewed explanations.
All origins remain `ORIGIN_UNAVAILABLE`; no historical claim is marked verified. A reviewer
must approve the role, position and Vietnamese explanation of every component.

## Real assets and rights

Six original files are present under `hsk-0-pack/sources/`; none is generated silence or a
synthetic drawing. The source and byte receipts are in `sources/sources.json`, and
[the attribution notice](../backend/content/roadmaps/preparation/hsk-0-pack/ATTRIBUTION.md)
identifies authors, source pages, selected licenses and unchanged status. Per-word credits
are included in the proposed notes for eventual in-app display after review.

The three Mandarin recordings are by Wei Gao and Vion Nicolas, from The Shtooka Project:
[我](https://commons.wikimedia.org/wiki/File:Zh-w%C7%92.ogg),
[你](https://commons.wikimedia.org/wiki/File:Zh-n%C7%90.ogg),
[好](https://commons.wikimedia.org/wiki/File:Zh-h%C7%8Eo.ogg). Their selected license is
[CC BY 2.0 France](https://creativecommons.org/licenses/by/2.0/fr/).
The stroke GIFs are from the Commons CJK Stroke Order Project:
[我](https://commons.wikimedia.org/wiki/File:%E6%88%91-order.gif),
[你](https://commons.wikimedia.org/wiki/File:%E4%BD%A0-order.gif),
[好](https://commons.wikimedia.org/wiki/File:%E5%A5%BD-order.gif), under the offered
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) option. Audio is labeled
HUMAN_RECORDED and stroke assets DATASET. No TTS provider, paid API or new dependency is used.

The downloader checks source license URLs before downloading, matches upstream SHA-1 and
length, then records local SHA-256. It resumes verified per-file checkpoints and refuses
changed originals. A temporary Commons 429 was resolved by resuming later, without substituting
another source. Ogg/Vorbis was added to the existing asset contracts so original audio can
be used directly; Android documents [Vorbis in Ogg support](https://developer.android.com/media/platform/supported-formats).
The bounded parser checks complete pages, CRCs, sequence, stream identity, sample rate,
channels, end marker and duration; it does not claim to evaluate pronunciation.

GIF originals are 100×100, with 30/33/36 decoded frames. Visual inspection of decoded frame
sheets found the expected characters and progressive strokes. Dictionary reference counts
are 我=7, 你=7 and 好=6; reference sequences are 3121534, 3235234 and 531521 respectively.
Frame counts are **not** stroke counts. These small historical GIFs are usable but low resolution;
the educational reviewer must watch complete loops and approve shape, sequence and legibility.
The exact original GIFs are compatible with the existing Android Movie renderer; structured
stroke JSON is unnecessary for this pack and no new animation engine was added.

## Review and publication gates

`review-preview-v3/` and `operator-review-bundle-v3.json` are explicitly **OPERATOR_REVIEW_ONLY**.
They display pending materials for local review/testing but retain all source review statuses
as UNREVIEWED. Their report has **17 HUMAN_REVIEW_REQUIRED errors**, zero missing assets and
two operator warnings. `roadmap import` refuses a marked review-preview directory, and normal
candidate validation refuses its manifest. No review hash or reviewer identity is fabricated.

`draft-v3/` is the normal compiler's safe output: pending enrichment is omitted, so it is not
the complete playable proposal and must not be released as a shortcut. Normal preparation
can be repeated after real reviewers supply exact evidence. `review-bindings-v3.json` lists
the current checksums for the 17 review items; it is not itself approval.

Complete [the exact educational checklist](runbooks/roadmap-phase-6.3b-review.md), return the
reviewer's identity/ticket and corrections, and then prepare a new version/output directory.
Review components/examples/assets before notes, because the notes review binds its whole
enrichment input including those review fields. Recalculate the final notes checksum after
the child reviews are entered. Re-run all gates; approval does not waive errors. Actual
development import/publication/activation still needs separate explicit authorization.

## Validation and release procedure

Executed results and the exact future development publication sequence are recorded in
[the runbook](runbooks/roadmap-phase-6.3b.md). All backend rehearsal writes target dedicated
test databases and rolled-back fixtures. Android media/Compose results are stated there
separately from JVM tests, with device limitations called out. The isolated debug application
ID `.hsk0validation` prevents instrumentation cleanup from uninstalling the user's main app.
No physical pronunciation-quality, tone-accuracy or handwriting-grade claim is made.
