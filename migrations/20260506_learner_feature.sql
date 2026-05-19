-- =========================================================
-- 增量迁移：学习画像多维特征表
-- 幂等执行：可重复运行，不会破坏已有数据
-- =========================================================

CREATE TABLE IF NOT EXISTS app.learner_feature (
    id                    BIGSERIAL PRIMARY KEY,
    user_id               UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    dimension             TEXT NOT NULL,
    feature_key           TEXT NOT NULL,
    canonical_key         TEXT,
    feature_value         JSONB NOT NULL DEFAULT '{}'::jsonb,
    aliases               JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence            REAL NOT NULL DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    source_type           TEXT NOT NULL DEFAULT 'CONVERSATION'
                              CHECK (source_type IN ('CONVERSATION', 'EVALUATION', 'PRACTICE', 'INFERRED', 'EXPLICIT')),
    source_ref            JSONB,
    reasoning             TEXT NOT NULL DEFAULT '',
    evidence              JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_count    INT NOT NULL DEFAULT 1,
    decay_enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    stability_period_days INT NOT NULL DEFAULT 30,
    decay_rate            REAL NOT NULL DEFAULT 0.05,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    status                TEXT NOT NULL DEFAULT 'ACTIVE'
                          CHECK (status IN ('ACTIVE', 'RESOLVED', 'REGRESSED', 'ARCHIVED')),
    resolved_at           TIMESTAMPTZ,
    resolved_reason       TEXT NOT NULL DEFAULT '',
    resolved_by           JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_observed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    inferred              BOOLEAN NOT NULL DEFAULT FALSE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, dimension, feature_key)
);

CREATE INDEX IF NOT EXISTS idx_learner_feature_user_dim
    ON app.learner_feature(user_id, dimension, is_active, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_learner_feature_confidence
    ON app.learner_feature(user_id, confidence DESC, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_learner_feature_canonical_status
    ON app.learner_feature(user_id, dimension, canonical_key, status, is_active, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_learner_feature_resolved
    ON app.learner_feature(user_id, status, resolved_at DESC);

ALTER TABLE app.learner_feature ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_learner_feature_rw ON app.learner_feature;
CREATE POLICY p_learner_feature_rw ON app.learner_feature
    FOR ALL USING (user_id = app.current_user_uuid())
    WITH CHECK (user_id = app.current_user_uuid());

DROP TRIGGER IF EXISTS trg_learner_feature_touch_updated_at ON app.learner_feature;
CREATE TRIGGER trg_learner_feature_touch_updated_at
    BEFORE UPDATE ON app.learner_feature
    FOR EACH ROW EXECUTE FUNCTION app.touch_updated_at();
