"""Expand content authoring without assigning meaning to legacy learning data.

Revision ID: 0002_content_foundation
Revises: 0001_initial
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_content_foundation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("storage_key", sa.Text(), nullable=False, unique=True),
        sa.Column("media_type", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("byte_length", sa.BigInteger(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("byte_length > 0", name="positive_byte_length"),
        sa.CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="valid_sha256"),
        sa.CheckConstraint("jsonb_typeof(metadata) = 'object'", name="metadata_object"),
        sa.CheckConstraint(
            "storage_key ~ '^sha256/[0-9a-f]{64}\\.[a-z0-9]+$'", name="stable_storage_key"
        ),
        sa.CheckConstraint("length(trim(media_type)) > 0", name="nonblank_media_type"),
    )
    op.create_table(
        "lesson_templates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.CheckConstraint("length(trim(code)) > 0", name="nonblank_code"),
    )
    op.create_table(
        "lesson_template_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "template_id",
            sa.Uuid(),
            sa.ForeignKey("lesson_templates.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("template_id", "version"),
        sa.CheckConstraint("version >= 1", name="positive_version"),
        sa.CheckConstraint("status IN ('DRAFT','PUBLISHED')", name="valid_status"),
        sa.CheckConstraint(
            "(status = 'PUBLISHED') = (published_at IS NOT NULL)", name="publication_timestamp"
        ),
        sa.CheckConstraint("published_at >= created_at", name="publication_time_order"),
    )
    op.create_table(
        "lesson_template_scenes",
        sa.Column(
            "template_version_id",
            sa.Uuid(),
            sa.ForeignKey("lesson_template_versions.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column("scene_key", sa.Uuid(), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("scene_type", sa.String(40), nullable=False),
        sa.Column("contract_version", sa.Integer(), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint("template_version_id", "position"),
        sa.CheckConstraint("position >= 0", name="nonnegative_position"),
        sa.CheckConstraint("contract_version = 1", name="supported_contract"),
        sa.CheckConstraint(
            "scene_type IN ('VOCABULARY_INFORMATION','CHARACTER_ANALYSIS')", name="supported_type"
        ),
        sa.CheckConstraint("jsonb_typeof(config) = 'object'", name="config_object"),
    )
    op.create_table(
        "lesson_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "lesson_id", sa.Uuid(), sa.ForeignKey("lessons.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "template_version_id",
            sa.Uuid(),
            sa.ForeignKey("lesson_template_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("bundle_asset_id", sa.Uuid(), sa.ForeignKey("assets.id", ondelete="RESTRICT")),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("lesson_id", "version"),
        sa.UniqueConstraint("id", "lesson_id", name="uq_lesson_versions_id_lesson_id"),
        sa.CheckConstraint("version >= 1", name="positive_version"),
        sa.CheckConstraint("status IN ('DRAFT','PUBLISHED')", name="valid_status"),
        sa.CheckConstraint("length(trim(title)) > 0", name="nonblank_title"),
        sa.CheckConstraint(
            "(status = 'DRAFT' AND bundle_asset_id IS NULL AND published_at IS NULL) OR "
            "(status = 'PUBLISHED' AND bundle_asset_id IS NOT NULL AND published_at IS NOT NULL)",
            name="publication_fields",
        ),
        sa.CheckConstraint("published_at >= created_at", name="publication_time_order"),
    )
    op.create_index(
        "ix_lesson_versions_lesson_status_version",
        "lesson_versions",
        ["lesson_id", "status", "version"],
    )
    for column in ("template_version_id", "bundle_asset_id"):
        op.create_index(f"ix_lesson_versions_{column}", "lesson_versions", [column])

    op.add_column("lessons", sa.Column("code", sa.Text()))
    op.create_unique_constraint("uq_lessons_code", "lessons", ["code"])
    # NOT VALID deliberately preserves unknown legacy types without guessing a mapping.
    op.execute(
        "ALTER TABLE lessons ADD CONSTRAINT ck_lessons_valid_type CHECK "
        "(lesson_type IN ('VOCABULARY','PRONUNCIATION','GRAMMAR','TOPIC','REVIEW')) NOT VALID"
    )
    op.alter_column("characters", "stroke_count", existing_type=sa.Integer(), nullable=True)
    for table, column in (
        ("characters", "stroke_order_asset_id"),
        ("vocabulary", "audio_asset_id"),
    ):
        op.add_column(table, sa.Column(column, sa.Uuid()))
        op.create_foreign_key(
            f"fk_{table}_{column}_assets", table, "assets", [column], ["id"], ondelete="RESTRICT"
        )
        op.create_index(f"ix_{table}_{column}", table, [column])
        op.add_column(
            table, sa.Column("revision", sa.Integer(), server_default="1", nullable=False)
        )
        op.create_check_constraint(f"ck_{table}_positive_revision", table, "revision >= 1")
    op.add_column("vocabulary", sa.Column("part_of_speech", sa.Text()))

    # Retain all original association columns and rows. No provenance is inferred.
    op.add_column(
        "lesson_vocabulary",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
    )
    op.add_column("lesson_vocabulary", sa.Column("lesson_version_id", sa.Uuid()))
    op.add_column("lesson_vocabulary", sa.Column("role", sa.String(20)))
    op.drop_constraint("pk_lesson_vocabulary", "lesson_vocabulary", type_="primary")
    op.create_primary_key("pk_lesson_vocabulary", "lesson_vocabulary", ["id"])
    op.drop_constraint("uq_lesson_vocabulary_lesson_id", "lesson_vocabulary", type_="unique")
    op.create_index(
        "uq_lesson_vocabulary_legacy_target",
        "lesson_vocabulary",
        ["lesson_id", "vocabulary_id"],
        unique=True,
        postgresql_where=sa.text("lesson_version_id IS NULL"),
    )
    op.create_index(
        "uq_lesson_vocabulary_legacy_position",
        "lesson_vocabulary",
        ["lesson_id", "position"],
        unique=True,
        postgresql_where=sa.text("lesson_version_id IS NULL"),
    )
    op.create_unique_constraint(
        "uq_lesson_vocabulary_lesson_version_id",
        "lesson_vocabulary",
        ["lesson_version_id", "vocabulary_id"],
    )
    op.create_unique_constraint(
        "uq_lesson_vocabulary_version_position",
        "lesson_vocabulary",
        ["lesson_version_id", "position"],
    )
    op.create_foreign_key(
        "fk_lesson_vocabulary_lesson_version_id_lesson_versions",
        "lesson_vocabulary",
        "lesson_versions",
        ["lesson_version_id", "lesson_id"],
        ["id", "lesson_id"],
        ondelete="RESTRICT",
    )
    for column in ("lesson_id", "vocabulary_id"):
        op.create_index(f"ix_lesson_vocabulary_{column}", "lesson_vocabulary", [column])
    op.create_check_constraint(
        "ck_lesson_vocabulary_version_role",
        "lesson_vocabulary",
        "(lesson_version_id IS NULL AND role IS NULL) OR "
        "(lesson_version_id IS NOT NULL AND role IS NOT NULL "
        "AND role IN ('TEACHES','CONTEXT','REVIEWS'))",
    )

    # Guard both old and new parents: moving a child must not evade immutability.
    op.execute("""
    CREATE FUNCTION content_child_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE parent_id uuid; parent_status text;
    BEGIN
      FOR parent_id IN
        SELECT DISTINCT value FROM unnest(ARRAY[
          CASE WHEN TG_OP <> 'INSERT' THEN (to_jsonb(OLD)->>TG_ARGV[1])::uuid END,
          CASE WHEN TG_OP <> 'DELETE' THEN (to_jsonb(NEW)->>TG_ARGV[1])::uuid END
        ]) value WHERE value IS NOT NULL ORDER BY value
      LOOP
        EXECUTE format('SELECT status FROM %I WHERE id=$1 FOR UPDATE', TG_ARGV[0])
          INTO parent_status USING parent_id;
        IF parent_status = 'PUBLISHED' THEN
          RAISE EXCEPTION 'published definition is immutable' USING ERRCODE='23514';
        END IF;
      END LOOP;
      IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
      RETURN NEW;
    END $$
    """)
    for child, parent, key in (
        ("lesson_template_scenes", "lesson_template_versions", "template_version_id"),
        ("lesson_vocabulary", "lesson_versions", "lesson_version_id"),
    ):
        op.execute(
            f"CREATE TRIGGER {child}_immutable BEFORE INSERT OR UPDATE OR DELETE ON {child} "
            f"FOR EACH ROW EXECUTE FUNCTION content_child_guard('{parent}','{key}')"
        )
    op.execute("""
    CREATE FUNCTION content_definition_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP = 'INSERT' THEN
        IF NEW.status <> 'DRAFT' THEN
          RAISE EXCEPTION 'insert draft before publication' USING ERRCODE='23514';
        END IF;
        RETURN NEW;
      END IF;
      IF OLD.status = 'PUBLISHED' THEN
        RAISE EXCEPTION 'published definition is immutable' USING ERRCODE='23514';
      END IF;
      IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
      IF NEW.id <> OLD.id THEN
        RAISE EXCEPTION 'definition identity is immutable' USING ERRCODE='23514';
      END IF;
      RETURN NEW;
    END $$
    """)
    for table in ("lesson_versions", "lesson_template_versions"):
        op.execute(
            f"CREATE TRIGGER {table}_immutable BEFORE INSERT OR UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION content_definition_guard()"
        )
    op.execute("""
    CREATE FUNCTION content_asset_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      RAISE EXCEPTION 'asset metadata is immutable' USING ERRCODE='23514';
    END $$
    """)
    op.execute(
        "CREATE TRIGGER assets_immutable BEFORE UPDATE OR DELETE ON assets "
        "FOR EACH ROW EXECUTE FUNCTION content_asset_guard()"
    )
    op.execute("""
    CREATE FUNCTION content_lesson_publication_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE template_status text; target_count integer; teaches_count integer;
    BEGIN
      IF NEW.status = 'PUBLISHED' THEN
        SELECT status INTO template_status FROM lesson_template_versions
          WHERE id=NEW.template_version_id FOR UPDATE;
        SELECT count(*), count(*) FILTER (WHERE role='TEACHES')
          INTO target_count, teaches_count FROM lesson_vocabulary WHERE lesson_version_id=NEW.id;
        IF template_status IS DISTINCT FROM 'PUBLISHED' OR target_count <> 1 OR teaches_count <> 1
           OR NOT EXISTS (SELECT 1 FROM lessons WHERE id=NEW.lesson_id AND lesson_type='VOCABULARY')
        THEN
          RAISE EXCEPTION 'publication prerequisites are incomplete' USING ERRCODE='23514';
        END IF;
      END IF;
      RETURN NEW;
    END $$
    """)
    op.execute(
        "CREATE TRIGGER lesson_versions_publish BEFORE UPDATE ON lesson_versions "
        "FOR EACH ROW EXECUTE FUNCTION content_lesson_publication_guard()"
    )
    op.execute("""
    CREATE FUNCTION content_identity_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE used boolean;
    BEGIN
      IF TG_TABLE_NAME = 'lessons' THEN
        SELECT EXISTS(SELECT 1 FROM lesson_versions
          WHERE lesson_id=OLD.id AND status='PUBLISHED') INTO used;
        IF used AND (TG_OP = 'DELETE' OR NEW.id IS DISTINCT FROM OLD.id
          OR NEW.code IS DISTINCT FROM OLD.code OR NEW.lesson_type IS DISTINCT FROM OLD.lesson_type)
        THEN
          RAISE EXCEPTION 'published lesson identity is immutable' USING ERRCODE='23514';
        END IF;
      ELSE
        SELECT EXISTS(SELECT 1 FROM lesson_template_versions
          WHERE template_id=OLD.id AND status='PUBLISHED') INTO used;
        IF used AND (TG_OP = 'DELETE' OR NEW.id IS DISTINCT FROM OLD.id
          OR NEW.code IS DISTINCT FROM OLD.code)
        THEN
          RAISE EXCEPTION 'published template identity is immutable' USING ERRCODE='23514';
        END IF;
      END IF;
      IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
      RETURN NEW;
    END $$
    """)
    for table in ("lessons", "lesson_templates"):
        op.execute(
            f"CREATE TRIGGER {table}_identity BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION content_identity_guard()"
        )


def downgrade():
    raise RuntimeError("Content foundation downgrade requires a separately reviewed retention plan")
