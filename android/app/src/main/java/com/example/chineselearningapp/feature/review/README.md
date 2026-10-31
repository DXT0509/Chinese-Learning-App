# Review

FSRS 6.3.2 owns all scheduling. Reviews require per-character ML Kit handwriting
and tone-correct Pinyin; POS is dictionary metadata only. Durable daily plans select
by forgetting risk, then randomize order within the 20-minute budget. Draft recovery,
prefetch and summaries remain. See the current `docs/srs-v2.md` and deployment report.
See [Android integration and verification](../../../../../../../../../../docs/android-srs-review.md).

`ReviewViewModel` owns operations and immutable state. `ReviewScreen` renders that state
and forwards actions. `RemoteReviewRepository` maps Retrofit DTOs to framework-free domain
models and delegates authentication to the existing session repository.
