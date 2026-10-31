"""Version-pinned upstream FSRS boundary. No persistence or mastery calculations."""

from datetime import datetime

from fsrs import Card, Rating, Scheduler

from app.services.srs_state import Outcome, utc

VERSION = "fsrs-6.3.2/binary-v2"


def configuration(retention: float = 0.90) -> dict:
    if not 0 < retention < 1:
        raise ValueError("Retention must be between zero and one")
    return Scheduler(desired_retention=retention, enable_fuzzing=False).to_dict()


def scheduler(config: dict | None = None) -> Scheduler:
    return Scheduler.from_dict(config or configuration())


def rating(outcome: Outcome) -> Rating:
    return {Outcome.FAIL: Rating.Again, Outcome.PASS: Rating.Good}[Outcome(outcome)]


def review(card: dict | None, outcome: Outcome, now: datetime, config: dict) -> tuple[dict, dict]:
    now = utc(now)
    memory = Card.from_dict(card) if card else Card(card_id=0, due=now)
    if memory.last_review is not None and now < memory.last_review:
        raise ValueError("Review precedes recorded history")
    updated, log = scheduler(config).review_card(memory, rating(outcome), review_datetime=now)
    return updated.to_dict(), log.to_dict()


def replay(history, config: dict) -> dict | None:
    """Only actual scheduling-applied outcomes, deterministically ordered by caller."""
    card = None
    for outcome, completed_at in history:
        card, _ = review(card, Outcome(outcome), completed_at, config)
    return card


def retrievability(card: dict | None, now: datetime, config: dict | None = None) -> float:
    if card is None:
        return 0.0
    return scheduler(config).get_card_retrievability(Card.from_dict(card), utc(now))
