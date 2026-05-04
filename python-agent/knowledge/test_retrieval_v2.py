"""
Test: compare old ILIKE grep vs new FMM+IDF+Coverage grep channel.
Usage: python test_retrieval_v2.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()
from retrieval.hybrid_retriever import HybridRetriever

DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()

TEST_QUERIES = [
    "TCP三次握手",
    "进程同步PV操作",
    "红黑树旋转",
    "死锁预防",
    "动态规划状态转移方程",
    "面向对象设计原则SOLID",
    "LR语法分析器",
    "页面置换算法",
]


def old_iliKE_search(cur, query: str) -> list[tuple]:
    """Old approach: simple ILIKE substring matching."""
    keywords = query.split()
    conditions = " AND ".join([f"kc.content ILIKE '%%{kw}%%'" for kw in keywords]) if keywords else "1=1"
    cur.execute(f"""
        SELECT DISTINCT kd.source_ref AS slug, kd.title
        FROM rag.knowledge_chunk kc
        JOIN rag.knowledge_document kd ON kd.id = kc.document_id
        WHERE {conditions} AND kd.domain = %s
        LIMIT 10
    """, (RUNTIME_CONFIG.retrieval_domain,))
    return [(row[0], row[1]) for row in cur.fetchall()]


def main():
    print("=" * 70)
    print("  Retrieval Comparison: ILIKE vs FMM+IDF+Coverage")
    print("=" * 70)

    retriever = HybridRetriever(DB_CONFIG)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for query in TEST_QUERIES:
        print(f"\n── Query: \"{query}\" ──")

        # Old approach
        old_results = old_iliKE_search(cur, query)
        print(f"  [ILIKE] {len(old_results)} results:")
        for slug, title in old_results[:5]:
            print(f"    - {title}")

        # New approach
        result = retriever.retrieve(cur, query)
        grep_priority = result["channels"]["grep"]["priority"]
        grep_normal_count = result["channels"]["grep"]["normal_count"]
        print(f"  [FMM+IDF] priority={len(grep_priority)}, normal={grep_normal_count}")
        for slug, title, coverage, tokens in grep_priority[:5]:
            print(f"    - [{coverage:.2f}] {title}  tokens={tokens[:5]}...")

        fused = result["fused"]
        print(f"  [RRF Fused] top-5:")
        for slug, title, score in fused[:5]:
            print(f"    - [{score:.2f}] {title}")

    cur.close()
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
