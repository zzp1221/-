#!/bin/sh
# Restore vectorized knowledge base data into PostgreSQL
# This script is called automatically by docker-compose on first startup,
# or can be run manually: docker exec zhixue-postgres sh /docker-entrypoint-initdb.d/restore_vector_data.sh
set -e

echo "Checking if vector data needs to be restored..."

EXISTS=$(psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-zhixue}" -tAc \
  "SELECT count(*) FROM rag.knowledge_chunk;" 2>/dev/null || echo "0")

if [ "$EXISTS" -gt 0 ]; then
  echo "Vector data already exists ($EXISTS chunks), skipping restore."
  exit 0
fi

echo "Restoring vectorized knowledge base from dump..."
pg_restore -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-zhixue}" \
  --no-owner --no-privileges --single-transaction \
  /docker-entrypoint-initdb.d/vector_data.dump

CHUNKS=$(psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-zhixue}" -tAc \
  "SELECT count(*) FROM rag.knowledge_chunk;")
echo "Vector data restore complete: $CHUNKS chunks loaded."
