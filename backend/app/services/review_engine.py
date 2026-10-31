"""Ordered persisted submissions; the existing SRS service alone changes progress."""

from datetime import timedelta

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from app.models.curated_vocabulary import CuratedUserVocabulary as Saved
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.srs import SrsReviewAttempt as Attempt
from app.services.review_grading import grade, pinyin_mismatches
from app.services.srs import SrsService
from app.services.srs_contract import Stage, StageEvidence, StageVerdict, ValidatedReview
from app.services.srs_state import utc

TTL = timedelta(minutes=30)
EVALUATOR = "two-stage-v2"


def answered(attempt):
    return {entry["stage"] for entry in attempt.submissions if entry["action"] == "ANSWER"}


def current_stage(attempt):
    return next(
        (s for s in attempt.target["applicable_stages"] if s not in answered(attempt)), None
    )


def solution(target, stage):
    return target[
        {
            "HANZI": "accepted_simplified",
            "PINYIN": "accepted_pinyin_numbered",
            "POS": "accepted_pos",
        }[stage]
    ]


def feedback(attempt, stage):
    entries = [e for e in attempt.submissions if e["stage"] == stage]
    first = next((e for e in entries if e["action"] == "ANSWER"), None)
    if not first and not entries:
        return None
    result = {
        "stage": stage,
        "first_correct": first["correct"] if first else None,
        "assisted": any(e["action"] != "ANSWER" for e in entries),
    }
    # Keys are educational feedback only after the actual first answer is sealed.
    if first and (
        attempt.target.get("review_version") != "two-stage-v2" or current_stage(attempt) is None
    ):
        result["correct_answer"] = solution(attempt.target, stage)
        if stage == "PINYIN" and not first["correct"] and len(result["correct_answer"]) == 1:
            result.update(pinyin_mismatches(first["answer"], result["correct_answer"][0]))
    return result


def evaluate(attempt):
    if attempt.target.get("review_version") != "two-stage-v2" or attempt.target[
        "applicable_stages"
    ] != ["HANZI", "PINYIN"]:
        raise HTTPException(409, "Historical attempts are read-only")
    if current_stage(attempt) is not None:
        raise HTTPException(409, "Complete all applicable stages before finalizing")
    stages = []
    for stage in attempt.target["applicable_stages"]:
        entries = [e for e in attempt.submissions if e["stage"] == stage]
        first = next(e for e in entries if e["action"] == "ANSWER")
        stages.append(
            StageEvidence(
                Stage(stage),
                StageVerdict.CORRECT if first["correct"] else StageVerdict.INCORRECT,
                hints_used=any(e["action"] == "HINT" for e in entries),
                answer_revealed=any(e["action"] == "REVEAL" for e in entries),
            )
        )
    return ValidatedReview(
        attempt.id,
        EVALUATOR,
        tuple(stages),
    )


