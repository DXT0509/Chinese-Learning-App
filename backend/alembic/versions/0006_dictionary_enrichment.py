"""Add separate character enrichment and revision-correction audit metadata."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_dictionary_enrichment"
down_revision = "0005_dictionary_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "dictionary_imports", sa.Column("revision_correction", postgresql.JSONB(), nullable=True)
    )
    op.create_table(
        "dictionary_enrichment_imports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("revision", sa.String(100), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("license", sa.String(100), nullable=False),
        sa.Column("license_url", sa.Text(), nullable=False),
        sa.Column("attribution", sa.Text(), nullable=False),
        sa.Column("changes", sa.Text(), nullable=False),
        sa.Column("review_status", sa.String(100), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column(
            "imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("source", "revision"),
        sa.CheckConstraint("record_count > 0", name="positive_record_count"),
        sa.CheckConstraint("length(sha256) = 64", name="sha256_length"),
    )
    op.create_table(
        "dictionary_character_enrichments",
        sa.Column("source", sa.String(50), primary_key=True),
        sa.Column("hanzi", sa.String(1, collation="C"), primary_key=True),
        sa.Column("traditional", sa.String(1, collation="C"), nullable=True),
        sa.Column("pinyin", sa.String(100), nullable=False),
        sa.Column("sino_vietnamese", sa.String(200), nullable=False),
        sa.Column("vietnamese_gloss", sa.Text(), nullable=False),
        sa.Column(
            "import_id",
            sa.Uuid(),
            sa.ForeignKey("dictionary_enrichment_imports.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.CheckConstraint("length(hanzi) = 1", name="single_hanzi"),
        sa.CheckConstraint(
            "traditional IS NULL OR length(traditional) = 1", name="single_traditional"
        ),
        sa.CheckConstraint(
            "length(pinyin) > 0 AND length(sino_vietnamese) > 0 AND length(vietnamese_gloss) > 0",
            name="nonempty_content",
        ),
    )
    op.create_index(
        "ix_dictionary_character_enrichments_traditional",
        "dictionary_character_enrichments",
        ["traditional"],
    )


def downgrade():
    raise RuntimeError("Enrichment and correction history require a separately reviewed migration")
