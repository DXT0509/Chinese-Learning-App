"""Additive curated catalog; no legacy data is modified."""

from alembic import op

revision = "0008_curated_vocabulary"
down_revision = "0007_personal_vocabulary"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE curated_vocabulary_batches (
        id TEXT NOT NULL,
        checksum TEXT NOT NULL,
        imported_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        CONSTRAINT pk_curated_vocabulary_batches PRIMARY KEY (id)
    )
    """)
    op.execute("""
    CREATE TABLE curated_vocabulary (
        id UUID NOT NULL,
        lexical_key TEXT NOT NULL,
        simplified TEXT NOT NULL,
        pinyin TEXT NOT NULL,
        pinyin_numbered TEXT NOT NULL,
        sino_vietnamese TEXT,
        part_of_speech TEXT,
        learning_level INTEGER NOT NULL,
        classification_standard TEXT DEFAULT 'APP_CURATED' NOT NULL,
        difficulty_reference TEXT DEFAULT 'HSK_2_0' NOT NULL,
        review_status TEXT DEFAULT 'GENERATED_UNREVIEWED' NOT NULL,
        content_version INTEGER NOT NULL,
        batch_id TEXT NOT NULL,
        checksum TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        CONSTRAINT pk_curated_vocabulary PRIMARY KEY (id),
        CONSTRAINT uq_curated_vocabulary_simplified UNIQUE (simplified, pinyin_numbered),
        CONSTRAINT ck_curated_vocabulary_level_range CHECK (learning_level BETWEEN 0 AND 5),
        CONSTRAINT ck_curated_vocabulary_positive_version CHECK (content_version > 0),
        CONSTRAINT ck_curated_vocabulary_classification CHECK (classification_standard = 'APP_CURATED'),
        CONSTRAINT ck_curated_vocabulary_difficulty CHECK (difficulty_reference = 'HSK_2_0'),
        CONSTRAINT ck_curated_vocabulary_quality CHECK (review_status IN ('GENERATED_UNREVIEWED','NEEDS_REVIEW','HUMAN_APPROVED')),
        CONSTRAINT uq_curated_vocabulary_lexical_key UNIQUE (lexical_key),
        CONSTRAINT fk_curated_vocabulary_batch_id_curated_vocabulary_batches FOREIGN KEY(batch_id) REFERENCES curated_vocabulary_batches (id)
    )
    """)
    op.execute("""
    CREATE INDEX ix_curated_vocabulary_simplified ON curated_vocabulary (simplified)
    """)
    op.execute("""
    CREATE TABLE curated_user_vocabulary (
        id UUID NOT NULL,
        user_id UUID NOT NULL,
        vocabulary_id UUID NOT NULL,
        mastery_level INTEGER DEFAULT '0' NOT NULL,
        next_review_at TIMESTAMP WITH TIME ZONE,
        last_reviewed_at TIMESTAMP WITH TIME ZONE,
        saved_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        is_active BOOLEAN DEFAULT 'true' NOT NULL,
        CONSTRAINT pk_curated_user_vocabulary PRIMARY KEY (id),
        CONSTRAINT uq_curated_user_vocabulary_user_id UNIQUE (user_id, vocabulary_id),
        CONSTRAINT ck_curated_user_vocabulary_mastery_range CHECK (mastery_level BETWEEN 0 AND 5),
        CONSTRAINT fk_curated_user_vocabulary_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
        CONSTRAINT fk_curated_user_vocabulary_vocabulary_id_curated_vocabulary FOREIGN KEY(vocabulary_id) REFERENCES curated_vocabulary (id) ON DELETE RESTRICT
    )
    """)
    op.execute("""
    CREATE INDEX ix_curated_user_vocabulary_owner_due ON curated_user_vocabulary (user_id, is_active, next_review_at)
    """)
    op.execute("""
    CREATE TABLE curated_vocabulary_revisions (
        vocabulary_id UUID NOT NULL,
        content_version INTEGER NOT NULL,
        checksum TEXT NOT NULL,
        payload JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        CONSTRAINT pk_curated_vocabulary_revisions PRIMARY KEY (vocabulary_id, content_version),
        CONSTRAINT fk_curated_vocabulary_revisions_vocabulary_id_curated_v_ccc6 FOREIGN KEY(vocabulary_id) REFERENCES curated_vocabulary (id) ON DELETE CASCADE
    )
    """)
    op.execute("""
    CREATE TABLE vocabulary_examples (
        vocabulary_id UUID NOT NULL,
        position INTEGER NOT NULL,
        simplified TEXT NOT NULL,
        pinyin TEXT NOT NULL,
        vietnamese TEXT NOT NULL,
        CONSTRAINT pk_vocabulary_examples PRIMARY KEY (vocabulary_id, position),
        CONSTRAINT fk_vocabulary_examples_vocabulary_id_curated_vocabulary FOREIGN KEY(vocabulary_id) REFERENCES curated_vocabulary (id) ON DELETE CASCADE
    )
    """)
    op.execute("""
    CREATE TABLE vocabulary_meanings (
        vocabulary_id UUID NOT NULL,
        language TEXT NOT NULL,
        position INTEGER NOT NULL,
        gloss TEXT NOT NULL,
        CONSTRAINT pk_vocabulary_meanings PRIMARY KEY (vocabulary_id, language, position),
        CONSTRAINT ck_vocabulary_meanings_language CHECK (language IN ('vi','en')),
        CONSTRAINT ck_vocabulary_meanings_usable_meaning CHECK (length(trim(gloss)) > 0 AND position >= 0),
        CONSTRAINT fk_vocabulary_meanings_vocabulary_id_curated_vocabulary FOREIGN KEY(vocabulary_id) REFERENCES curated_vocabulary (id) ON DELETE CASCADE
    )
    """)
    op.execute("""
    CREATE TABLE curated_vocabulary_reviews (
        id UUID NOT NULL,
        user_vocabulary_id UUID NOT NULL,
        submission_key UUID NOT NULL,
        content_version INTEGER NOT NULL,
        vietnamese_prompt TEXT NOT NULL,
        answer_simplified TEXT NOT NULL,
        answer_pinyin TEXT NOT NULL,
        result JSONB NOT NULL,
        submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        CONSTRAINT pk_curated_vocabulary_reviews PRIMARY KEY (id),
        CONSTRAINT uq_curated_vocabulary_reviews_user_vocabulary_id UNIQUE (user_vocabulary_id, submission_key),
        CONSTRAINT ck_curated_vocabulary_reviews_positive_content_version CHECK (content_version > 0),
        CONSTRAINT fk_curated_vocabulary_reviews_user_vocabulary_id_curate_b463 FOREIGN KEY(user_vocabulary_id) REFERENCES curated_user_vocabulary (id) ON DELETE RESTRICT
    )
    """)
    op.execute("""
    CREATE FUNCTION curated_collection_insert_guard() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              IF NEW.mastery_level <> 0 OR NOT EXISTS (
                SELECT 1 FROM curated_vocabulary v
                JOIN vocabulary_meanings m ON m.vocabulary_id=v.id AND m.language='vi'
                WHERE v.id=NEW.vocabulary_id AND v.review_status='HUMAN_APPROVED'
                  AND length(trim(m.gloss)) > 0
              ) THEN
                RAISE EXCEPTION 'new collection entries require approved Vietnamese content and mastery zero'
                  USING ERRCODE='23514';
              END IF;
              RETURN NEW;
            END $$
    """)
    op.execute("""
    CREATE TRIGGER curated_collection_insert BEFORE INSERT ON curated_user_vocabulary
            FOR EACH ROW EXECUTE FUNCTION curated_collection_insert_guard()
    """)


def downgrade():
    raise RuntimeError("Curated catalog requires a reviewed retention plan")