class ReviewEngine(SrsService):
    async def targets_report(self, owner, limit, offset):
        rows = (
            await self.session.execute(
                select(Saved, Word)
                .join(Word)
                .where(Saved.user_id == owner, Saved.is_active)
                .order_by(Saved.id)
                .offset(offset)
                .limit(limit)
            )
        ).all()
        from app.services.curated_catalog import visible
        from app.services.review_targets import editorial_flags

        # Share the requested page's identities so validation generates this batch once.
        # Collision checks still see every catalog row, including unpublished peers.
        self.session.info["review_policy_batch"] = (
            self.session.sync_session.get_transaction(),
            {word.id for _, word in rows},
        )
        flags = await editorial_flags(self.session, [word for _, word in rows])
        items, excluded = [], []
        for saved, word in rows:
            available = await self.session.scalar(select(visible()).where(Word.id == word.id))
            target = await self.targets.resolve(self.session, word)
            if available and target.gradeable:
                items.append(
                    {"saved_id": saved.id, "due": saved.next_review_at <= utc(self.clock())}
                )
            else:
                excluded.append(
                    {
                        "saved_id": saved.id,
                        "editorial_flags": flags[word.id],
                        "reason": "REVIEWED_POLICY_REQUIRED"
                        if available
                        else "VOCABULARY_UNAVAILABLE",
                    }
                )
        return {"items": items, "excluded": excluded, "offset": offset, "limit": limit}

    async def _locked(self, owner, attempt_id):
        # Match the scheduler's lock order for same- and cross-attempt concurrency.
        saved = await self.session.scalar(
            select(Saved)
            .join(Attempt)
            .where(Attempt.id == attempt_id, Saved.user_id == owner)
            .with_for_update(of=Saved)
        )
        if saved is None:
            raise HTTPException(404, "Review attempt not found")
        attempt = await self.session.scalar(
            select(Attempt).where(Attempt.id == attempt_id).with_for_update()
        )
        return attempt

    def _active(self, attempt):
        if attempt.target.get("review_version") != "two-stage-v2":
            raise HTTPException(409, "Legacy attempt is read-only; start a new review")
        if not attempt.target["gradeable"]:
            raise HTTPException(409, "Reviewed grading policy required")
        if utc(self.clock()) >= attempt.started_at + TTL:
            raise HTTPException(410, "Review expired; start a new session")

    def _view(self, attempt):
        stage = current_stage(attempt)
        result = {
            "review_version": attempt.target.get("review_version", "three-stage-v1"),
            "attempt_id": attempt.id,
            "stage": stage,
            "expires_at": utc(attempt.started_at) + TTL,
            "status": "COMPLETED"
            if attempt.completed_at
            else "READY_TO_FINALIZE"
            if stage is None
            else "IN_PROGRESS",
            "disabled_stages": dict(attempt.target["disabled_stages"]),
            "skipped_stages": [
                {"stage": stage, "status": "NOT_APPLICABLE", "reason": reason}
                for stage, reason in attempt.target["disabled_stages"]
            ],
            "feedback": [
                f
                for s in attempt.target["applicable_stages"]
                if (f := feedback(attempt, s)) is not None
            ],
        }
        if attempt.target.get("review_version") != "two-stage-v2":
            # Historical reading retains the journal and feedback, with no active questions.
            result["stage"] = None
            result["draft_questions"] = {}
            return result
        questions = {
            "HANZI": {
                "prompt_vi": attempt.target["vietnamese_prompt"],
                "input_mode": "TEXT",
                "character_count": len(attempt.target["accepted_simplified"][0]),
            },
            "PINYIN": {"prompt_vi": attempt.target["vietnamese_prompt"], "input_mode": "TEXT"},
        }
        result["question"] = questions.get(stage)
        result["draft_questions"] = questions
        return result

    async def question(self, owner, attempt_id):
        async with self.session.begin():
            attempt = await self._locked(owner, attempt_id)
            if (
                attempt.completed_at is None
                and attempt.target.get("review_version") == "two-stage-v2"
            ):
                self._active(attempt)
            return self._view(attempt)

    async def submit(self, owner, attempt_id, body):
        async with self.session.begin():
            attempt = await self._locked(owner, attempt_id)
            request = body.model_dump(mode="json")
            previous = next(
                (
                    e
                    for e in attempt.submissions
                    if e["submission_key"] == request["submission_key"]
                ),
                None,
            )
            if previous:
                if any(previous.get(k) != v for k, v in request.items()):
                    raise HTTPException(409, "Submission key already used")
                return previous["response"]
            if attempt.completed_at:
                raise HTTPException(409, "Review already completed")
            self._active(attempt)
            if len(attempt.submissions) >= 128:
                raise HTTPException(429, "Review submission limit reached; start a new session")
            stage = body.stage.value
            if stage not in ("HANZI", "PINYIN"):
                raise HTTPException(409, "Stage is not part of this review")
            if body.action == "REVEAL" and current_stage(attempt) is not None:
                raise HTTPException(409, "Complete both stages before viewing solutions")
            if body.action == "ANSWER" and stage == "HANZI":
                ink = body.handwriting
                if ink is None or len(ink.characters) != len(
                    attempt.target["accepted_simplified"][0]
                ):
                    raise HTTPException(422, "Handwriting is required for every character slot")
                if "".join(c.selected for c in ink.characters) != body.answer:
                    raise HTTPException(422, "Answer must match selected ink transcriptions")
            if body.action == "REVEAL" and stage not in answered(attempt):
                raise HTTPException(409, "Submit an answer before requesting its solution")
            # Retrying an answered stage is practice; first correctness stays fixed.
            if stage != current_stage(attempt) and stage not in answered(attempt):
                raise HTTPException(409, "Submit the current stage")
            correct = grade(stage, body.answer, attempt.target) if body.action == "ANSWER" else None
            entry = {**request, "correct": correct, "at": utc(self.clock()).isoformat()}
            attempt.submissions = [*attempt.submissions, entry]
            result = self._view(attempt)
            result["submission_correct"] = correct
            if body.action == "HINT":
                result["hint_vi"] = "Hãy kiểm tra kỹ chữ và thanh điệu."
            result = jsonable_encoder(result)
            entry["response"] = result
            # Reassign to ensure JSONB sees the complete immutable response snapshot.
            attempt.submissions = [*attempt.submissions[:-1], entry]
            await self.session.flush()
            return result

    async def finalize(self, owner, attempt_id):
        async with self.session.begin():
            attempt = await self._locked(owner, attempt_id)
            if attempt.completed_at is None:
                self._active(attempt)
                review = evaluate(attempt)
                await self._complete_in_transaction(owner, review)
            return {
                "attempt_id": attempt.id,
                "outcome": attempt.outcome,
                "scheduling_applied": attempt.scheduling_applied,
                "mode": attempt.mode,
                "state_after": attempt.state_after,
                "previous_mastery_level": attempt.state_before["mastery_level"],
                "resulting_mastery_level": attempt.state_after["mastery_level"],
                "completed_at": utc(attempt.completed_at),
                "feedback": self._view(attempt)["feedback"],
            }
