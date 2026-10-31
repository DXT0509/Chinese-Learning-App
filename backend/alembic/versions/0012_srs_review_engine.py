"""Persist ordered answers and reviewed grading policies without changing scheduling."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0012_srs_review_engine"
down_revision = "0011_srs_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "srs_review_attempts",
        sa.Column("submissions", JSONB(), nullable=False, server_default="[]"),
    )
    op.create_table(
        "srs_target_policies",
        sa.Column(
            "vocabulary_id", sa.Uuid(), sa.ForeignKey("curated_vocabulary.id"), primary_key=True
        ),
        sa.Column("content_version", sa.Integer(), primary_key=True),
        sa.Column("checksum", sa.Text(), primary_key=True),
        sa.Column("policy", JSONB(), nullable=False),
    )
    # A second guard preserves the ordered journal even before finalization.
    # Existing 0011 history and pinned-target protection remain in force.
    op.execute("""CREATE FUNCTION srs_submission_guard() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        IF jsonb_typeof(NEW.submissions) <> 'array' OR
           jsonb_array_length(NEW.submissions) < jsonb_array_length(OLD.submissions) OR
           EXISTS (SELECT 1 FROM jsonb_array_elements(OLD.submissions) WITH ORDINALITY AS e(v,n)
                   WHERE NEW.submissions->(n::int-1) IS DISTINCT FROM v) THEN
          RAISE EXCEPTION 'SRS submissions are append only' USING ERRCODE='23514';
        END IF;
        RETURN NEW;
      END $$""")
    op.execute("""CREATE TRIGGER srs_submission_guard BEFORE UPDATE ON srs_review_attempts
        FOR EACH ROW EXECUTE FUNCTION srs_submission_guard()""")


def downgrade():
    raise RuntimeError("SRS evidence requires a separately reviewed retention plan")
