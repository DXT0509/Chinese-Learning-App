"""Email credentials, revocable sessions and version-pinned preview checkpoints.

Existing users, emails and progress are intentionally untouched. Email uniqueness
belongs to the new login namespace; legacy unverified emails are not ownership.
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_sessions_and_runs"
down_revision = "0002_content_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_credentials",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("email = lower(trim(email))", name="normalized_email"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("access_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_table(
        "refresh_credentials",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("auth_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("used_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_refresh_credentials_session_id", "refresh_credentials", ["session_id"])
    op.create_table(
        "lesson_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column(
            "lesson_version_id",
            sa.Uuid(),
            sa.ForeignKey("lesson_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("user_id", "request_id"),
    )
    op.create_index("ix_lesson_runs_user_id", "lesson_runs", ["user_id"])
    op.create_table(
        "lesson_scene_progress",
        sa.Column(
            "run_id",
            sa.Uuid(),
            sa.ForeignKey("lesson_runs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("scene_key", sa.Uuid(), primary_key=True),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.CheckConstraint("page >= 0 AND page <= 10000", name="valid_page"),
    )


def downgrade():
    raise RuntimeError("Session and learning retention requires a separately reviewed migration")
