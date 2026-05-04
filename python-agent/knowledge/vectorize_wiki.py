"""
Vectorize wiki pages using DashScope qwen3-vl-embedding API.
Generates 1024-dim embeddings and writes to rag.knowledge_document + rag.knowledge_chunk.
Usage: python vectorize_wiki.py [--dry-run] [--limit N]
"""
import sys
import os
import uuid
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


# 鈹€鈹€ Config 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()

DIMENSION = RUNTIME_CONFIG.embedding_dimension
BATCH_SIZE = 5  # texts per API call
API_DELAY = 0.3  # seconds between batches


# 鈹€鈹€ DB 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def connect():
    return psycopg2.connect(**DB_CONFIG)


def fetch_wiki_pages(cur, limit: int = None) -> list[dict]:
    """Fetch wiki pages that haven't been vectorized yet."""
    sql = """
        SELECT w.id, w.slug, w.title, w.markdown_content, w.difficulty_level::text,
               w.tags, w.source_refs, w.frontmatter_json, w.summary_text
        FROM rag.wiki_page w
        WHERE w.is_active = true
        AND NOT EXISTS (
            SELECT 1 FROM rag.knowledge_document kd
            WHERE kd.external_doc_id = w.id::text AND kd.source_type = 'md'
        )
        ORDER BY w.slug
    """
    if limit:
        sql += f" LIMIT {int(limit)}"
    cur.execute(sql)
    rows = cur.fetchall()
    return [
        {
            "wiki_id": str(r[0]),
            "slug": r[1],
            "title": r[2],
            "content": r[3],
            "difficulty": r[4] or "MIXED",
            "tags": r[5] or [],
            "source_refs": r[6] or [],
            "frontmatter": r[7] or {},
            "summary": r[8] or "",
        }
        for r in rows
    ]


def clear_vectorized_data(cur):
    """Remove vectorized data for re-run."""
    cur.execute("DELETE FROM rag.knowledge_chunk")
    cur.execute("DELETE FROM rag.knowledge_document")
    print("  Cleared existing vectorized data")


def insert_knowledge_document(cur, doc: dict) -> str:
    """Insert a single knowledge_document row. Returns the document id."""
    cur.execute("""
        INSERT INTO rag.knowledge_document (id, title, domain, source_type, source_ref,
            external_doc_id, content_hash, difficulty_level, access_scope, tags, metadata_json,
            created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::app.difficulty_level, %s::app.access_scope, %s, %s, %s)
        ON CONFLICT (course_id, domain, external_doc_id, version) DO UPDATE SET
            title = EXCLUDED.title,
            content_hash = EXCLUDED.content_hash,
            tags = EXCLUDED.tags,
            metadata_json = EXCLUDED.metadata_json,
            updated_at = now()
        RETURNING id
    """, (
        doc["id"],
        doc["title"],
        doc["domain"],
        doc["source_type"],
        doc["source_ref"],
        doc["external_doc_id"],
        doc["content_hash"],
        doc["difficulty"],
        doc["access_scope"],
        json.dumps(doc["tags"], ensure_ascii=False),
        json.dumps(doc["metadata"], ensure_ascii=False),
        doc["created_by"],
    ))
    return str(cur.fetchone()[0])


def insert_knowledge_chunks(cur, chunks: list[dict]):
    """Insert knowledge_chunk rows (batch)."""
    for c in chunks:
        cur.execute("""
            INSERT INTO rag.knowledge_chunk (document_id, chunk_no, content, embedding,
                token_count, domain, difficulty_level, access_scope, quality_score, metadata_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s::app.difficulty_level, %s::app.access_scope, %s, %s)
            ON CONFLICT (document_id, chunk_no) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                token_count = EXCLUDED.token_count,
                quality_score = EXCLUDED.quality_score,
                metadata_json = EXCLUDED.metadata_json
        """, (
            c["document_id"],
            c["chunk_no"],
            c["content"],
            c["embedding"],
            c["token_count"],
            c["domain"],
            c["difficulty"],
            c["access_scope"],
            c["quality_score"],
            json.dumps(c["metadata"], ensure_ascii=False),
        ))


