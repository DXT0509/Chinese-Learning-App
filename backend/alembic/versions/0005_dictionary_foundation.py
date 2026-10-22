"""Add isolated shared dictionary lookup data; preserve all learning/session tables."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_dictionary_foundation"
down_revision = "0004_vocabulary_player"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dictionary_imports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("revision", sa.String(100), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("license", sa.String(100), nullable=False),
        sa.Column("license_url", sa.Text(), nullable=False),
        sa.Column("attribution", sa.Text(), nullable=False),
        sa.Column("changes", sa.Text(), nullable=False),
        sa.Column("entry_count", sa.Integer(), nullable=False),
        sa.Column(
            "imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("source", "revision"),
        sa.CheckConstraint("entry_count > 0", name="positive_entry_count"),
        sa.CheckConstraint("length(sha256) = 64", name="sha256_length"),
    )
    op.create_table(
        "dictionary_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column(
            "import_id",
            sa.Uuid(),
            sa.ForeignKey("dictionary_imports.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("simplified", sa.String(255, collation="C"), nullable=False),
        sa.Column("traditional", sa.String(255, collation="C"), nullable=False),
        sa.Column("pinyin_numbered", sa.String(500), nullable=False),
        sa.Column("pinyin", sa.String(500), nullable=False),
        sa.Column("english_glosses", postgresql.JSONB(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.UniqueConstraint("source", "traditional", "simplified", "pinyin_numbered"),
        sa.CheckConstraint(
            "length(simplified) > 0 AND length(traditional) > 0", name="nonempty_forms"
        ),
        sa.CheckConstraint("jsonb_array_length(english_glosses) > 0", name="nonempty_glosses"),
    )
    op.create_index("ix_dictionary_entries_simplified", "dictionary_entries", ["simplified"])
    op.create_index("ix_dictionary_entries_traditional", "dictionary_entries", ["traditional"])


def downgrade():
    raise RuntimeError("Dictionary retention requires a separately reviewed migration")
