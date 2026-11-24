# HSK 0 educational review checklist

Proposal: `backend/content/roadmaps/preparation/hsk-0-pack/plan-v3.json`.
Full private packet: `operator-review-bundle-v3.json`. Human approval: **PENDING**.
The checklist requests educational review only; it does not authorize development writes.

Reviewer must supply a real name/identity, evidence or review-ticket reference, decision,
corrections and the exact content checksum for each accepted item. Do not copy a test
fixture's attestation. Current item hashes are in `review-bindings-v3.json`; any content
change requires a fresh hash. Recalculate notes hashes after all child reviews are final.

## Vocabulary and examples

- [ ] Confirm pinned 我/wo3, 你/ni3 and 好/hao3 identities and revision 1 checksums in `catalog-preflight.json`; approve meanings tôi/mình, bạn/cậu and tốt/ổn/khỏe in context.
- [ ] Confirm Hán Việt ngã, nhĩ and hảo are appropriate for these selected senses; they are not Mandarin pronunciation instructions.
- [ ] Approve 我在家。/Wǒ zài jiā./Tôi ở nhà.; verify grammar, target position 0, translation and beginner suitability.
- [ ] Approve 你喝茶吗？/Nǐ hē chá ma?/Bạn có uống trà không?; verify target position 0 and neutral-tone ma.
- [ ] Approve 我很好。/Wǒ hěn hǎo./Tôi khỏe.; verify target position 2, health sense and citation-tone Pinyin.
- [ ] Confirm contextual sentence words do not become roadmap targets and examples do not misleadingly promise that their entire grammar has already been taught.

## Five component explanations and three notes

- [ ] 我: 戈 at OVERLAPPING, structural/radical-identification explanation; no invented etymology or meaning-composition claim.
- [ ] 你: left 亻, semantic-radical explanation; distinguish dictionary radical from a universal meaning rule.
- [ ] 你: right 尔, structural beginner explanation; no claim that its modern pronunciation determines nǐ.
- [ ] 好: left 女, dictionary-radical explanation without an invented historical story or social claim.
- [ ] 好: right 子, structural explanation and relevant writing hint.
- [ ] Approve the 我 usage/pronunciation note, including third tone and Hán Việt distinction.
- [ ] Approve the 你 note, including third-tone sandhi in 你好 versus citation Pinyin.
- [ ] Approve the 好 note, including the separate hǎo/hào identities and health-context meaning.
- [ ] Check all three notes include the correct asset authors, original source links, license links and unchanged status. Confirm credits remain visible in expandable lesson details.

## Six real assets

- [ ] Listen to `sources/wo.ogg` and approve actual Mandarin wǒ, tone, recording quality and lack of clipping/unwanted content; confirm human-recorded source identity.
- [ ] Listen to `sources/ni.ogg` and approve nǐ with the same checks.
- [ ] Listen to `sources/hao.ogg` and approve hǎo, explicitly excluding hào.
- [ ] Watch all of `sources/wo.gif`; approve 我, 7 strokes, PRC sequence 3121534 and legibility at app size.
- [ ] Watch all of `sources/ni.gif`; approve 你, 7 strokes and sequence 3235234.
- [ ] Watch all of `sources/hao.gif`; approve 好, 6 strokes and sequence 531521.
- [ ] Confirm source/license records match originals and attribution obligations are satisfied; approve continued distribution under the selected CC BY licenses.
- [ ] Perform audible playback on supported Android hardware. Decoder preparation alone does not prove speakers or listening quality.

## Activities and release decision

- [ ] Review every row in `activity-audit.json` (31 originals) and all nine final questions in `quiz-quality-v3.json` (private answer keys).
- [ ] Confirm exactly one correct answer per question, tone alternatives genuinely incorrect for the selected identity, and plausible unambiguous meaning distractors.
- [ ] Approve six steps per word, two speaking repetitions, original unsnapped freehand and the absence of automated quality scores.
- [ ] Approve the optional review introduction and three required in-scope reverse-recall questions, with no future identity leakage.
- [ ] Review Android/API/isolated-rehearsal results and any remaining device limitations in `roadmap-phase-6.3b.md`.
- [ ] Return an explicit ACCEPT / REQUEST_CHANGES decision with reviewer identity and evidence. No unresolved errors may be waived.

After acceptance, obtain **separate authorization for development asset registration,
draft import, publication and activation**. Existing `publish` atomically publishes and
activates; it must not be run when only draft import has been authorized.
