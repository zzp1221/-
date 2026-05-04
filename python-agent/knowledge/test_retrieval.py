"""
Test vector retrieval from the RAG knowledge base.
Usage: python test_retrieval.py [query]
"""
import sys
import os
import json
import psycopg2
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()

TEST_QUERIES = [
    "浠€涔堟槸杩涚▼鍜岀嚎绋嬬殑鍖哄埆",
    "TCP涓夋鎻℃墜鐨勮繃绋?,
    "鏁版嵁搴撲簨鍔＄殑ACID鐗规€?,
    "蹇€熸帓搴忕畻娉曠殑鍘熺悊",
    "浠€涔堟槸姝婚攣锛屽浣曢伩鍏?,
    "OSI涓冨眰缃戠粶妯″瀷",
    "浠€涔堟槸浜屽弶鎼滅储鏍?,
    "闈㈠悜瀵硅薄鐨勪笁澶х壒寰?,
]


def embed_query(text: str) -> list[float]:
    """Generate embedding for a single query text."""
    resp = MultiModalEmbedding.call(
        model=RUNTIME_CONFIG.embedding_model_name,
        input=[{"text": text}],
        dimension=RUNTIME_CONFIG.embedding_dimension,
        output_type="dense",
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Embedding API error: {resp.code} {resp.message}")
    embeddings = resp.output.get("embeddings", [])
    if not embeddings:
        raise RuntimeError(f"No embeddings returned: {resp.output}")
    return embeddings[0]["embedding"]


def vector_search(cur, query_embedding: list[float], top_k: int = 5):
    """Search knowledge_chunk by cosine similarity."""
    vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    cur.execute("""
        SELECT
            kc.id,
            kc.content,
            kd.title,
            kc.difficulty_level,
            kc.quality_score,
            1 - (kc.embedding <=> %s::vector) AS cosine_similarity
        FROM rag.knowledge_chunk kc
        JOIN rag.knowledge_document kd ON kd.id = kc.document_id
        WHERE kd.is_active = true
        ORDER BY kc.embedding <=> %s::vector
        LIMIT %s
    """, (vec_str, vec_str, top_k))
    return cur.fetchall()


def keyword_search(cur, keyword: str, top_k: int = 5):
    """Simple ILIKE keyword search for comparison."""
    cur.execute("""
        SELECT
            kc.id,
            kc.content,
            kd.title,
            kc.difficulty_level,
            kc.quality_score
        FROM rag.knowledge_chunk kc
        JOIN rag.knowledge_document kd ON kd.id = kc.document_id
        WHERE kd.is_active = true
          AND (kc.content ILIKE %s OR kd.title ILIKE %s)
        ORDER BY kc.quality_score DESC
        LIMIT %s
    """, (f"%{keyword}%", f"%{keyword}%", top_k))
    return cur.fetchall()


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate text for display."""
    text = text.replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def run_test(query: str, cur):
    """Run a single query test: vector search + keyword search."""
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")

    # Keyword search
    keywords = query.replace("锛?, "").replace("锛?, " ").replace("鐨?, " ").split()
    kw_results = set()
    for kw in keywords:
        if len(kw) >= 2:
            rows = keyword_search(cur, kw, top_k=3)
            for r in rows:
                kw_results.add((r[0], r[2]))  # (id, title)

    if kw_results:
        print(f"\n[Keyword matches] Found {len(kw_results)} pages:")
        for _, title in sorted(kw_results, key=lambda x: x[1]):
            print(f"  - {title}")
    else:
        print("\n[Keyword matches] None")

    # Vector search
    try:
        query_vec = embed_query(query)
        rows = vector_search(cur, query_vec, top_k=5)
    except Exception as e:
        print(f"\n[Vector search] ERROR: {e}")
        return

    print(f"\n[Vector top-5]")
    for i, (rid, content, title, diff, quality, sim) in enumerate(rows, 1):
        in_kw = " *" if (rid, title) in kw_results else ""
        print(f"  {i}. [{sim:.4f}] {title} (diff={diff}, q={quality}){in_kw}")
        print(f"     {truncate(content, 100)}")

    # Overlap analysis
    kw_titles = {t for _, t in kw_results}
    vec_titles = {r[2] for r in rows[:3]}
    overlap = kw_titles & vec_titles
    print(f"\n[Overlap] Top-3 vector vs keyword: {len(overlap)}/{min(3, len(kw_titles))} = {overlap or 'none'}")


def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Check data exists
            cur.execute("SELECT count(*) FROM rag.knowledge_chunk")
            chunk_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM rag.knowledge_document")
            doc_count = cur.fetchone()[0]
            print(f"Knowledge base: {doc_count} documents, {chunk_count} chunks")

            if chunk_count == 0:
                print("No data found. Run vectorize_wiki.py first.")
                return

            if query:
                run_test(query, cur)
            else:
                for q in TEST_QUERIES:
                    run_test(q, cur)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

