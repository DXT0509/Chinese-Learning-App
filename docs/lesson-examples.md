# Representative lesson definitions

Status: **illustrative target design fixtures**, 2026-10-18. The actual Slice 1 sample in
backend/content is smaller: exactly 你 / nǐ / nhĩ / bạn, no supplied media or reviewed
analysis, with two reference scenes and no runtime. See [content authoring](content-authoring.md).
The full examples below are not seeds,
migrations, API payloads accepted today, or implemented renderers. See [engine contract](learning-engine-design.md)
and [schema](database-design.md). All strings are UTF-8.

For readability, IDs such as `v-ni`, `scene-intro`, `grammar-svo`, `audio-ni` and
`sentence-love-dad` are symbolic authoring aliases, resolved to stable UUIDs before
publication. `scene_key` aliases denote UUIDs retained across compatible versions;
they are not display order. Configs are representative v1 objects using the registry;
all production defaults must be filled and validated before publication. Required
scene flags mean required if included by the pinned conditional policy. Speaking uses
required valid microphone capture and policy-stt-content-v1. Its PASS/FAIL means recognized
content only, never a pronunciation percentage. Permission/service problems retain
recoverable progress. Approved accessible alternatives are recorded separately.

## 1. Vocabulary — 你

Stable lesson `lesson-ni`, type VOCABULARY, version 1, template `vocabulary-v1`.
Exactly one lesson_vocabulary row: `v-ni`, position 0, role TEACHES.
Catalog: 你; citation nǐ; đại từ; Hán-Việt nhĩ; meaning “bạn; anh/chị (ngôi thứ hai)”.
Audio is the isolated citation reading. HSK is assigned only with a reviewed standard
edition, not guessed here. Character 你 has dictionary radical 人; modern visible
components include 亻 on the left and 尔 on the right. A reviewed character entry may
explain the phono-semantic analysis and historical phonetic relationship; do not claim
that today's ěr predicts nǐ. If that analysis lacks a reviewed source, leave classification
unset and label the decomposition as modern structure only.

| Sequence | Scene and instance expansion | Requirement |
| --- | --- | --- |
| 1 | VOCABULARY_INTRODUCTION, listen and required speaking | Valid microphone recording and STT content PASS; no pronunciation score |
| 2 | VOCABULARY_INFORMATION | Required acknowledgment |
| 3.1–3.2 | CHARACTER_ANALYSIS: 亻, then 尔 | Required reviewed pages, `char:0/component:0..1` |
| 4 | STROKE_ANIMATION: 你 | Required demonstration |
| 5 | HANDWRITING_PRACTICE: 你 | Required freehand capture/confirmation or approved accessibility alternative |
| 6 | SENTENCE_TRANSLATION | Conditional; beginner commonly has no eligible sentences, so skip |
| 7 | LISTENING_TRANSCRIPTION: 你 | Optional extension |

The inherited template provides the core definitions; the lesson binds the single target.
It does not duplicate all scenes in lesson_scenes. Representative intro definition:

```json
{
  "scene_key": "scene-intro",
  "position": 10,
  "scene_type": "VOCABULARY_INTRODUCTION",
  "contract_version": 1,
  "required": true,
  "config": {
    "vocabulary_ref": {
      "binding": "TARGET_VOCABULARY"
    },
    "show_pinyin": true,
    "listen_required": true,
    "recording_policy": "REQUIRED_CAPTURE",
    "speech_evaluation_policy_id": "policy-stt-content-v1"
  },
  "condition": null
}
```

Representative analysis config and resolved reference projection (not another DB row):

```json
{
  "vocabulary_ref": {
    "binding": "TARGET_VOCABULARY"
  },
  "expansion": "PER_COMPONENT",
  "include_unreviewed": false
}
```

Component occurrence `component-ren-left`: glyph 亻, location LEFT, role SEMANTIC,
explanation “Dạng đứng bên trái của 人, liên quan đến người”. The right-hand component's
phonetic role is shown only if reviewed; otherwise UNKNOWN. Dictionary radical 人 is
displayed separately. A stroke animation points at `asset-strokes-ni` with a stable key/hash.

## 2. Vocabulary — 你好

