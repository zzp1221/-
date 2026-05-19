-- Mistake book schema and automatic capture from practice submissions.

CREATE TABLE IF NOT EXISTS app.mistake_record (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    practice_item_id UUID NOT NULL REFERENCES app.practice_item(id) ON DELETE CASCADE,
    last_submission_id UUID NOT NULL REFERENCES app.practice_submission(id) ON DELETE CASCADE,
    knowledge_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    difficulty_level app.difficulty_level NOT NULL DEFAULT 'MIXED',
    mistake_type VARCHAR(32) CHECK (
        mistake_type IS NULL OR mistake_type IN ('conceptual', 'procedural', 'careless')
    ),
    user_note TEXT NOT NULL DEFAULT '',
    wrong_count INT NOT NULL DEFAULT 1 CHECK (wrong_count >= 1),
    review_count INT NOT NULL DEFAULT 0 CHECK (review_count >= 0),
    next_review_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ease_factor NUMERIC(3,2) NOT NULL DEFAULT 2.50 CHECK (ease_factor >= 1.30),
    interval_days INT NOT NULL DEFAULT 1 CHECK (interval_days >= 1),
    mastered BOOLEAN NOT NULL DEFAULT FALSE,
    first_wrong_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_wrong_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, practice_item_id)
);

CREATE TABLE IF NOT EXISTS app.mistake_review_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    mistake_ids UUID[] NOT NULL DEFAULT ARRAY[]::UUID[],
    status VARCHAR(16) NOT NULL DEFAULT 'IN_PROGRESS' CHECK (status IN ('IN_PROGRESS', 'DONE', 'CANCELLED')),
    score NUMERIC(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS app.mistake_review_result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES app.mistake_review_session(id) ON DELETE CASCADE,
    mistake_record_id UUID NOT NULL REFERENCES app.mistake_record(id) ON DELETE CASCADE,
    quality INT NOT NULL CHECK (quality BETWEEN 0 AND 5),
    is_correct BOOLEAN,
    answer_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, mistake_record_id)
);

CREATE INDEX IF NOT EXISTS idx_mistake_user_next_review
    ON app.mistake_record(user_id, next_review_at)
    WHERE NOT mastered;

CREATE INDEX IF NOT EXISTS idx_mistake_user_mastered
    ON app.mistake_record(user_id, mastered, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_mistake_tags_gin
    ON app.mistake_record USING GIN (knowledge_tags);

CREATE INDEX IF NOT EXISTS idx_mistake_review_session_user
    ON app.mistake_review_session(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_mistake_review_result_session
    ON app.mistake_review_result(session_id, mistake_record_id);

ALTER TABLE app.mistake_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.mistake_review_session ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.mistake_review_result ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_mistake_record_rw ON app.mistake_record;
CREATE POLICY p_mistake_record_rw ON app.mistake_record
    FOR ALL USING (user_id = app.current_user_uuid())
    WITH CHECK (user_id = app.current_user_uuid());

DROP POLICY IF EXISTS p_mistake_review_session_rw ON app.mistake_review_session;
CREATE POLICY p_mistake_review_session_rw ON app.mistake_review_session
    FOR ALL USING (user_id = app.current_user_uuid())
    WITH CHECK (user_id = app.current_user_uuid());

DROP POLICY IF EXISTS p_mistake_review_result_rw ON app.mistake_review_result;
CREATE POLICY p_mistake_review_result_rw ON app.mistake_review_result
    FOR ALL USING (user_id = app.current_user_uuid())
    WITH CHECK (user_id = app.current_user_uuid());

DROP TRIGGER IF EXISTS trg_mistake_record_touch_updated_at ON app.mistake_record;
CREATE TRIGGER trg_mistake_record_touch_updated_at
    BEFORE UPDATE ON app.mistake_record
    FOR EACH ROW EXECUTE FUNCTION app.touch_updated_at();

CREATE OR REPLACE FUNCTION app.capture_mistake_from_submission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    item_record RECORD;
    wrong_at TIMESTAMPTZ;
BEGIN
    IF NEW.is_correct IS DISTINCT FROM FALSE THEN
        RETURN NEW;
    END IF;

    SELECT knowledge_tags, difficulty_level
    INTO item_record
    FROM app.practice_item
    WHERE id = NEW.practice_item_id;

    wrong_at := COALESCE(NEW.submitted_at, now());

    INSERT INTO app.mistake_record (
        user_id,
        practice_item_id,
        last_submission_id,
        knowledge_tags,
        difficulty_level,
        wrong_count,
        next_review_at,
        first_wrong_at,
        last_wrong_at,
        mastered
    )
    VALUES (
        NEW.user_id,
        NEW.practice_item_id,
        NEW.id,
        COALESCE(item_record.knowledge_tags, '[]'::jsonb),
        COALESCE(item_record.difficulty_level, 'MIXED'::app.difficulty_level),
        1,
        now(),
        wrong_at,
        wrong_at,
        FALSE
    )
    ON CONFLICT (user_id, practice_item_id) DO UPDATE
    SET last_submission_id = EXCLUDED.last_submission_id,
        knowledge_tags = EXCLUDED.knowledge_tags,
        difficulty_level = EXCLUDED.difficulty_level,
        wrong_count = app.mistake_record.wrong_count + 1,
        next_review_at = now(),
        last_wrong_at = EXCLUDED.last_wrong_at,
        mastered = FALSE,
        updated_at = now();

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_capture_mistake_from_submission ON app.practice_submission;
CREATE TRIGGER trg_capture_mistake_from_submission
    AFTER INSERT OR UPDATE OF is_correct, judge_result_json, submitted_at ON app.practice_submission
    FOR EACH ROW
    WHEN (NEW.is_correct IS FALSE)
    EXECUTE FUNCTION app.capture_mistake_from_submission();

INSERT INTO app.mistake_record (
    user_id,
    practice_item_id,
    last_submission_id,
    knowledge_tags,
    difficulty_level,
    wrong_count,
    next_review_at,
    first_wrong_at,
    last_wrong_at,
    mastered
)
SELECT
    s.user_id,
    s.practice_item_id,
    s.id,
    COALESCE(i.knowledge_tags, '[]'::jsonb),
    COALESCE(i.difficulty_level, 'MIXED'::app.difficulty_level),
    1,
    now(),
    COALESCE(s.submitted_at, now()),
    COALESCE(s.submitted_at, now()),
    FALSE
FROM app.practice_submission s
JOIN app.practice_item i ON i.id = s.practice_item_id
WHERE s.is_correct IS FALSE
ON CONFLICT (user_id, practice_item_id) DO UPDATE
SET last_submission_id = EXCLUDED.last_submission_id,
    knowledge_tags = EXCLUDED.knowledge_tags,
    difficulty_level = EXCLUDED.difficulty_level,
    last_wrong_at = GREATEST(app.mistake_record.last_wrong_at, EXCLUDED.last_wrong_at),
    mastered = FALSE,
    updated_at = now();
