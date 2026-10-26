# Curated Simplified vocabulary schema and API

Phase 4.0.1 adds revision 0009 and the append-only curated_vocabulary_ai_reviews table.
See [AI review contracts, publication policy and commands](ai-vocabulary-publication.md).
HUMAN_APPROVED remains the default publication policy; explicitly enabled AI_APPROVED
publication also requires current-version/checksum review evidence and Vietnamese content.
NEEDS_REVIEW and REJECTED never publish. No existing catalog or user row is reset.

Revision `0008_curated_vocabulary` is additive after 0007. The `curated_` prefix avoids
renaming legacy tables and changing their foreign keys during an ordinary upgrade.
The **only active collection** is curated_user_vocabulary. Legacy user_vocabulary,
srs_states and personal_vocabulary_entries are retired and cleared by explicit reset.

| Table | Identity and purpose |
| --- | --- |
| curated_vocabulary_batches | Text batch ID, immutable byte checksum, UTC import time |
| curated_vocabulary | UUID; unique lexical_key and (simplified,pinyin_numbered); tone-marked and numbered Pinyin; optional Sino-Vietnamese/POS; learning_level 0..5; APP_CURATED classification; HSK_2_0 difficulty reference; review_status; content_version; batch FK; normalized-content checksum; UTC created_at/updated_at |
| vocabulary_meanings | (vocabulary_id,language,position) PK; vi/en nonblank glosses, ordered senses |
| vocabulary_examples | (vocabulary_id,position) PK; Simplified sentence, Pinyin, Vietnamese translation |
| curated_vocabulary_revisions | (vocabulary_id,content_version) PK; checksum, normalized record snapshot, UTC timestamp; explicit human-review evidence |
| curated_user_vocabulary | UUID; users/catalog FKs; UNIQUE(user_id,vocabulary_id); mastery_level 0..5 default 0; next_review_at/last_reviewed_at nullable UTC; saved_at UTC; is_active |
| curated_vocabulary_reviews | UUID; collection FK; UNIQUE(user_vocabulary_id,submission_key); pinned content version; Vietnamese prompt; Simplified handwriting-recognition text; typed Pinyin; result JSON; submitted_at UTC |

No new table stores Traditional Chinese. Meaning/example/revision children cascade only
from a curated lexical parent; user associations restrict lexical deletion. User identity
is always the authenticated users UUID. Review history restricts collection deletion;
removing a saved word deactivates it and retains its mastery/history.

Identity is `simplified|numbered pinyin`, e.g. `行|hang2` versus `行|xing2`. A dedicated
UUIDv5 namespace isolates new IDs from CC-CEDICT IDs. Meaning corrections retain identity
and increment content_version; form/pronunciation changes create a new identity. Multiple
ordered meanings represent senses of one reading; homographs with different readings
are separate words. A changed batch ID cannot rewrite an existing content version.

Draft import statuses are GENERATED_UNREVIEWED or NEEDS_REVIEW only. HUMAN_APPROVED requires
a separate checksum-bound review command with a named reviewer, retained in revision
evidence. AI_APPROVED requires separate independent semantic evidence; REJECTED records
remain unpublished. Content revisions return to an unapproved status. Approved-only API predicates
also require at least one usable Vietnamese meaning. PostgreSQL checks level/mastery,
quality enum, classification, positive versions, meaning languages and uniqueness.
A BEFORE INSERT collection trigger requires approved Vietnamese content and mastery zero.

Learning level is editorial difficulty, not verified HSK membership. Level 0 is app-defined;
1..5 are app classifications. HSK_2_0 is a named difficulty reference, never a membership
claim. No automatic HSK mapping, TEACHES provenance, lesson completion, mastery evaluator,
interval calculation or handwriting grading is implemented.

Future scheduling can use the (user_id,is_active,next_review_at) index and join the approved
catalog/vi meanings. A future review must use a Vietnamese meaning prompt, a Simplified
handwriting answer and typed Pinyin. Review history has a collection-scoped submission key
for idempotency; the future transactional evaluator must compare duplicate request payloads,
return the stored result and update this SAME mastery/schedule. There are no review cards
or due-review endpoints in this phase. No second state is allocated for roadmap words;
future roadmap enrollment must call the same collection save operation.