`lesson-nihao`, VOCABULARY v1, TEACHES only `v-nihao`. This is one lexical greeting
entry with two character occurrences, not two automatically learned words. Citation
pinyin is nǐ hǎo. Contextual speech for this greeting is ní hǎo; keep the lexical
citation value unchanged. Vietnamese meaning “xin chào”; optional Hán-Việt “nhĩ hảo”
is a reading aid, not the natural Vietnamese translation. POS is a reviewed greeting/
interjection tag, not a fabricated single-character etymological classification.

Sequence: introduction with greeting audio -> information -> character analysis
你/亻, 你/尔, 好/女, 好/子 -> stroke demonstrations for 你 and 好 -> freehand recall
for both occurrences -> conditional translation -> optional transcription.
好's dictionary radical is 女. The explanation of 女+子 must distinguish the traditional
analysis from an asserted historical fact; etymology/source remain a reviewed character
property. Do not classify the entire expression 你好 as a compound ideograph.

An optional pronunciation explanation is added after introduction; inherited positions
are spaced so this can use position 15 without collisions:

```json
{
  "lesson_version_id": "lesson-nihao-v1",
  "scene_key": "scene-nihao-tone-note",
  "operation": "ADD",
  "position": 15,
  "scene_type": "CONTENT_EXPLANATION",
  "contract_version": 1,
  "required": false,
  "config": {
    "pronunciation_rule_id": "rule-third-tone",
    "example_ids": [
      "pron-example-nihao"
    ]
  },
  "condition": null
}
```

Handwriting config:

```json
{
  "vocabulary_ref": {
    "binding": "TARGET_VOCABULARY"
  },
  "mode": "FREEHAND_RECALL",
  "retries": 3,
  "completion_policy": "CAPTURE_AND_CONFIRM_EACH_CHARACTER"
}
```

A retry preserves natural point order. Its recognition candidate, selected Hanzi and
submitted text are separate state; no recognition service is presumed. Completing this
lesson grants app-learned `v-nihao` only. It does not grant `v-ni` or `v-hao` unless
their own TEACHES completions exist.

## 3. Pronunciation — 不大

`lesson-bu-sandhi`, PRONUNCIATION v1, references reusable `rule-bu-before-fourth`.
UNLOCK prerequisite: completed introductory tones lesson. Vocabulary 不 and 大 are
CONTEXT links, not newly TEACHES merely because they occur in an example.
The example means “không lớn” in this exercise context; 不大 can have other contextual
uses, so do not present that gloss as its only possible meaning.

Stored pronunciation example fields:

```json
{
  "id": "pron-example-buda",
  "rule_id": "rule-bu-before-fourth",
  "vocabulary_id": null,
  "chinese_text": "不大",
  "citation_pinyin": "bù dà",
  "spoken_pinyin": "bú dà",
  "explanation": "不 đổi sang thanh 2 khi đứng ngay trước âm tiết thanh 4.",
  "audio_asset_id": "audio-buda-context",
  "revision": 1
}
```

Sequence: CONTENT_EXPLANATION -> AUDIO_COMPARISON (isolated 不 and contextual 不大,
clearly labeled as different contexts) -> PRONUNCIATION_PRACTICE -> MULTIPLE_CHOICE
about the tone change -> optional LISTENING_TRANSCRIPTION. A citation-form audio is
not mislabeled as a natural contextual model.

```json
{
  "scene_key": "scene-buda-practice",
  "position": 30,
  "scene_type": "PRONUNCIATION_PRACTICE",
  "contract_version": 1,
  "required": true,
  "config": {
    "pronunciation_example_id": "pron-example-buda",
    "replay_policy": {
      "max_replays": null
    },
    "recording_policy": "REQUIRED_CAPTURE",
    "speech_evaluation_policy_id": "policy-stt-content-v1"
  },
  "condition": null
}
```

A valid recording is evaluated through STT_CONTENT_MATCH against 不大. A transcript
match passes content recognition, not tone correctness. A mismatch permits retry; a
permission/network/provider problem leaves the scene BLOCKED without a learning FAIL. 一 rules can reuse this lesson
structure with separate reviewed examples: citation yī, contextual yí before fourth
tone and yì before first/second/third tones in appropriate contexts; isolated/counting/
ordinal exceptions must be taught explicitly, not handled by a blind spelling rewrite.

## 4. Pronunciation — third-tone sandhi in 你好

