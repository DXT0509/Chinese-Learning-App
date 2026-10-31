# Phase 4.1D coverage checkpoint — 2026-10-28

Historical checkpoint: the subsequent [complete preparation report](srs-phase41d-completion.md)
resolves all 242 remaining policies. This original audit/checkpoint is retained
unchanged below for provenance. Development still has 2,148 installed policies.

**Incomplete: 242 published identities still require editorial POS review.**
Development was inspected read-only and remains unchanged. This checkpoint is not
a claim of complete linguistic coverage or permission to install anything.

The current development target is `chinese_learning`, `127.0.0.1:5432`, role
`postgres`, revision `0012_srs_review_engine`. Actual counts match the historical
baseline: 2,810 catalog identities, 2,804 published, six protected unpublished,
2,148 installed policies and 656 published identities without a valid policy.

The additive candidate bundle contains **2,562 policies**, retaining all 2,148
installed payloads verbatim and adding **414**. Proposed coverage is **91.37%**;
live coverage remains **2,148 / 2,804** until a separately authorized installation.
No vocabulary content, identity, publication evidence, learner state or scheduling
algorithm was changed. The exact list of corrected vocabulary metadata is `[]`.
There are 43 authored **policy prompt** decisions, not vocabulary corrections.

| App level (HSK 2.0 reference) | Published | Installed valid | Proposed valid | Proposed coverage | Pending |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 218 | 112 | 209 | 95.87% | 9 |
| 1 | 289 | 110 | 274 | 94.81% | 15 |
| 2 | 158 | 142 | 158 | 100% | 0 |
| 3 | 294 | 276 | 294 | 100% | 0 |
| 4 | 599 | 536 | 596 | 99.50% | 3 |
| 5 | 1,246 | 972 | 1,031 | 82.74% | 215 |
| Total | 2,804 | 2,148 | 2,562 | 91.37% | 242 |

## Complete inventories and root causes

- [Original read-only audit](srs-phase41d-baseline.json): all 2,810 exact identities,
  versions, checksums, source meanings, Hán-Việt and POS, with overlapping original
  exclusion reasons. Filter `published` and `status == NEEDS_GRADING_REVIEW` for
  the complete original set of 656.
- [Final proposed audit](srs-phase41d-final-audit.json): the same complete denominator,
  plus levels, Vietnamese source contexts, installed/proposed separation, candidate
  conflicts, original reasons and remaining blockers. `baseline_counts` in this
  final file includes the additional 43 preserved authored policies; use the
  original audit for the untouched 656 baseline.
- [Editorial checkpoint](datasets/srs-phase41d-editorial-checkpoint.json): all 242
  pending identities, full source revision payloads, bindings, publication state,
  exact original labels and next action. No pending item is marked reviewed or
  unresolvable. This is the durable continuation input, not an approval receipt.

Original reasons among the 656 published uncovered records overlap:

| Reason | Published uncovered count | Finding |
| --- | ---: | --- |
| Compound POS | 214 | Source categories need parsing and whole-lexeme multi-select, not positional gloss/POS alignment. Some also contain unsupported structural labels. |
| Unsupported POS | 239 | Broad dictionary labels do not always specify grammatical function. |
| Missing/unsuitable Hán-Việt | 202 | Absence of this optional cue does not make known Vietnamese meanings unusable. Source Vietnamese context can supply a question. |
| Shared Hán-Việt | 61 | Shared readings alone are not semantic collisions; meanings and length also matter. |
| Gloss contains Chinese | 2 | Copying the original gloss would leak Hanzi; authored Vietnamese-only questions resolve the policy prompt. |
| Missing POS | 0 | Synthetic regressions still require a genuine category or documented editorial exception. |
| Multiple pronunciation identities | 0 | Both alternate readings of `谁` are protected unpublished; neither is made gradable. |
| Stale installed bindings | 0 | Exact version/checksum matches were verified. |

The 242 pending records are 215 `idiom`, 13 `phrase`, five `phrase; modal`, four
`word element`, and one each `quantifier`, `verb phrase`, `phrase; time`,
`phrase; locality`, `phrase; adverb`. These labels require investigation; this
checkpoint does not assert that their POS is unknowable. In particular it does
not classify every idiom as an adjective or skip the POS stage on every phrase.
Incomplete examples are not an independent blocker for the proposed entries;
each generated question without usable Hán-Việt requires usable Vietnamese example
context. Existing cue-bound policies do not require an example.

## Implementation and linguistic scope

