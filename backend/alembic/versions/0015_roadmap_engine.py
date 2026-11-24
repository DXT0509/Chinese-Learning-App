"""Executable roadmap foundation; additive, no learner or catalog backfill."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0015_roadmap_engine"
down_revision = "0014_fsrs_only"
branch_labels = None
depends_on = None


def upgrade():
    # Additive tables; no existing rows are rewritten.
    op.add_column(
        "lesson_versions",
        sa.Column("engine_definition", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("active_version_id", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roadmaps")),
        sa.UniqueConstraint("code", name=op.f("uq_roadmaps_code")),
    )
    op.create_table(
        "roadmap_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("roadmap_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), server_default="DRAFT", nullable=False),
        sa.Column("definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bundle_asset_id", sa.Uuid(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(status = 'PUBLISHED') = (published_at IS NOT NULL)",
            name=op.f("ck_roadmap_versions_published"),
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT','PUBLISHED')", name=op.f("ck_roadmap_versions_status")
        ),
        sa.CheckConstraint("version > 0", name=op.f("ck_roadmap_versions_positive_version")),
        sa.ForeignKeyConstraint(
            ["bundle_asset_id"],
            ["assets.id"],
            name=op.f("fk_roadmap_versions_bundle_asset_id_assets"),
        ),
        sa.ForeignKeyConstraint(
            ["roadmap_id"], ["roadmaps.id"], name=op.f("fk_roadmap_versions_roadmap_id_roadmaps")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roadmap_versions")),
        sa.UniqueConstraint("roadmap_id", "version", name=op.f("uq_roadmap_versions_roadmap_id")),
    )
    op.create_index(
        op.f("ix_roadmap_versions_roadmap_id"), "roadmap_versions", ["roadmap_id"], unique=False
    )
    op.create_table(
        "roadmap_node_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("roadmap_id", sa.Uuid(), nullable=False),
        sa.Column("node_type", sa.Text(), nullable=False),
        sa.Column("vocabulary_id", sa.Uuid(), nullable=True),
        sa.CheckConstraint(
            "(node_type = 'NEW_WORD') = (vocabulary_id IS NOT NULL)",
            name=op.f("ck_roadmap_node_identities_one_word"),
        ),
        sa.CheckConstraint(
            "node_type IN ('NEW_WORD','REVIEW')", name=op.f("ck_roadmap_node_identities_type")
        ),
        sa.ForeignKeyConstraint(
            ["roadmap_id"],
            ["roadmaps.id"],
            name=op.f("fk_roadmap_node_identities_roadmap_id_roadmaps"),
        ),
        sa.ForeignKeyConstraint(
            ["vocabulary_id"],
            ["curated_vocabulary.id"],
            name=op.f("fk_roadmap_node_identities_vocabulary_id_curated_vocabulary"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roadmap_node_identities")),
    )
    op.create_table(
        "roadmap_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("roadmap_version_id", sa.Uuid(), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("lesson_version_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("position >= 0", name=op.f("ck_roadmap_nodes_position")),
        sa.ForeignKeyConstraint(
            ["lesson_version_id"],
            ["lesson_versions.id"],
            name=op.f("fk_roadmap_nodes_lesson_version_id_lesson_versions"),
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["roadmap_node_identities.id"],
            name=op.f("fk_roadmap_nodes_node_id_roadmap_node_identities"),
        ),
        sa.ForeignKeyConstraint(
            ["roadmap_version_id"],
            ["roadmap_versions.id"],
            name=op.f("fk_roadmap_nodes_roadmap_version_id_roadmap_versions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roadmap_nodes")),
        sa.UniqueConstraint("roadmap_version_id", "node_id", name="uq_roadmap_nodes_identity"),
        sa.UniqueConstraint("roadmap_version_id", "position", name="uq_roadmap_nodes_position"),
    )
    op.create_table(
        "roadmap_exp_grants",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("amount >= 0", name=op.f("ck_roadmap_exp_grants_amount")),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["roadmap_node_identities.id"],
            name=op.f("fk_roadmap_exp_grants_node_id_roadmap_node_identities"),
        ),
        sa.ForeignKeyConstraint(
            ["node_version_id"],
            ["roadmap_nodes.id"],
            name=op.f("fk_roadmap_exp_grants_node_version_id_roadmap_nodes"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_roadmap_exp_grants_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "node_id", name=op.f("pk_roadmap_exp_grants")),
    )
    op.create_table(
        "roadmap_progress",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_completed_version_id", sa.Uuid(), nullable=True),
        sa.CheckConstraint(
            "(status = 'COMPLETED') = (completed_at IS NOT NULL)",
            name=op.f("ck_roadmap_progress_completion"),
        ),
        sa.CheckConstraint(
            "status IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','SKIPPED')",
            name=op.f("ck_roadmap_progress_status"),
        ),
        sa.ForeignKeyConstraint(
            ["first_completed_version_id"],
            ["roadmap_nodes.id"],
            name=op.f("fk_roadmap_progress_first_completed_version_id_roadmap_nodes"),
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["roadmap_node_identities.id"],
            name=op.f("fk_roadmap_progress_node_id_roadmap_node_identities"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_roadmap_progress_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "node_id", name=op.f("pk_roadmap_progress")),
    )
    op.create_table(
        "roadmap_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("replay", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["node_version_id"],
            ["roadmap_nodes.id"],
            name=op.f("fk_roadmap_runs_node_version_id_roadmap_nodes"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_roadmap_runs_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roadmap_runs")),
    )
    op.create_index(op.f("ix_roadmap_runs_user_id"), "roadmap_runs", ["user_id"], unique=False)
    op.create_index(
        "uq_roadmap_runs_first",
        "roadmap_runs",
        ["user_id", "node_version_id"],
        unique=True,
        postgresql_where=sa.text("NOT replay"),
    )
    op.create_table(
        "roadmap_vocabulary",
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("vocabulary_id", sa.Uuid(), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["node_version_id"],
            ["roadmap_nodes.id"],
            name=op.f("fk_roadmap_vocabulary_node_version_id_roadmap_nodes"),
        ),
        sa.ForeignKeyConstraint(
            ["vocabulary_id", "content_version"],
            [
                "curated_vocabulary_revisions.vocabulary_id",
                "curated_vocabulary_revisions.content_version",
            ],
            name=op.f("fk_roadmap_vocabulary_vocabulary_id_curated_vocabulary_revisions"),
        ),
        sa.PrimaryKeyConstraint(
            "node_version_id", "vocabulary_id", name=op.f("pk_roadmap_vocabulary")
        ),
    )
    op.create_table(
        "roadmap_activity_receipts",
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("activity_id", sa.Uuid(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("evaluator", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["roadmap_runs.id"],
            name=op.f("fk_roadmap_activity_receipts_run_id_roadmap_runs"),
        ),
        sa.PrimaryKeyConstraint("run_id", "request_id", name=op.f("pk_roadmap_activity_receipts")),
    )

    op.create_foreign_key(
        "fk_roadmap_active_version", "roadmaps", "roadmap_versions", ["active_version_id"], ["id"]
    )
    guards()


def downgrade():
    raise RuntimeError("Roadmap history requires a reviewed retention plan")


def guards():
    op.execute("""
    CREATE FUNCTION roadmap_revision_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS (SELECT 1 FROM roadmap_vocabulary scope
        JOIN roadmap_nodes node ON node.id=scope.node_version_id
        JOIN roadmap_versions version ON version.id=node.roadmap_version_id
        WHERE scope.vocabulary_id=OLD.vocabulary_id AND scope.content_version=OLD.content_version
          AND version.status='PUBLISHED') THEN
        RAISE EXCEPTION 'published roadmap vocabulary revision is immutable' USING ERRCODE='23514';
      END IF;
      IF TG_OP='DELETE' THEN RETURN OLD; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER roadmap_vocabulary_revision_immutable BEFORE UPDATE OR DELETE
      ON curated_vocabulary_revisions FOR EACH ROW EXECUTE FUNCTION roadmap_revision_guard();
    """)
    # Preserve the original preview branch verbatim in behavior; executable content
    # is explicitly distinguished and never inherits CONTENT_PREVIEW completion.
    op.execute("""
    CREATE OR REPLACE FUNCTION content_lesson_publication_guard() RETURNS trigger
    LANGUAGE plpgsql AS $$
    DECLARE template_status text; target_count integer; teaches_count integer;
    BEGIN
      IF NEW.status = 'PUBLISHED' THEN
        SELECT status INTO template_status FROM lesson_template_versions
          WHERE id=NEW.template_version_id FOR UPDATE;
        IF NEW.engine_definition IS NOT NULL THEN
          IF template_status IS DISTINCT FROM 'PUBLISHED' OR
             jsonb_typeof(NEW.engine_definition->'lesson'->'vocabulary') IS DISTINCT FROM 'array' OR
             jsonb_array_length(NEW.engine_definition->'lesson'->'vocabulary') < 1 OR
             (NEW.engine_definition->>'node_type' = 'NEW_WORD' AND
              jsonb_array_length(NEW.engine_definition->'lesson'->'vocabulary') <> 1) OR
             NOT EXISTS (SELECT 1 FROM roadmap_nodes n
               JOIN roadmap_node_identities i ON i.id=n.node_id
               WHERE n.lesson_version_id=NEW.id AND NEW.lesson_id=i.id
                 AND i.node_type=NEW.engine_definition->>'node_type') THEN
            RAISE EXCEPTION 'invalid executable lesson publication' USING ERRCODE='23514';
          END IF;
        ELSE
          SELECT count(*), count(*) FILTER (WHERE role='TEACHES')
            INTO target_count, teaches_count FROM lesson_vocabulary WHERE lesson_version_id=NEW.id;
          IF template_status IS DISTINCT FROM 'PUBLISHED' OR target_count <> 1 OR teaches_count <> 1
             OR NOT EXISTS (SELECT 1 FROM lessons WHERE id=NEW.lesson_id AND lesson_type='VOCABULARY')
          THEN
            RAISE EXCEPTION 'publication prerequisites are incomplete' USING ERRCODE='23514';
          END IF;
        END IF;
      END IF;
      RETURN NEW;
    END $$
    """)
    op.execute("""CREATE TRIGGER roadmap_versions_immutable
      BEFORE INSERT OR UPDATE OR DELETE ON roadmap_versions
      FOR EACH ROW EXECUTE FUNCTION content_definition_guard()""")
    op.execute("""CREATE TRIGGER roadmap_nodes_immutable
      BEFORE INSERT OR UPDATE OR DELETE ON roadmap_nodes
      FOR EACH ROW EXECUTE FUNCTION content_child_guard('roadmap_versions','roadmap_version_id')""")
    op.execute("""
    CREATE FUNCTION roadmap_scope_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE item uuid; parent uuid; state text;
    BEGIN
      FOR item IN SELECT DISTINCT x FROM unnest(ARRAY[
        CASE WHEN TG_OP <> 'INSERT' THEN OLD.node_version_id END,
        CASE WHEN TG_OP <> 'DELETE' THEN NEW.node_version_id END]) x WHERE x IS NOT NULL
      LOOP
        SELECT roadmap_version_id INTO parent FROM roadmap_nodes WHERE id=item;
        SELECT status INTO state FROM roadmap_versions WHERE id=parent FOR UPDATE;
        IF state='PUBLISHED' THEN
          RAISE EXCEPTION 'published scope is immutable' USING ERRCODE='23514';
        END IF;
      END LOOP;
      IF TG_OP='DELETE' THEN RETURN OLD; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER roadmap_vocabulary_immutable BEFORE INSERT OR UPDATE OR DELETE
      ON roadmap_vocabulary FOR EACH ROW EXECUTE FUNCTION roadmap_scope_guard();
    """)
    for table in ("roadmap_node_identities", "roadmap_exp_grants", "roadmap_activity_receipts"):
        op.execute(
            f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION content_asset_guard()"
        )
    op.execute("""
    CREATE FUNCTION roadmap_publication_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE total integer;
    BEGIN
      IF NEW.status='PUBLISHED' THEN
        SELECT count(*) INTO total FROM roadmap_nodes WHERE roadmap_version_id=NEW.id;
        IF NEW.bundle_asset_id IS NULL OR total=0 OR
           total <> jsonb_array_length(NEW.definition->'nodes') OR
           EXISTS (SELECT 1 FROM roadmap_nodes n
             JOIN roadmap_node_identities i ON i.id=n.node_id
             JOIN lesson_versions l ON l.id=n.lesson_version_id
             WHERE n.roadmap_version_id=NEW.id AND
               (i.roadmap_id <> NEW.roadmap_id OR l.status <> 'PUBLISHED' OR
                l.engine_definition IS DISTINCT FROM (NEW.definition->'nodes'->n.position)))
        THEN
          RAISE EXCEPTION 'roadmap publication incomplete' USING ERRCODE='23514';
        END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER roadmap_versions_publish BEFORE UPDATE ON roadmap_versions
      FOR EACH ROW EXECUTE FUNCTION roadmap_publication_guard();
    CREATE FUNCTION roadmap_activation_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' AND (NEW.id <> OLD.id OR NEW.code <> OLD.code) THEN
        RAISE EXCEPTION 'stable roadmap identity is immutable' USING ERRCODE='23514';
      END IF;
      IF NEW.active_version_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM roadmap_versions WHERE id=NEW.active_version_id
          AND roadmap_id=NEW.id AND status='PUBLISHED') THEN
        RAISE EXCEPTION 'invalid active roadmap' USING ERRCODE='23514';
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER roadmaps_activation BEFORE INSERT OR UPDATE ON roadmaps
      FOR EACH ROW EXECUTE FUNCTION roadmap_activation_guard();
    CREATE FUNCTION roadmap_completion_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF OLD.status='COMPLETED' AND (NEW.status <> OLD.status OR
        NEW.completed_at IS DISTINCT FROM OLD.completed_at OR
        NEW.first_completed_version_id IS DISTINCT FROM OLD.first_completed_version_id) THEN
        RAISE EXCEPTION 'first completion is durable' USING ERRCODE='23514';
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER roadmap_progress_completion BEFORE UPDATE ON roadmap_progress
      FOR EACH ROW EXECUTE FUNCTION roadmap_completion_guard();
    """)
