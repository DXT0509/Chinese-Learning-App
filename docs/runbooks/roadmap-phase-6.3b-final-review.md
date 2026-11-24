# HSK 0 final educational review — version 4

Current status: the approved v4 pack is now published and active in local development
under separate Phase 6.3C authorization. See the
[deployment report](hsk0-v4-deployment-20261102.md).

Follow-up: the owner has now supplied the real sign-off identity/reference. See the
[recorded v4 educational sign-off](hsk0-v4-educational-signoff.md) for the current approved
artifacts and deployment boundary. The preparation snapshot below is preserved as history.

Prepared 2 November 2026. The corrected pack is ready for explicit operator sign-off,
**not formally approved, published or activated**. No development asset registration,
content import, EXP grant, learner mutation or FSRS write was performed.

## Corrections and preserved content

Version 3 is preserved byte-for-byte. The corrected unpublished definition reserves roadmap
version 4 and retains all three vocabulary UUIDs/revisions, four stable node UUIDs, 22
activity UUIDs, nine quizzes, six asset source UUIDs and six immutable lesson asset UUIDs.
Only lesson/node **version** identities change, as required by the existing publisher.

1. The 女 explanation now includes: “Trong chữ 好, nét ngang cuối của bộ 女 được viết
   thành nét hất (提), hướng lên bên phải.” It retains separate radical identification
   and the existing disclaimer against invented historical explanations.
2. The imprecise writing hint was removed from the 子 explanation. Its replacement describes
   only 子's position and the left–right structure of 好; 女's technique is no longer
   assigned to a different component.
3. The 你 note now explicitly describes the first of two adjacent third tones as read
   like a second tone, using ní hǎo as the spoken example while retaining dictionary
   Pinyin nǐ hǎo. No automatic tone conversion of longer third-tone strings is implied.

