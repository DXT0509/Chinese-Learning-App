"""Seed FSRS memory from recorded history without changing existing schedules."""

from datetime import UTC, datetime
from importlib.metadata import version

import sqlalchemy as sa
from fsrs import Card, Rating, Scheduler
from sqlalchemy.dialects.postgresql import JSONB, insert

from alembic import op

revision = "0014_fsrs_only"
down_revision = "0013_srs_v2"
branch_labels = None
depends_on = None


def upgrade():
    if version("fsrs") != "6.3.2":
        raise RuntimeError("This reviewed memory conversion requires fsrs 6.3.2")
    connection = op.get_bind()
    memory = sa.table(
        "srs_memory",
        sa.column("user_vocabulary_id", sa.Uuid()),
        sa.column("scheduler_version", sa.Text()),
        sa.column("configuration", JSONB()),
        sa.column("card", JSONB()),
        sa.column("adopted_at", sa.DateTime(timezone=True)),
    )
    scheduler = Scheduler(desired_retention=0.9, enable_fuzzing=False)
    adopted_at = datetime.now(UTC)
    rows = connection.execute(
        sa.text("SELECT id, next_review_at FROM curated_user_vocabulary ORDER BY id")
    ).all()
    for saved_id, existing_due in rows:
        history = connection.execute(
            sa.text(
                "SELECT outcome, completed_at FROM srs_review_attempts "
                "WHERE user_vocabulary_id=:id AND scheduling_applied IS TRUE "
                "AND completed_at IS NOT NULL ORDER BY completed_at, id"
            ),
            {"id": saved_id},
        ).all()
        card = Card(card_id=saved_id.int, due=existing_due.astimezone(UTC))
        for outcome, completed_at in history:
            # No inferred ratings or timestamps. Practice did not alter memory.
            card, _ = scheduler.review_card(
                card,
                Rating.Good if outcome == "PASS" else Rating.Again,
                review_datetime=completed_at.astimezone(UTC),
            )
        # Memory adaptation does not move the learner's current due date.
        card.due = existing_due.astimezone(UTC)
        connection.execute(
            insert(memory)
            .values(
                user_vocabulary_id=saved_id,
                scheduler_version="fsrs-6.3.2/binary-v2",
                configuration=scheduler.to_dict(),
                card=card.to_dict(),
                adopted_at=adopted_at,
            )
            .on_conflict_do_nothing(index_elements=[memory.c.user_vocabulary_id])
        )


def downgrade():
    raise RuntimeError("FSRS memory and review evidence are retained; use a reviewed forward fix")