`lesson-third-tone`, PRONUNCIATION v1, references `rule-third-tone`. UNLOCK introductory
tones. The rule has reusable example `pron-example-nihao`: chinese_text 你好,
citation_pinyin nǐ hǎo, spoken_pinyin ní hǎo, audio `audio-nihao-context`.
Explanation: “Trong nhóm hai âm tiết thanh 3, âm tiết đầu được phát âm gần thanh 2.”
This example illustrates the two-syllable rule, not a universal flattening of every
third tone in long sentences; grouping and actual phonetics require care.

Sequence: explanation -> contextual audio and labeled citation comparison -> pronunciation
practice -> multiple choice -> optional transcription. The separate vocabulary lesson
can reuse this same rule/example without copying the rule text into its scene config.

```json
{
  "scene_key": "scene-third-tone-check",
  "position": 40,
  "scene_type": "MULTIPLE_CHOICE",
  "contract_version": 1,
  "required": true,
  "config": {
    "prompt": "Khi nói 你好, âm tiết đầu thường được phát âm thế nào?",
    "options": [
      {
        "key": "rising",
        "text": "ní (gần thanh 2)"
      },
      {
        "key": "falling",
        "text": "nì (thanh 4)"
      }
    ],
    "correct_option_keys": [
      "rising"
    ],
    "shuffle": true,
    "attempts": 3,
    "hint_policy": {
      "enabled": false
    }
  },
  "condition": null
}
```

The first half of the third-tone syllable is not always realized as a textbook full
dip; the renderer presents reviewed audio, not an inferred numeric pitch trace.

## 5. Grammar — 我的爸爸

`lesson-possessive-de`, GRAMMAR v1, TEACHES `grammar-possessive-de`.
Structure: Possessor + 的 + Noun. Example 我的爸爸, citation teaching pinyin wǒ de bàba,
meaning “bố của tôi”. This is a **noun phrase**, not a full declarative sentence. In
ordinary speech 我的爸爸 and 我爸爸 can both be appropriate; do not mark omission of
的 universally wrong. The targeted exercise explicitly asks for the structure with 的.
The reduplicated 爸爸 commonly has a neutral second syllable in standard Mandarin.

UNLOCK proposal: app-learned 我 and 爸爸. The lesson introduces the grammar and may
display 的 as teaching content, but it does not automatically make 的 an eligible lexical
entry. A separate vocabulary lesson for 的 is required before restricted translation
that uses that particle. Its absence should skip that optional scene, not prevent
introductory grammar teaching. This avoids circular grammar bootstrapping.

Sequence: CONTENT_EXPLANATION -> reviewed example/audio -> FILL_IN_BLANK ->
SENTENCE_ORDERING -> optional listening -> conditional translation only with complete
vocabulary and prior grammar prerequisites. A grammar_examples row links this sentence/
phrase entry to the rule; sentence bank “sentences” also permits reviewed short phrases.

```json
{
  "scene_key": "scene-possessive-order",
  "position": 40,
  "scene_type": "SENTENCE_ORDERING",
  "contract_version": 1,
  "required": true,
  "config": {
    "sentence_id": "phrase-my-dad",
    "token_keys": [
      "token-wo",
      "token-de",
      "token-baba"
    ],
    "accepted_orders": [
      [
        "token-wo",
        "token-de",
        "token-baba"
      ]
    ],
    "attempts": 3
  },
  "condition": null
}
```

The prompt asks “Sắp xếp theo mẫu có 的”. An unrelated scene accepting natural
possessives would need a separately reviewed 我爸爸 variant and its vocabulary/grammar
annotation. Repeated 爸 characters in 爸爸 have different positions even when the sentence
token is one lexical `v-baba` entry.

## 6. Topic — weekdays

`lesson-weekdays`, TOPIC v1, links topic `topic-weekdays`. Sequence: explanation of
星期 -> reviewed weekday cards -> audio/word multiple choice -> listening transcription
-> ordering of weekday labels. Weekday words are CONTEXT initially; if the product wants
the topic to grant lexical knowledge, explicitly mark each taught entry TEACHES and
require corresponding study scenes. The vocabulary-lesson one-entry rule does not
restrict a TOPIC lesson's deliberate multi-entry teaching contract.

| Chinese | Teaching pinyin | Vietnamese |
| --- | --- | --- |
| 星期一 | xīngqī yī | thứ hai |
| 星期二 | xīngqī èr | thứ ba |
| 星期三 | xīngqī sān | thứ tư |
| 星期四 | xīngqī sì | thứ năm |
| 星期五 | xīngqī wǔ | thứ sáu |
| 星期六 | xīngqī liù | thứ bảy |
| 星期日 / 星期天 | xīngqī rì / xīngqī tiān | chủ nhật |