`policy_coverage.py` extends the existing preparer under `catalog-context-v2`.
The original `catalog-cued-v1` algorithm and immutable payloads remain usable.
Source-supported POS lists become exact-set multi-select answers. Recognized
subtypes normalize `proper noun` to noun and `modal verb` to verb; explicit
time/locality/word-element annotations qualify an existing supported category.
Bare structural labels remain pending. This follows the existing broad category
system; it does not synthesize a category from Vietnamese delimiter positions.
References consulted: [Oxford Chinese grammar database](https://www.ctcfl.ox.ac.uk/materials_lang-work_grammar-database_grammar-database-content/)
and [Word Classes of Spoken Chinese, publisher excerpt](https://tuttlepublishing.com/content/docs/9780804840187/PDFs/Word%20Classes%20of%20Spoken%20Chinese.pdf).

The new generator retains all glosses, optional usable Hán-Việt, character count
and safe source Vietnamese context. It checks overlapping glosses against all
same-length candidates, including unpublished records. A missing cue on either
candidate cannot be used to escape a conflict. Multiple reading identities are
not merged. Such mechanical comparison does not establish equivalence of every
Vietnamese paraphrase or detect all possible synonyms outside this catalog.

371 new generated policies use those reusable rules. Their source gloss/POS/cue
and Vietnamese example inventory was inspected in this session for question
compatibility; this is not a new nine-area certification of all underlying
published vocabulary. The bundle remains an operator-review candidate.

43 additional prompts were individually authored after inspecting the actual
collision inventory and source records. [Authored notes](../backend/scripts/phase41d_context_notes.py)
distinguish, for example, `拍照`/`照相`, `作`/`做`, `报道`/`报导`, `星期天`/`星期日`,
and the place suffix variants. Semantic component/stroke cues disclose neither
the written target nor its Pinyin. `明` and `小姐` receive Vietnamese-only questions
without rewriting their approved glosses. [Bound authored policies](datasets/srs-phase41d-reviewed-contexts.json)
record Codex session review, without a human reviewer or fabricated approval.

Every proposed policy still requires Hanzi, tone-correct Pinyin and POS, in that
order. No new alternate spelling or pronunciation is accepted. No policy uses
`pos_skip_reason`. Existing first-answer, assistance, failure and schedule rules
are untouched. The API continues exposing only the current stage question;
accepted answer sets remain server-side.

Generated policies revalidate against current source data at installation and
runtime, with transaction-scoped caches. Installed payloads are never updated.
Changed bindings or invalidated installed policies require a new content version;
they cannot be silently replaced by a different generated policy. Importers
reject duplicate/conflicting identities and preserve reviewed manual payloads.
Dry-run commands enforce repeatable-read, read-only transactions and report
`would_insert` / `would_update` separately from actual writes.

## Executed verification

[Machine-readable verification](srs-phase41d-verification.json) records the exact
bundle SHA-256, development preview and isolated import receipts.

- Backend full suite: **353 passed, 13 skipped** against fresh isolated
  `chinese_p41d_tests_64a086fb54`, with local-review enablement explicitly false.
  An earlier run inherited the development flag and failed one enablement test;
  the explicit test configuration resolved it. Optional dedicated migration and
  race fixtures without environment URLs remain skipped.
- Final targeted coverage unit rerun: **26 passed**. The new PostgreSQL test also
  passed in the full suite: installation preserves saved state and the Hanzi wire
  response contains the complete prompt/count without hidden answer sets.
- Ruff repository check and changed-file formatting check passed.
- Fresh blank migration through head and `alembic check` passed on both isolated
  test and restored-catalog databases. No schema migration was added.
- A fresh development dump was restored to isolated
  `chinese_p41d_rehearsal_64a086fb54`. First import: **414 inserted, 2,148 unchanged**.
  Second import: **zero inserted, 2,562 unchanged**. Runtime resolution checked
  every published identity: **2,562 gradable**. Regeneration matched bundle bytes.
- Complete JSON fingerprints, including the attempt submission journal, matched
  between current development and the restored rehearsal for every non-policy
  table. No real learner review was submitted. Rehearsal fixtures remain intact.
- Android `testDebugUnitTest assembleDebug lintDebug`: **BUILD SUCCESSFUL**, using
  the installed Gradle 9.2.1 and Android Studio JBR with cached dependencies.
  The wrapper's first sandboxed download attempt failed; the installed offline
  distribution completed verification. No emulator or physical-device validation.

Android already renders `prompt_vi` in full, character counts, radio buttons for
single-select, checkboxes for multi-select, and server-declared skipped stages.
No Android source change was necessary. Existing handwriting and random session
selection were preserved and their unit tests remained included.

## Continue without repeating completed work

Use the bound editorial checkpoint, beginning with the nine level-0 and fifteen
level-1 identities, then the three level-4 phrases and 215 level-5 idioms. Inspect
the full original source example, sense, translation and pronunciation before
choosing grammatical categories. For a real content correction, author a separate
`content_version + 1` record retaining UUID/lexical key, and follow all nine checks
in [the local Codex workflow](runbooks/local-codex-vocabulary.md). Do not generate
PASS notes mechanically from these pending rows. Prepare new version-bound
policies only after that review. Review/publication and installation need separate
previews and operator authorization; no such writes occurred here.

Follow the [installation and post-deployment runbook](runbooks/srs-phase41d-installation.md)
for the current 414-policy candidate. Installing it alone will leave 242 published
items uncovered and is not completion of Phase 4.1D.
