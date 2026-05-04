-- =========================================================
-- 增量迁移：视频生成任务 + 视频事件类型 + Provider 审计分类
-- 适用场景：数据库已初始化，不能再依赖 docker-entrypoint-initdb.d
-- 幂等执行：可重复运行
-- =========================================================

CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS rag;

DO $$
DECLARE
  existing_constraint_name text;
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'app' AND table_name = 'smart_engine_task_event'
  ) THEN
    SELECT con.conname
    INTO existing_constraint_name
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
    WHERE nsp.nspname = 'app'
      AND rel.relname = 'smart_engine_task_event'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) ILIKE '%event_type%';

    IF existing_constraint_name IS NOT NULL THEN
      EXECUTE format(
        'ALTER TABLE app.smart_engine_task_event DROP CONSTRAINT IF EXISTS %I',
        existing_constraint_name
      );
    END IF;

    ALTER TABLE app.smart_engine_task_event
      ADD CONSTRAINT ck_smart_engine_task_event_type
      CHECK (
        event_type IN (
          'progress',
          'result_chunk',
          'resource_file',
          'question_batch',
          'judge_result',
          'video_gen:start',
          'video_gen:script',
          'video_gen:speech',
          'video_gen:avatar',
          'video_gen:complete',
          'done',
          'error'
        )
      );
  END IF;
END $$;

DO $$
DECLARE
  existing_constraint_name text;
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'app' AND table_name = 'audit_log'
  ) THEN
    SELECT con.conname
    INTO existing_constraint_name
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
    WHERE nsp.nspname = 'app'
      AND rel.relname = 'audit_log'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) ILIKE '%event_category%';

    IF existing_constraint_name IS NOT NULL THEN
      EXECUTE format(
        'ALTER TABLE app.audit_log DROP CONSTRAINT IF EXISTS %I',
        existing_constraint_name
      );
    END IF;

    ALTER TABLE app.audit_log
      ADD CONSTRAINT ck_audit_log_event_category
      CHECK (
        event_category IN ('AUTH', 'TASK', 'DOWNLOAD', 'SAFETY', 'ADMIN', 'PROVIDER')
      );
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS rag.video_generation_task (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id              UUID UNIQUE REFERENCES app.smart_engine_task(id) ON DELETE CASCADE,
  resource_document_id UUID REFERENCES rag.resource_document(id) ON DELETE SET NULL,
  student_id           UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
  trace_id             TEXT UNIQUE,
  title                TEXT NOT NULL,
  topic                TEXT NOT NULL,
  script_json          JSONB NOT NULL DEFAULT '{}'::jsonb,
  script_text          TEXT NOT NULL DEFAULT '',
  status               TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN (
      'pending',
      'script_generated',
      'speech_synthesized',
      'video_rendering',
      'completed',
      'failed'
    )
  ),
  audio_path           TEXT,
  avatar_video_path    TEXT,
  animation_video_path TEXT,
  final_video_path     TEXT,
  thumbnail_path       TEXT,
  active_provider      TEXT,
  fallback_provider    TEXT,
  tts_provider         TEXT,
  avatar_provider      TEXT,
  duration_seconds     INT CHECK (duration_seconds IS NULL OR duration_seconds > 0),
  video_style          TEXT CHECK (
    video_style IS NULL OR video_style IN ('talking_head', 'animation', 'hybrid')
  ),
  generation_params    JSONB NOT NULL DEFAULT '{}'::jsonb,
  critic_score         NUMERIC(3,2) CHECK (
    critic_score IS NULL OR (critic_score >= 0 AND critic_score <= 1)
  ),
  safety_passed        BOOLEAN NOT NULL DEFAULT FALSE,
  error_message        TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_video_generation_task_status
ON rag.video_generation_task(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_video_generation_task_student
ON rag.video_generation_task(student_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_video_generation_task_provider
ON rag.video_generation_task(active_provider, tts_provider, avatar_provider);

ALTER TABLE rag.video_generation_task ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_video_generation_task_rw ON rag.video_generation_task;
CREATE POLICY p_video_generation_task_rw ON rag.video_generation_task
FOR ALL USING (student_id = app.current_user_uuid())
WITH CHECK (student_id = app.current_user_uuid());

DROP TRIGGER IF EXISTS trg_video_generation_task_touch_updated_at ON rag.video_generation_task;
CREATE TRIGGER trg_video_generation_task_touch_updated_at
BEFORE UPDATE ON rag.video_generation_task
FOR EACH ROW EXECUTE FUNCTION app.touch_updated_at();

ANALYZE rag.video_generation_task;