Spacing above separates teaching units; it is not a character-by-character pronunciation
generator. In 星期一, final 一 is yī; do not apply the pre-syllable sandhi rule blindly.
Sunday's two lexical forms have separate IDs and can be approved answer variants when
the question permits either. Vietnamese weekday numbering differs from the Chinese label.

```json
{
  "scene_key": "scene-weekdays-explanation",
  "position": 10,
  "scene_type": "CONTENT_EXPLANATION",
  "contract_version": 1,
  "required": true,
  "config": {
    "topic_id": "topic-weekdays",
    "example_ids": [
      "phrase-monday",
      "phrase-tuesday",
      "phrase-sunday"
    ]
  },
  "condition": null
}
```

No weekdays-specific table is introduced. Topic explanation is reviewed content and
interactive behavior uses the same scene registry as vocabulary/grammar lessons.

## 7. Roadmap review

`lesson-review-01`, REVIEW v1, stable node inserted by editors after a configured target
of five new vocabulary lessons. A pronunciation or grammar node between those lessons
does not increment that vocabulary spacing counter. This is an authoring policy, not
a runtime rule that only vocabulary may occur on the path.

Sequence: meaning MULTIPLE_CHOICE -> pinyin FILL_IN_BLANK -> PRONUNCIATION_PRACTICE ->
HANDWRITING_PRACTICE -> LISTENING_TRANSCRIPTION -> relevant grammar SENTENCE_ORDERING.
Vocabulary memberships have role REVIEWS. The completion rule only checks this run's
required scenes. First node completion can award EXP once; it grants no new vocabulary
and no automatic mastery increase.

```json
{
  "scene_key": "scene-review-meaning",
  "position": 10,
  "scene_type": "MULTIPLE_CHOICE",
  "contract_version": 1,
  "required": true,
  "config": {
    "prompt": "你 có nghĩa là gì?",
    "options": [
      {
        "key": "you",
        "text": "bạn"
      },
      {
        "key": "I",
        "text": "tôi"
      },
      {
        "key": "dad",
        "text": "bố"
      }
    ],
    "correct_option_keys": [
      "you"
    ],
    "shuffle": true,
    "attempts": 3,
    "hint_policy": {
      "enabled": false
    }
  },
  "condition": null
}
```

This recognition question alone cannot complete a graded SRS review. A separate due
review attempt pins every required assessment task (for example meaning recall, Pinyin
recall and STT speaking). Every required task must finalize PASS for aggregate PASS;
a valid complete set with any FAIL produces aggregate FAIL. A blocked evaluator keeps
the aggregate ungraded. Early review is practice only; scene retries keep the same
review_attempt_id and cannot produce multiple mastery changes.

## 8. Reusable listening transcription

This example can be ADDed to any of the five lesson types; template authors choose its
required flag. Canonical target 你好 (greeting audio with third-tone sandhi), accepted
text exactly 你好. A character target can instead reference `character-ni`; phrases
and sentences use reviewed sentence-bank entries with aligned audio/variants.

```json
{
  "scene_key": "scene-listen-nihao",
  "position": 70,
  "scene_type": "LISTENING_TRANSCRIPTION",
  "contract_version": 1,
  "required": false,
  "config": {
    "target_ref": {
      "kind": "VOCABULARY",
      "id": "v-nihao"
    },
    "audio_asset_id": "audio-nihao-context",
    "accepted_texts": [
      "你好"
    ],
    "pinyin_visibility": "AFTER_SUBMIT",
    "replay_policy": {
      "max_replays": 3
    },
    "hint_policy": {
      "enabled": false
    },
    "answer_mode": "FREEHAND_SELECTED_TEXT",
    "scoring_policy": {
      "type": "EXACT_ACCEPTED_TEXT",
      "normalization": "NFC_TRIM_OUTER"
    },
    "max_attempts": 3
  },
  "condition": null
}
```

Flow: hear audio -> optionally replay -> draw character -> manually select intended
Hanzi (or use future recognition candidates) -> draw/select second character -> submit
final text -> deterministic feedback -> retry within policy. Keyboard input uses the
same scene with answer_mode KEYBOARD. Inability to recognize handwriting is not itself
an incorrect transcription if the learner selects the correct intended text.

Illustrative local checkpoint, separate from published config:

```json
{
  "text_revision": 2,
  "stroke_document_local_ref": "local-private-attempt-12",
  "candidate_slots": [
    {
      "position": 0,
      "candidates": [],
      "selected_hanzi": "你"
    },
    {
      "position": 1,
      "candidates": [],
      "selected_hanzi": "好"
    }
  ],
  "final_text": "你好",
  "replays_used": 1,
  "hints_used": 0,
  "submissions": 1
}
```

Candidate lists are empty while recognition is unavailable; manual selection still
works. Future candidates may have confidence values, but that score never substitutes
for comparing final text to accepted text. Full raw points remain in the local stroke
document rather than being squeezed into this bounded checkpoint.

## 9. Conditional sentence translation

Current VOCABULARY lesson teaches 爱 (ài; yêu), with all required core scenes already
satisfied in the current run. Prior **accepted** TEACHES completions provide vocabulary
我, 爸爸, 妈妈 and grammar `grammar-svo`. None of these can be supplied by custom entries,
saved-only words or a claim of external knowledge. Set V contains their exact lexical IDs;
the run-local capability adds current `v-ai`. Prior completion of 你好 is irrelevant here.

Reviewed bank contains two different sentences, both requiring grammar-svo:

| Prompt | Canonical text | Token IDs and source offsets |
| --- | --- | --- |
| Tôi yêu bố. | 我爱爸爸 | v-wo at 0, v-ai at 1, v-baba at 2 |
| Tôi yêu mẹ. | 我爱妈妈 | v-wo at 0, v-ai at 1, v-mama at 2 |

No punctuation is present in the canonical Chinese answers; adding accepted punctuation
later requires annotation of those variants too. 爸爸 and 妈妈 each occupy two Hanzi but
one reviewed lexical token. All lexical surfaces are covered; no automatic substring
credit is used.

```json
{
  "scene_key": "scene-translate-love",
  "position": 60,
  "scene_type": "SENTENCE_TRANSLATION",
  "contract_version": 1,
  "required": true,
  "config": {
    "sentence_pool_ids": [
      "sentence-love-dad",
      "sentence-love-mom"
    ],
    "selection_count": 1,
    "answer_modes": [
      "FREEHAND_SELECTED_TEXT"
    ],
    "recording_policy": "REQUIRED_CAPTURE",
    "evaluation_policy": {
      "type": "EXACT_ACCEPTED_TEXT",
      "normalization": "NFC_TRIM_OUTER"
    },
    "speech_evaluation_policy_id": "policy-stt-content-v1"
  },
  "condition": {
    "type": "ELIGIBLE_SENTENCE_AVAILABLE",
    "schema_version": 1,
    "vocabulary_source": "COMPLETED_APP_LESSONS",
    "minimum_sentence_count": 1,
    "allow_current_target_after_core": true
  }
}
```

At start, the server pins candidate sentence IDs using provisional V union {爱};
the scene stays locked until accepted core work activates the current-target capability.
The default minimum_sentence_count=1 includes the scene if only the dad sentence is
eligible (even without 妈妈); selection_count=1 deterministically selects one available
sentence. If grammar-svo is absent, neither sentence is eligible even with hundreds of
known words and the scene is skipped. A lesson may explicitly override both availability
and selection count to 2; then lacking 妈妈 would skip that stricter scene. After Canvas
drawing/Hanzi selection and correct text submission, require a valid sentence recording
and STT content match. No detailed pronunciation/tone assessment is implied. A technical
blocker preserves progress without a failed assessment.

Skipping or selection is part of this run's resolution. Learning 妈妈 on another device
later does not reopen or replace its selected sentence; a new practice run can include translation without new
EXP or automatic SRS advancement. Only final valid lesson completion makes 爱 durable
app-learned knowledge. A generated sentence containing 的 would fail this example's
vocabulary/grammar checks unless both its lexical ID and required grammar were eligible.

## 10. Speaking evaluation policies and recovery

Shared immutable MVP speech policy (aliases resolve to UUIDs) compares Chinese content:

```json
{
  "id": "policy-stt-content-v1",
  "code": "mandarin-content-match",
  "version": 1,
  "evaluation_mode": "STT_CONTENT_MATCH",
  "locale": "zh-CN",
  "evaluator_version": "stt-adapter-contract-v1",
  "parameters": {
    "normalization": "NFC_REMOVE_REVIEWED_PUNCTUATION_TRIM_OUTER",
    "ignored_punctuation": ["。", "！", "？"],
    "accept_unlisted_homophones": false,
    "max_scored_attempts": 3
  }
}
```

