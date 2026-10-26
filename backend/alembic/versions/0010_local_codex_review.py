"""Opt-in development session evidence; production AI policy remains unchanged."""

from alembic import op

revision = "0010_local_codex_review"
down_revision = "0009_vocabulary_ai_review"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE curated_vocabulary DROP CONSTRAINT ck_curated_vocabulary_quality")
    op.execute("""ALTER TABLE curated_vocabulary ADD CONSTRAINT ck_curated_vocabulary_quality
        CHECK (review_status IN ('GENERATED_UNREVIEWED','NEEDS_REVIEW','AI_APPROVED',
                                 'HUMAN_APPROVED','REJECTED','LOCAL_CODEX_REVIEWED'))""")
    op.execute("""CREATE TABLE curated_vocabulary_local_reviews (
        id UUID NOT NULL CONSTRAINT pk_curated_vocabulary_local_reviews PRIMARY KEY,
        vocabulary_id UUID NOT NULL REFERENCES curated_vocabulary(id),
        content_version INTEGER NOT NULL,
        checksum TEXT NOT NULL,
        evidence_checksum TEXT NOT NULL,
        evidence JSONB NOT NULL,
        submitted_by TEXT NOT NULL,
        received_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
    )""")
    op.execute("""CREATE FUNCTION curated_local_review_immutable() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
          RAISE EXCEPTION 'Local session review evidence is append-only' USING ERRCODE='23514';
        END $$""")
    op.execute("""CREATE TRIGGER curated_local_review_immutable BEFORE UPDATE OR DELETE
        ON curated_vocabulary_local_reviews FOR EACH ROW
        EXECUTE FUNCTION curated_local_review_immutable()""")
    op.execute("""CREATE OR REPLACE FUNCTION curated_collection_insert_guard()
        RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
          IF NEW.mastery_level <> 0 OR NOT EXISTS (
            SELECT 1 FROM curated_vocabulary v
            JOIN vocabulary_meanings m ON m.vocabulary_id=v.id AND m.language='vi'
            WHERE v.id=NEW.vocabulary_id AND length(trim(m.gloss)) > 0 AND (
              v.review_status='HUMAN_APPROVED' OR (
                v.review_status='AI_APPROVED' AND
                current_setting('app.allow_ai_approved_vocabulary', true)='true' AND EXISTS (
                  SELECT 1 FROM curated_vocabulary_ai_reviews r
                  WHERE r.vocabulary_id=v.id AND r.content_version=v.content_version
                    AND r.checksum=v.checksum AND r.decision='AI_APPROVED'
                )
              ) OR (
                v.review_status='LOCAL_CODEX_REVIEWED' AND
                current_setting('app.allow_local_codex_reviewed_vocabulary', true)='true'
                AND EXISTS (
                  SELECT 1 FROM curated_vocabulary_local_reviews r
                  WHERE r.vocabulary_id=v.id AND r.content_version=v.content_version
                    AND r.checksum=v.checksum
                )
              )
            )
          ) THEN
            RAISE EXCEPTION 'new collection entries require approved Vietnamese content and mastery zero'
              USING ERRCODE='23514';
          END IF;
          RETURN NEW;
        END $$""")


def downgrade():
    raise RuntimeError("Local review evidence requires a reviewed retention plan")