## Updated authenticated APIs

All paths are under `/api/v1`, require the existing Bearer session, and retain existing
pagination/ownership conventions. Auth/session behavior is unchanged.

| Method/path | Contract |
| --- | --- |
| GET /dictionary/search?q=&limit=20&offset=0 | Simplified/Pinyin/Vietnamese/optional English literal substring search; exact Simplified first, deterministic ordering; items + next_offset; approved only |
| GET /dictionary/entries/{entry_id} | Approved detail, or 404 (also for legacy/unknown UUIDs) |
| POST /me/vocabulary | `{dictionary_entry_id: UUID}` selects a curated UUID; idempotent add/reactivation; new mastery 0; duplicate save preserves mastery and scheduling |
| GET /me/vocabulary?q=&limit=20&cursor= | Active saved associations; user-scoped count and keyset pagination; unapproved revisions stay visible as inactive content |
| GET /me/vocabulary/status?dictionary_entry_id= | `{saved_id: UUID|null}`, scoped to owner and active association |
| GET /me/vocabulary/{saved_id} | Owner-only saved detail; 404 for absent/other owner/deactivated |
| DELETE /me/vocabulary/{saved_id} | 204 idempotent owner-scoped deactivation; no cross-user mutation |
| Future due-review lookup | Deferred; must join active due collection + HUMAN_APPROVED vocabulary + usable vi meaning |

`entry_id` and the existing `dictionary_entry_id` request/response names now identify
curated lexical UUIDs. Old provider UUIDs are never remapped to a new word: detail/save
return 404; saved status returns null. Pre-reset legacy personal rows are intentionally
invisible through the new API. No misleading traditional, source_revision, saved_snapshot,
character_enrichments, license or external-provider provenance fields survive in the new
wire response.

Search item example:

```json
{"entry_id":"<curated UUID>","simplified":"学","primary_pinyin":"xué","short_vi_meaning":"học","available_languages":["vi"],"source":"APP_CURATED","content_version":1,"learning_level":0}
```

Detail adds pinyin_numbered, citation_pinyin, meanings keyed by vi/en with
`{sense_number,gloss}`, optional sino_vietnamese and part_of_speech,
`examples:[{simplified,pinyin,vietnamese}]`, review_status and active.
Saved items contain id, dictionary_entry_id, saved_at, simplified, pinyin,
short_vi_meaning, optional short_en_meaning, active, mastery_level,
next_review_at and last_reviewed_at.

## Android compatibility and physical verification

Retrofit DTOs and domain models no longer carry Traditional Chinese or character/provider
provenance. Search/detail/wordbook render curated Vietnamese and optional English content;
detail labels its app-curated source. Existing session refresh, saved state, owner-specific
navigation and UUID selection remain. ML Kit zh-Hans recognition, candidate selection,
query debounce and handwriting Canvas are unchanged. Recognition is a search input only.

From android run `gradlew.bat testDebugUnitTest assembleDebug lintDebug`.
Instrumentation source compilation can be checked with `compileDebugAndroidTestKotlin`;
this is not device execution. On a physical Android device:

1. Install the debug APK, start the migrated API, configure USB/ADB reverse as in
   android-usb-development.md and log in with an existing account.
2. After operator reset and before import, open Dictionary and My Vocabulary. Search,
   refresh, Back and empty collection navigation must work without crashes.
3. Stage an unapproved fixture: it must remain absent from search and unsavable by UUID.
   After real human approval, search by Simplified, tone/numbered Pinyin and Vietnamese.
4. Open detail, verify Vietnamese meanings and no Traditional/provider sections. Save
   twice, reopen My Vocabulary and verify a single entry and persisted saved status.
5. Remove then re-add; verify the same association/mastery, and switch accounts to verify
   isolation. Open an old UUID: show the normal not-found state.
6. Download the existing handwriting model, draw Simplified characters, select a candidate,
   and open the matching curated detail. Verify offline model/error behavior remains.
7. Open the pinned historical preview: confirm self-contained bundle content and bookmark
   resume. This is historical preview behavior, not curated lesson completion.

Physical/emulator execution has not been performed during this phase.