The rising stroke agrees with the existing [好 GIF](https://commons.wikimedia.org/wiki/File:%E5%A5%BD-order.gif)
and inspected frame sheet. The primary textbook search extract also describes 女字旁's
final horizontal becoming a rising stroke; its full PDF could not be fetched, so no full
textbook inspection is claimed. The tone explanation is corroborated by the publisher's
[greeting lesson](https://www.chineseclass101.com/lesson/taiwanese-mandarin-survival-phrases-4-basic-greetings?lp=122).
Historical origins remain unavailable; visible structure, dictionary radical, writing
technique and historical character formation are not treated as interchangeable claims.

All three lexical identities and Hán Việt readings were rechecked against the linked
publisher/dictionary entries in `vocabulary-audit.json`. The examples remain 我在家。,
你喝茶吗？ and 我很好。 with their existing citation Pinyin and Vietnamese translations.
They are short contextual illustrations, not a claim that every sentence word or grammar
pattern has already been introduced. No curated record correction is needed or made.
The distinction between hǎo/tốt and the separate hào/thích reading is preserved.

## Exact artifacts and counts

All final artifacts are in:
`backend/content/roadmaps/preparation/hsk-0-pack/final-review-v4/`.

| File | Purpose |
| --- | --- |
| `plan.json` | Corrected strict preparation schema, pending exact review hashes |
| `bundle.json` | Complete 22-activity operator review bundle, explicitly OPERATOR_REVIEW_ONLY |
| `content/roadmap.json` | Existing executable lesson schema, three NEW_WORD and one exact REVIEW |
| `content/manifest.json`, `content/assets.json`, `content/objects/` | Version/checksum bindings, original CAS bytes and provenance |
| `review-status.json`, `review-status.md` | Status and exact payload hash of every required review item |
| `signoff-form.json` | Explicit per-item approval form; reviewer/reference fields are unfilled |
| `review-bindings.json` | Child and parent hashes in dependency order |
| `educational-audit.md`, `vocabulary-audit.json` | Full five-component/three-note/three-example audit and lexical evidence |
| `quiz-audit.json` | All nine private answer keys with unique-correct-answer and scope checks |
| `asset-audit.json` | Six unchanged assets, source/license checks and owner-reported inspection |
| `catalog-preflight.json` | Fresh READ ONLY database reconciliation bound to the exact plan hash |

Required item counts: **APPROVED 0; READY_FOR_APPROVAL 17; REQUEST_CHANGES 0; BLOCKED 0**.
These are six assets, five components, three examples and three notes. Corrections have
been applied; there are no outstanding requested content changes. Each proposed decision
is AI-assisted editorial analysis, not a human signature. Overall pack acceptance and
development write authorization are additional pending release gates, outside those 17 records.

Technical content-validation errors: **0**. The existing compiler still reports **17
HUMAN_REVIEW_REQUIRED approval-gate errors** for the complete private preview, plus its
two operator warnings. Those gates have not been removed or reclassified as passing.
Normal import refuses the OPERATOR_REVIEW_ONLY marker; no degraded omission-only pack is
offered as a substitute for the 22-activity proposal.

## Assets, provenance and quiz decisions

The owner's statement that all three OGG recordings and three GIFs appeared satisfactory
is recorded as **USER_REPORTED_INSPECTION**, associated with the six supplied filenames.
The owner did not provide reviewer identity, review reference or checksum-bound acceptance.
The report is therefore inspection evidence only, not independent acoustic/stroke expertise
or formal APPROVED status. Source bytes, licenses and attribution strings match the frozen
version-3 source records, upstream SHA-1, local SHA-256 and byte lengths. Existing CRC/format
checks pass and per-word notes retain visible creator/source/license/unchanged notices.

Audio retains the offered [CC BY 2.0 France](https://creativecommons.org/licenses/by/2.0/fr/deed.en)
license; GIFs retain the offered [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/deed.en)
option. The six original Commons page URLs are recorded individually in `asset-audit.json`.
Preserve credit and license links, the unchanged notice and absence of endorsement; impose
no incompatible restrictions. No new provenance or licensing discrepancy was found. This
records the source/license review and obligations, not an expert legal certification.
No recording or GIF was modified, re-encoded or substituted.

Every final quiz was inspected. There are three tone-mark reading questions, three
Chinese-to-meaning questions and three review meaning-to-Chinese questions. Correct labels
are wǒ/tôi, nǐ/bạn, hǎo/tốt and 我/你/好 in their corresponding questions. All nine keys match
the selected sense exactly once; labels are distinct and distractors unambiguous within
this three-word pack. New-word meaning distractors follow the existing fixed-group policy;
they do not add vocabulary reference targets. REVIEW follows all three introductions and
has their exact ordered revisions, with no future targets. Answer indices remain operator-only;
the authenticated rehearsal checks that all four learner responses strip them.

## Sign-off procedure — no approval inferred

1. Review `educational-audit.md`, the nine questions and `asset-audit.json`. The current
   proposal hashes are already supplied in the project's existing `Review` structure.
   Do not change a proposed decision to APPROVED without an actual attributable decision.
2. Copy `signoff-form.json` to an operator-owned file such as `child-signoffs.json`. For each
   of the **14 child items** (six assets, five components, three examples) actually accepted,
   set its outer `decision` to `APPROVED` and its nested `review` to `status: REVIEWED`, the
   real `reviewer`, real `evidence` reference and supplied exact `content_sha256`. Leave the
   three notes READY_FOR_APPROVAL. Top-level names alone never approve any row.
3. From `backend/`, apply only those explicit records into a fresh directory:

   ```powershell
   .venv/Scripts/python -m scripts.finalize_hsk0_review --plan content/roadmaps/preparation/hsk-0-pack/final-review-v4/plan.json --signoffs child-signoffs.json --output content/roadmaps/preparation/hsk-0-pack/signed-children-v4
   ```

   The helper validates the form's exact plan hash and each child signature. It then
   recalculates pending notes hashes **after** the child review objects are final. It
   never invents a reviewer/reference or rewrites a stale signed hash.
4. Copy the newly emitted `signed-children-v4/signoff-form.json` to `notes-signoffs.json`.
   Have the operator explicitly accept the three notes using their **new** hashes and
   actual identity/reference. Preserve all 14 already supplied child approvals. Then run:

   ```powershell
   .venv/Scripts/python -m scripts.finalize_hsk0_review --plan content/roadmaps/preparation/hsk-0-pack/signed-children-v4/plan.json --signoffs notes-signoffs.json --output content/roadmaps/preparation/hsk-0-pack/signed-complete-v4
   ```

   Only real accepted rows become APPROVED. Attempting to sign old parent hashes while
   changing child review fields is rejected. Missing, duplicate, mismatched or stale
   records cannot bypass validation. The helper does not use test-fixture names or evidence.
5. Obtain explicit overall acceptance of the exact completed plan hash and all nine quizzes,
   with the real reviewer/ticket. `overall_decision` is an operator record; the helper does
   not supply it or infer pack acceptance from item signatures. Text corrections after
   signing require a new content version and fresh affected approvals. The version-4
   definition is still unpublished, so sign-off-only sidecar updates use fresh output directories.

## Future authorized development commands — not executed

Run these only after actual item/pack acceptance, and obtain **separate explicit authorization**
before any staging/registration/import/publication operation. No new migration is required.
The following paths assume the sign-off procedure produced `signed-complete-v4`:

```powershell
$releaseArgs = @(
  '--plan', 'content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/plan.json',
  '--catalog', '../docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl',
  '--asset-root', 'content/roadmaps/preparation/hsk-0-pack',
  '--output', 'content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content'
)
.venv/Scripts/python -m scripts.roadmap check-content @releaseArgs
.venv/Scripts/python -m scripts.roadmap preview-file @releaseArgs
.venv/Scripts/python -m scripts.roadmap prepare-bundle @releaseArgs
.venv/Scripts/python -m scripts.hsk0_catalog_preflight --plan content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/plan.json --output catalog-before-publication.json
.venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs
```

The commands above validate/preview only; staging is a dry run. Stop on errors, failed
catalog reconciliation or omitted intended content. Approvals do not waive errors.
After separate authorization for the actual write plan:

```powershell
.venv/Scripts/python -m scripts.roadmap stage-assets @releaseArgs --apply
$apiStorage = .venv/Scripts/python -c "from app.core.config import get_settings; print(get_settings().content_storage_dir)"
.venv/Scripts/python -m scripts.validate_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/asset-library --storage-dir $apiStorage
.venv/Scripts/python -m scripts.import_content --assets-only --content-dir content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/asset-library --storage-dir $apiStorage
.venv/Scripts/python -m scripts.roadmap import content/roadmaps/preparation/hsk-0-pack/signed-complete-v4/content/roadmap.json
.venv/Scripts/python -m scripts.roadmap preview <version-UUID-returned-by-import>
.venv/Scripts/python -m scripts.roadmap publish <version-UUID-returned-by-import> --reviewed-by '<actual reviewer and accepted review reference>'
```

**Publish atomically activates.** It must be authorized for both publication and activation;
there is no publish-only staging step. If subsequently selecting another already-published
version is authorized, use `roadmap activate 5a8aa397-65fb-5582-b6a1-93a90ad9ebe8 <published-version-UUID>`.
Never run these with the unsigned `final-review-v4/content` proposal.

## Post-publication Android checklist — future, not executed

- [ ] Confirm the authenticated catalog exposes the intended published version and exactly 我 → 你 → 好 → REVIEW.
- [ ] Use a separately authorized QA account; verify Chinese, citation Pinyin, Hán Việt, meanings, the corrected 女 explanation and expanded per-word license credits.
- [ ] Listen to all three unchanged recordings and watch all three full stroke loops at the rendered size, including 女's rising stroke in 好.
- [ ] Write original unsnapped strokes, undo/clear them and submit; confirm no fabricated handwriting-quality score.
- [ ] Exercise explicit choice/submit, wrong-answer feedback, required repetitions and microphone permission handling; pronunciation remains participation only.
- [ ] Confirm skip/resume/replay behavior, optional review introduction and authoritative completion: first-completion EXP 10/10/10/15, repeated completion/replay zero.
- [ ] Verify exactly three saved words enter pending intake without artificial mastery or FSRS attempts, and unrelated existing users/schedules/history remain unchanged.
- [ ] Verify logout/account isolation, media lifecycle handling and version-pinned resume; use separately authorized depublication if withdrawing a release, never a database reset.

## Verification results

Full isolated backend result: **470 passed, 9 skipped, 4 warnings**, in **115.54 seconds**.
Isolated `alembic check` exited **0**. All eight databases with suffix `20261102101729`
are intentionally retained; no reset or downgrade was performed. The legacy, FSRS-v2
and roadmap nonempty migration rehearsals ran; the nine skips require separate historical
migration/operator/reset URLs and are not counted as passing checks. Existing Starlette/httpx
and SQLAlchemy reflection warnings remain.

The real-pack HTTP publication/activation rehearsal runs for both v3 and corrected v4,
inside rollback-only isolated fixtures. It confirms exact accessible assets, key removal,
all required participation, authoritative progress (4 completed, 0 skipped), exactly three
pending saved words with mastery 0, four unique grants totalling 45 EXP, completion retries
awarding zero, and unchanged FSRS memory/attempt counts. Existing nonempty preservation
and concurrency tests also pass. Its test-only catalog/release annotations are not copied
to this pack's review records or used as educational approval.

Ruff passes across `app`, `scripts`, `tests`; all four changed Python files pass formatting.
Focused sign-off tests additionally exercise missing reviewer fields, partial child acceptance,
stale signatures, exact form hashes and child-before-parent dependency handling. Their final
rerun is recorded in the generated verification summary. No new dependency or migration is needed.

The earlier checkpoint's 161 JVM and 14 device tests remain prior evidence for the unchanged
Android contracts and the same six asset bytes. They are not claimed as rerun in this final
text/sign-off correction phase. No Android source or activity contract changed in this phase.