For expected 你好, a successfully recognized “你好。” normalizes to an accepted text
and yields this result. It does not establish correct third-tone sandhi. Feedback and
stored evidence preserve the evaluation mode/version.

```json
{
  "assessment_attempt_id": "assessment-nihao-1",
  "input_revision": 1,
  "evaluation_policy_id": "policy-stt-content-v1",
  "evaluation_mode": "STT_CONTENT_MATCH",
  "status": "PASS",
  "recognized_text": "你好。",
  "score": null,
  "metrics": {},
  "provider": "configured-stt-provider",
  "provider_version": null,
  "error_code": null
}
```

Successfully recognized wrong text such as 你们 is content FAIL and permits retry.
A timeout is ERROR with error_code SERVICE_TIMEOUT, score NULL and no learning FAIL;
the task stays BLOCKED. Permission denial precedes evaluation: preserve WAITING_PERMISSION
and offer Vietnamese rationale plus permission retry/settings. Approved accessible
alternatives record their own completion method, never a fabricated STT result. Prior
pages and accepted task results survive technical failures. Raw recordings are ephemeral.

Future specialized policy is distinct and unusable until its capabilities are verified:

```json
{
  "id": "policy-pronunciation-assessment-v1",
  "code": "mandarin-detailed-assessment",
  "version": 1,
  "evaluation_mode": "PRONUNCIATION_ASSESSMENT",
  "locale": "zh-CN",
  "evaluator_version": "assessment-adapter-contract-v1",
  "parameters": {
    "score_metric": "verified_provider_overall_score",
    "passing_threshold": 70,
    "score_scale": 100,
    "required_metrics": ["verified_provider_overall_score"]
  }
}
```

This is a future contract fixture, not proof of a provider's metric or Mandarin tone
support. No threshold applies to STT. A valid supported score of 70 passes, 69 fails;
missing metrics/service errors stay ungraded. Aspiration/retroflex/tone metrics must be
individually verified before use. Policy changes create new versions, not history edits.

## 11. One aggregate due review across scene retries

Assume review-due-nihao-1 started server-side when due at state revision 4 and mastery 2.
The profile pins meaning, Pinyin and speaking tasks. Handwriting capture can be additional
practice; unsupported handwriting assessment is not silently passed. New recordings get
new assessment IDs under the same review_attempt_id/task_key.

```json
{
  "review_attempt_id": "review-due-nihao-1",
  "operation_id": "operation-review-start-1",
  "expected_srs_revision": 4,
  "policy_id": "srs-aggregate-v2",
  "required_tasks": [
    {
      "task_key": "meaning",
      "task_type": "MEANING_RECALL",
      "evaluation_policy_id": "policy-meaning-text-v1",
      "result": "PASS"
    },
    {
      "task_key": "pinyin",
      "task_type": "PINYIN_RECALL",
      "evaluation_policy_id": "policy-pinyin-text-v1",
      "result": "PASS"
    },
    {
      "task_key": "speaking",
      "task_type": "SPEAKING",
      "evaluation_policy_id": "policy-stt-content-v1",
      "result": "BLOCKED"
    }
  ],
  "aggregate_result": null,
  "mastery_before": 2,
  "mastery_after": 2
}
```

This is a joined projection, not JSON replacing relational task rows. A timeout consumes
no scored retry and writes no review_history. Recovery under the same review that yields
three PASS results produces aggregate PASS, mastery 3 and one history event. If any task
finalizes a valid FAIL and all tasks are otherwise complete, aggregate FAIL yields mastery 1
and a short relearning interval. Duplicate responses and extra recordings cannot grade
the review twice. History retains policy versions and timestamps through its attempt/task FKs.

## Linguistic review references

The two-third-tone distinction is supported by
[Lu, Chuang and Baayen's tone sandhi study](https://arxiv.org/abs/2408.15747).
The 不-before-fourth-tone rule is discussed in
[Wang's MIT thesis, tone sandhi discussion](https://sls.csail.mit.edu/archives/root/publications/2001/Wang_phd_thesis.pdf).
These support the pronunciation distinction, not the proposed database design or a
blanket claim that all etymologies/recordings have been reviewed. Character origins,
POS assignments, canonical spacing, media and actual curriculum HSK tags still require
editorial review before publication; the fixtures do not assert unverified HSK levels.
