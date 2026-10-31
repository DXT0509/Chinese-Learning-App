"""Add FSRS memory and daily plans; preserve all schedules and historical evidence."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0013_srs_v2"
down_revision = "0012_srs_review_engine"
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL constant default preserves existing saves as activated without
    # rewriting their due dates. Future saves wait for bounded planner admission.
    op.add_column(
        "curated_user_vocabulary",
        sa.Column("learning_activated", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.alter_column("curated_user_vocabulary", "learning_activated", server_default="false")
    op.create_table(
        "srs_memory",
        sa.Column(
            "user_vocabulary_id",
            sa.Uuid(),
            sa.ForeignKey("curated_user_vocabulary.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column("scheduler_version", sa.Text(), nullable=False),
        sa.Column("configuration", JSONB(), nullable=False),
        sa.Column("card", JSONB(), nullable=False),
        sa.Column("adopted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "srs_daily_plans",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("local_day", sa.Date(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column("target_seconds", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("items", JSONB(), nullable=False),
        sa.Column("new_items", JSONB(), nullable=False, server_default="[]"),
        sa.Column("completed", JSONB(), nullable=False, server_default="[]"),
        sa.Column("deferred", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("target_seconds > 0", name=op.f("ck_srs_daily_plans_target_seconds")),
    )
    op.create_index("ix_srs_daily_plans_owner_day", "srs_daily_plans", ["user_id", "local_day"])
    op.create_table(
        "srs_active_time",
        sa.Column(
            "attempt_id",
            sa.Uuid(),
            sa.ForeignKey("srs_review_attempts.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column(
            "plan_id",
            sa.Uuid(),
            sa.ForeignKey("srs_daily_plans.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("active_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("daily_ms", JSONB(), nullable=False, server_default="{}"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("active_ms >= 0", name=op.f("ck_srs_active_time_active_ms")),
    )


def downgrade():
    raise RuntimeError(
        "Retain FSRS evidence. Roll back application by disabling v2; do not drop history."
    )
