"""Independent personal dictionary collection; no learning-state changes."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0007_personal_vocabulary"
down_revision = "0006_dictionary_enrichment"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "personal_vocabulary_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("dictionary_entry_id", sa.Uuid(), nullable=False),
        sa.Column("source_revision_at_save", sa.Text(), nullable=False),
        sa.Column("saved_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column(
            "saved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["dictionary_entry_id"], ["dictionary_entries.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("user_id", "dictionary_entry_id"),
    )
    op.create_index(
        "ix_personal_vocabulary_owner_saved",
        "personal_vocabulary_entries",
        ["user_id", "saved_at", "id"],
    )


def downgrade():
    raise RuntimeError("Personal collections require a reviewed retention plan before removal")
