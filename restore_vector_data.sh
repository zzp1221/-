#!/bin/sh
# Restore vectorized knowledge base data into PostgreSQL
# This script is called automatically by docker-compose on first startup,
# or can be run manually: docker exec zhixue-postgres sh /docker-entrypoint-initdb.d/restore_vector_data.sh
set -e

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-zhixue}"
DUMP_FILE="/docker-entrypoint-initdb.d/vector_data.dump"
RESTORE_SQL="/tmp/vector_restore.sql"
RESOURCE_STAGE_SQL="/tmp/resource_document_stage.sql"

cleanup() {
  rm -f "$RESTORE_SQL" "$RESOURCE_STAGE_SQL"
}

trap cleanup EXIT

echo "Checking if vector data needs to be restored..."

EXISTS=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM rag.knowledge_chunk;" 2>/dev/null || echo "0")

if [ "$EXISTS" -gt 0 ]; then
  echo "Vector data already exists ($EXISTS chunks), skipping restore."
  exit 0
fi

echo "Ensuring vector extension exists..."
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Dumping vector archive to SQL..."
pg_restore -a -f "$RESTORE_SQL" "$DUMP_FILE"

echo "Preparing placeholder learning resources for imported resource documents..."
awk '
  /COPY rag\.resource_document / {
    print "CREATE TEMP TABLE pg_temp.resource_document_stage ("
    print "  id UUID,"
    print "  resource_id UUID,"
    print "  title TEXT,"
    print "  domain TEXT,"
    print "  resource_type app.resource_type,"
    print "  difficulty_level app.difficulty_level,"
    print "  source_kind app.source_kind,"
    print "  source_ref TEXT,"
    print "  summary_text TEXT,"
    print "  transcript_text TEXT,"
    print "  access_scope app.access_scope,"
    print "  owner_user_id UUID,"
    print "  course_id UUID,"
    print "  metadata_json JSONB,"
    print "  created_at TIMESTAMPTZ,"
    print "  updated_at TIMESTAMPTZ"
    print ");"
    print "COPY pg_temp.resource_document_stage (id, resource_id, title, domain, resource_type, difficulty_level, source_kind, source_ref, summary_text, transcript_text, access_scope, owner_user_id, course_id, metadata_json, created_at, updated_at) FROM stdin;"
    flag = 1
    next
  }
  flag {
    print
    if ($0 == "\\.") {
      exit
    }
  }
' "$RESTORE_SQL" > "$RESOURCE_STAGE_SQL"

psql -U "$DB_USER" -d "$DB_NAME" <<SQL
\i $RESOURCE_STAGE_SQL
INSERT INTO app.learning_resource (
  id,
  title,
  domain,
  resource_type,
  difficulty_level,
  source_kind,
  access_scope,
  owner_user_id,
  course_id,
  summary_text,
  metadata_json,
  status,
  created_at,
  updated_at
)
SELECT
  s.resource_id,
  s.title,
  s.domain,
  s.resource_type,
  s.difficulty_level,
  s.source_kind,
  CASE
    WHEN s.access_scope = 'USER' AND u.id IS NULL THEN 'GLOBAL'::app.access_scope
    WHEN s.access_scope = 'COURSE' AND c.id IS NULL THEN 'GLOBAL'::app.access_scope
    ELSE s.access_scope
  END AS access_scope,
  CASE WHEN u.id IS NOT NULL THEN s.owner_user_id ELSE NULL END AS owner_user_id,
  CASE WHEN c.id IS NOT NULL THEN s.course_id ELSE NULL END AS course_id,
  s.summary_text,
  COALESCE(s.metadata_json, '{}'::jsonb) || jsonb_build_object(
    'sourceRef', s.source_ref,
    'transcriptText', s.transcript_text,
    'restoredFrom', 'vector_data.dump'
  ),
  'ACTIVE',
  s.created_at,
  s.updated_at
FROM pg_temp.resource_document_stage s
LEFT JOIN app.users u ON u.id = s.owner_user_id
LEFT JOIN app.courses c ON c.id = s.course_id
WHERE NOT EXISTS (
  SELECT 1
  FROM app.learning_resource lr
  WHERE lr.id = s.resource_id
);
SQL

echo "Restoring vectorized knowledge base from dump..."
pg_restore -U "$DB_USER" -d "$DB_NAME" \
  --no-owner --no-privileges --single-transaction \
  "$DUMP_FILE"

CHUNKS=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM rag.knowledge_chunk;")
RESOURCES=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT count(*) FROM rag.resource_chunk;")
echo "Vector data restore complete: $CHUNKS knowledge chunks, $RESOURCES resource chunks loaded."
