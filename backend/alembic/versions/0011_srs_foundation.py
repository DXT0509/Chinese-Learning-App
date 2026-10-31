"""Add ChineseLearning SRS v1 without replacing saved-word identities or history."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0011_srs_foundation"
down_revision = "0010_local_codex_review"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "curated_user_vocabulary",
        sa.Column("phase", sa.Text(), nullable=False, server_default="LEARNING"),
    )
    for name in (
        "phase_step",
        "level_progress",
        "schedule_version",
        "due_review_count",
        "practice_count",
        "failure_count",
    ):
        op.add_column(
            "curated_user_vocabulary",
            sa.Column(name, sa.Integer(), nullable=False, server_default="0"),
        )
    op.add_column("curated_user_vocabulary", sa.Column("legacy_srs_snapshot", JSONB()))
    op.execute("""UPDATE curated_user_vocabulary SET
        legacy_srs_snapshot = jsonb_build_object('mastery_level', mastery_level,
            'next_review_at', next_review_at, 'last_reviewed_at', last_reviewed_at),
        phase = CASE WHEN mastery_level = 0 THEN 'LEARNING' ELSE 'REVIEW' END,
        next_review_at = COALESCE(next_review_at, saved_at)""")
    op.alter_column(
        "curated_user_vocabulary", "next_review_at", nullable=False, server_default=sa.func.now()
    )
    op.create_check_constraint(
        "srs_state",
        "curated_user_vocabulary",
        "(phase = 'LEARNING' AND mastery_level = 0 AND phase_step BETWEEN 0 AND 2 "
        "AND level_progress = 0) OR "
        "(phase = 'REVIEW' AND mastery_level BETWEEN 1 AND 5 AND phase_step = 0 "
        "AND level_progress BETWEEN 0 AND 1 AND (mastery_level < 5 OR level_progress = 0)) OR "
        "(phase = 'RELEARNING' AND mastery_level BETWEEN 1 AND 4 "
        "AND phase_step BETWEEN 0 AND 1 AND level_progress = 0)",
    )
    op.create_check_constraint(
        "srs_counters",
        "curated_user_vocabulary",
        "schedule_version >= 0 AND due_review_count >= 0 AND practice_count >= 0 "
        "AND failure_count BETWEEN 0 AND due_review_count",
    )
    op.create_table(
        "srs_review_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_vocabulary_id",
            sa.Uuid(),
            sa.ForeignKey("curated_user_vocabulary.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("schedule_version", sa.Integer(), nullable=False),
        sa.Column("target", JSONB(), nullable=False),
        sa.Column("state_before", JSONB(), nullable=False),
        sa.Column("state_after", JSONB()),
        sa.Column("evidence", JSONB()),
        sa.Column("outcome", sa.Text()),
        sa.Column("scheduling_applied", sa.Boolean()),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("mode IN ('DUE','PRACTICE')", name="mode"),
        sa.CheckConstraint("schedule_version >= 0", name="schedule_version"),
        sa.CheckConstraint(
            "(completed_at IS NULL AND outcome IS NULL AND evidence IS NULL "
            "AND state_after IS NULL AND scheduling_applied IS NULL) OR "
            "(completed_at IS NOT NULL AND outcome IS NOT NULL AND outcome IN ('PASS','FAIL') "
            "AND evidence IS NOT NULL AND state_after IS NOT NULL "
            "AND scheduling_applied IS NOT NULL AND completed_at >= started_at)",
            name="completion",
        ),
    )
    op.create_index(
        "ix_srs_review_attempts_progress_started",
        "srs_review_attempts",
        ["user_vocabulary_id", "started_at"],
    )
    op.execute("""CREATE FUNCTION srs_attempt_history_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          IF TG_OP = 'DELETE' THEN
            RAISE EXCEPTION 'SRS history is retained' USING ERRCODE='23514';
          END IF;
          IF OLD.completed_at IS NOT NULL OR
             (NEW.id, NEW.user_vocabulary_id, NEW.mode, NEW.schedule_version,
              NEW.target, NEW.state_before, NEW.started_at) IS DISTINCT FROM
             (OLD.id, OLD.user_vocabulary_id, OLD.mode, OLD.schedule_version,
              OLD.target, OLD.state_before, OLD.started_at) THEN
            RAISE EXCEPTION 'SRS attempt evidence is immutable' USING ERRCODE='23514';
          END IF;
          RETURN NEW;
        END $$""")
    op.execute("""CREATE TRIGGER srs_attempt_history_guard BEFORE UPDATE OR DELETE
        ON srs_review_attempts FOR EACH ROW EXECUTE FUNCTION srs_attempt_history_guard()""")


def downgrade():
    raise RuntimeError("SRS history requires a separately reviewed retention plan")
