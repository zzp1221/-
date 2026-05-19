-- Memory lifecycle fields for app.learner_feature.
-- Idempotent hot migration: safe to run against an existing database.

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS canonical_key TEXT;

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS aliases JSONB NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'ACTIVE';

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS resolved_reason TEXT NOT NULL DEFAULT '';

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS resolved_by JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE app.learner_feature
    ADD COLUMN IF NOT EXISTS last_observed_at TIMESTAMPTZ NOT NULL DEFAULT now();

UPDATE app.learner_feature
SET canonical_key = feature_key
WHERE canonical_key IS NULL OR btrim(canonical_key) = '';

UPDATE app.learner_feature
SET canonical_key = CASE
    WHEN feature_key IN (U&'\6B7B\9501', 'deadlock', 'dead lock')
        OR feature_key ILIKE '%' || U&'\4E24\4E2A\9501\4E92\76F8\7B49' || '%'
        OR feature_key ILIKE '%' || U&'\4E24\628A\9501\4E92\76F8\7B49' || '%'
        THEN 'deadlock'
    WHEN feature_key IN (U&'\5FAA\73AF\7B49\5F85', U&'\73AF\8DEF\7B49\5F85')
        THEN 'deadlock.circular_wait'
    WHEN feature_key IN (U&'\4E92\65A5\6761\4EF6', U&'\4E92\65A5')
        THEN 'deadlock.mutual_exclusion'
    WHEN feature_key IN (U&'\5360\6709\5E76\7B49\5F85', U&'\6301\6709\5E76\7B49\5F85')
        THEN 'deadlock.hold_and_wait'
    WHEN feature_key IN (U&'\4E0D\53EF\62A2\5360', U&'\4E0D\80FD\62A2\5360')
        THEN 'deadlock.no_preemption'
    ELSE canonical_key
END
WHERE dimension IN ('weak_points', 'skill_mastery', 'error_patterns')
  AND feature_key IS NOT NULL;

UPDATE app.learner_feature
SET aliases = to_jsonb(ARRAY[feature_key])
WHERE aliases = '[]'::jsonb AND feature_key IS NOT NULL AND btrim(feature_key) <> '';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'learner_feature_status_check'
          AND conrelid = 'app.learner_feature'::regclass
    ) THEN
        ALTER TABLE app.learner_feature
            ADD CONSTRAINT learner_feature_status_check
            CHECK (status IN ('ACTIVE', 'RESOLVED', 'REGRESSED', 'ARCHIVED'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_learner_feature_canonical_status
    ON app.learner_feature(user_id, dimension, canonical_key, status, is_active, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_learner_feature_resolved
    ON app.learner_feature(user_id, status, resolved_at DESC);
