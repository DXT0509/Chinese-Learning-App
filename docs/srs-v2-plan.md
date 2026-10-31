# Phase 5.0 implementation plan

Inspection baseline (30 October 2026): SrsService owns transactions; saved-row then
attempt-row locks and schedule_version prevent duplicate scheduling. Attempts pin
policy and state JSON; database triggers preserve journals. ReviewedTargets validates
the installed 2,804-policy catalog. ReviewEngine currently exposes solutions after
each stage and PINYIN questions contain Hanzi. Android keeps stage drafts and
prefetches attempts; its separate ink ViewModel has a keyboard fallback.

1. Pin upstream py-fsrs 6.3.2 after checking its installed API. Add a tested adapter,
   versioned parameters and separate memory storage. Again=FAIL, Good=PASS; retain
   the existing mastery transition's progress rules but discard its interval.
2. Add revision 0013 without updating due dates, mastery, policies or attempts.
   Existing saved words remain activated; future saves are pending. Adopt FSRS
   lazily on the next eligible completed v2 attempt, replaying only recorded,
   scheduling-applied historical outcomes. Preserve all pinned legacy attempts;
   unfinished legacy attempts become read-only and require a new v2 attempt.
3. New attempts pin exactly HANZI/PINYIN and a two-stage policy projection. Require
   bounded strokes, candidates and selected transcription per character. Validate
   geometry and membership on the server; client ink cannot prove physical origin
   against a malicious client without a trusted recognition/attestation service.
   Hide solutions until both submissions are sealed. Preserve first-answer grading.
4. Add durable daily plans, risk-first selection followed by stored random ordering,
   bounded pending intake, idempotent foreground duration accounting and recovery.
   Default 1,200 seconds; 45 seconds/word until five completed timed attempts.
5. Remove Android POS controls and graded Hanzi keyboard paths. Carry ink evidence
   through queued drafts/retries. Add lifecycle-aware, idle-bounded active timing,
   a compact budget indicator and explicit continuation beyond the target.
6. Test pure contracts, API concurrency, upgrade preservation and Android regressions.
   Generate read-only live preflight and explicitly synthetic 500/2,000/5,000-word
   simulations. Document exact writes, backup/restore and approval gate.

Deployment is disabled by default behind SRS_V2_ENABLED. No development migration,
policy installation, mastery change or graded learner attempt is authorized.