# 鈹€鈹€ Embedding 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def generate_embeddings(texts: list[str], dimension: int = RUNTIME_CONFIG.embedding_dimension) -> list[list[float]]:
    """Generate embeddings for multiple texts via DashScope API."""
    input_data = [{"text": t} for t in texts]
    resp = MultiModalEmbedding.call(
        model=RUNTIME_CONFIG.embedding_model_name,
        input=input_data,
        dimension=dimension,
        output_type="dense",
    )
    if resp.status_code != 200:
        raise RuntimeError(f"API error: code={resp.code} message={resp.message}")

    emb_list = resp.output.get("embeddings", [])
    if not emb_list:
        raise RuntimeError(f"No embeddings in response: {resp.output}")

    # Sort by index to maintain order
    emb_list.sort(key=lambda x: x.get("index", 0))
    return [e["embedding"] for e in emb_list]


def estimate_tokens(text: str) -> int:
    """Rough token estimation for mixed Chinese/English text."""
    # Chinese chars ~1.5 per token, others ~4 per token
    chinese = sum(1 for c in text if "涓€" <= c <= "榭?)
    other = len(text) - chinese
    return int(chinese / 1.5 + other / 4)


def build_embedding_str(vec: list[float]) -> str:
    """Format a float list as pgvector-compatible string."""
    return "[" + ",".join(str(v) for v in vec) + "]"


# 鈹€鈹€ Main 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def main():
    dry_run = "--dry-run" in sys.argv
    incremental = "--incremental" in sys.argv
    limit = None
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    print("=" * 60)
    print("Wiki Vectorization 鈫?PostgreSQL" + (" (INCREMENTAL)" if incremental else ""))
    print(f"Model: qwen3-vl-embedding | Dimension: {DIMENSION}")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN MODE]")

    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                if not dry_run and not incremental:
                    clear_vectorized_data(cur)

                pages = fetch_wiki_pages(cur, limit=limit)
                total = len(pages)
                print(f"\nPages to vectorize: {total}")

                if total == 0:
                    print("Already up to date.")
                    return

                # Process in batches
                for batch_start in range(0, total, BATCH_SIZE):
                    batch = pages[batch_start : batch_start + BATCH_SIZE]
                    batch_num = batch_start // BATCH_SIZE + 1
                    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

                    texts = [p["title"] for p in batch]
                    status = ", ".join(p["title"][:20] for p in batch)
                    print(f"\n[Batch {batch_num}/{total_batches}] {len(batch)} pages: {status}...")

                    if dry_run:
                        print("  (dry-run, skipping API call)")
                        continue

                    # Generate embeddings
                    try:
                        embeddings = generate_embeddings(texts, DIMENSION)
                    except Exception as e:
                        print(f"  API ERROR: {e}")
                        print("  Falling back to single-text mode...")
                        # Retry one by one
                        embeddings = []
                        for t in texts:
                            try:
                                emb = generate_embeddings([t], DIMENSION)
                                embeddings.extend(emb)
                                time.sleep(API_DELAY)
                            except Exception as e2:
                                print(f"  FAILED: {e2}")
                                embeddings.append(None)

                    # Write to DB
                    for i, page in enumerate(batch):
                        emb_vec = embeddings[i] if i < len(embeddings) and embeddings[i] is not None else None
                        if emb_vec is None:
                            print(f"  SKIP (no embedding): {page['title']}")
                            continue

                        content = page["content"]
                        doc = {
                            "id": str(uuid.uuid4()),
                            "title": page["title"],
                            "domain": "COMPUTER_SCIENCE",
                            "source_type": "md",
                            "source_ref": page["slug"],
                            "external_doc_id": page["wiki_id"],
                            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                            "difficulty": page["difficulty"],
                            "access_scope": "GLOBAL",
                            "tags": [json.dumps(page["tags"])] if isinstance(page["tags"], str) else page["tags"],
                            "metadata": {"wiki_page_id": page["wiki_id"], "slug": page["slug"]},
                            "created_by": "wiki_vectorizer",
                        }

                        doc_id = insert_knowledge_document(cur, doc)

                        chunk = {
                            "document_id": doc_id,
                            "chunk_no": 1,
                            "content": content,
                            "embedding": build_embedding_str(emb_vec),
                            "token_count": estimate_tokens(content),
                            "domain": "COMPUTER_SCIENCE",
                            "difficulty": page["difficulty"],
                            "access_scope": "GLOBAL",
                            "quality_score": 0.85,
                            "metadata": {},
                        }
                        insert_knowledge_chunks(cur, [chunk])

                        print(f"  OK [{batch_start + i + 1}/{total}]: {page['title']}  dim={len(emb_vec)}")

                    time.sleep(API_DELAY)

        print(f"\nAll done. {total} pages vectorized.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

