"""Add a resume cursor and vocabulary player scene contracts; retain all runs."""

import sqlalchemy as sa

from alembic import op

revision = "0004_vocabulary_player"
down_revision = "0003_sessions_and_runs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lesson_runs", sa.Column("current_scene_key", sa.Uuid(), nullable=True))
    op.drop_constraint(
        op.f("ck_lesson_template_scenes_supported_type"), "lesson_template_scenes", type_="check"
    )
    op.create_check_constraint(
        "supported_type",
        "lesson_template_scenes",
        "scene_type IN ('VOCABULARY_INFORMATION','CHARACTER_ANALYSIS','VOCABULARY_INTRODUCTION','STROKE_ANIMATION','HANDWRITING_PRACTICE')",
    )


def downgrade():
    raise RuntimeError("Player progress retention requires a separately reviewed migration")
