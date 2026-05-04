"""
Three-channel hybrid retrieval test.
Channel A: Keyword search (simulating FMM + grep)
Channel B: Vector search (pgvector cosine similarity)
Channel C: Graph expansion (wikilink + shared_tag)
Fusion: Weighted RRF (grep:vector = 7:3, k=60)

Usage: python test_hybrid_retrieval.py
"""
import sys
import os
import json
import re
import psycopg2
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()
from collections import defaultdict


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()

RRF_K = 60
GREP_WEIGHT = 7
VECTOR_WEIGHT = 3
VECTOR_TOP_K = 10
GRAPH_SEED_TOP_N = 3
GRAPH_SHARED_TAG_MIN = 3

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

# Expected correct pages (for evaluation)
EXPECTED = {
    "浠€涔堟槸杩涚▼鍜岀嚎绋嬬殑鍖哄埆": ["杩涚▼鐨勫畾涔変笌鐗瑰緛", "绾跨▼鐨勬蹇典笌灞炴€?, "鐢ㄦ埛绾х嚎绋嬩笌鍐呮牳绾х嚎绋?, "澶氱嚎绋嬫ā鍨?],
    "TCP涓夋鎻℃墜鐨勮繃绋?: ["TCP涓夋鎻℃墜"],
    "鏁版嵁搴撲簨鍔＄殑ACID鐗规€?: ["浜嬪姟涓嶢CID鐗规€?],
    "蹇€熸帓搴忕畻娉曠殑鍘熺悊": ["蹇€熸帓搴?, "鎺掑簭绠楁硶"],
    "浠€涔堟槸姝婚攣锛屽浣曢伩鍏?: ["姝婚攣棰勯槻", "姝婚攣閬垮厤-閾惰瀹剁畻娉?, "姝婚攣鐨勫繀瑕佹潯浠?, "姝婚攣妫€娴嬩笌鎭㈠", "姝婚攣澶勭悊"],
    "OSI涓冨眰缃戠粶妯″瀷": ["OSI涓冨眰鍙傝€冩ā鍨?, "TCP/IP浜斿眰妯″瀷"],
    "浠€涔堟槸浜屽弶鎼滅储鏍?: ["浜屽弶鎺掑簭鏍?, "鏈€浼樹簩鍙夋悳绱㈡爲", "浜屽弶鏍?],
    "闈㈠悜瀵硅薄鐨勪笁澶х壒寰?: ["闈㈠悜瀵硅薄缂栫▼", "闈㈠悜瀵硅薄璁捐-绫诲浘-椤哄簭鍥?鐘舵€佸浘", "缁ф壙涓庡鎬?],
}


def embed_query(text: str) -> list[float]:
    resp = MultiModalEmbedding.call(
        model=RUNTIME_CONFIG.embedding_model_name,
        input=[{"text": text}],
        dimension=RUNTIME_CONFIG.embedding_dimension,
        output_type="dense",
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Embedding API error: {resp.code} {resp.message}")
    return resp.output["embeddings"][0]["embedding"]


# 鈹€鈹€ Channel A: Keyword Search 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def extract_keywords(query: str) -> list[str]:
    """Extract meaningful keywords from query (simulating FMM segmentation)."""
    stop_words = {"浠€涔?, "鏄?, "鐨?, "鍜?, "涓?, "濡備綍", "鎬庢牱", "鎬庝箞", "浜?, "鍚?, "鍛?, "鍟?, "杩囩▼", "鍘熺悊", "鐗瑰緛", "鍖哄埆", "閬垮厤", "浠€涔堟槸", "浠€涔堟牱"}
    # Known multi-char terms to extract first (FMM-style)
    known_terms = [
        "TCP涓夋鎻℃墜", "TCP鍥涙鎸ユ墜", "TCP鎷ュ鎺у埗", "TCP娴侀噺鎺у埗",
        "OSI涓冨眰", "蹇€熸帓搴?, "褰掑苟鎺掑簭", "鍐掓场鎺掑簭", "甯屽皵鎺掑簭",
        "浜屽弶鎼滅储鏍?, "浜屽弶鎺掑簭鏍?, "浜屽弶鏍?, "绾㈤粦鏍?, "AVL鏍?,
        "闈㈠悜瀵硅薄", "姝婚攣閬垮厤", "姝婚攣棰勯槻", "姝婚攣妫€娴?,
        "鏁版嵁搴撲簨鍔?, "ACID鐗规€?, "ACID",
        "杩涚▼", "绾跨▼", "姝婚攣", "浜嬪姟", "鎺掑簭",
        "TCP", "UDP", "IP", "HTTP", "OSI",
        "MVCC", "SQL", "灏佽", "缁ф壙", "澶氭€?,
    ]
    keywords = []
    remaining = query
    for term in known_terms:
        if term in remaining:
            keywords.append(term)
            remaining = remaining.replace(term, " ")
    # Split remaining by delimiters
    tokens = re.split(r'[锛屻€傦紵锛併€乗s]+', remaining)
    for t in tokens:
        t = t.strip()
        if t and t not in stop_words and len(t) >= 2 and t not in keywords:
            keywords.append(t)
    return keywords


def channel_a_grep(cur, keywords: list[str]) -> dict:
    """Channel A: Keyword search returning {page_slug: rank}."""
    if not keywords:
        return {}

    # Build ILIKE conditions for each keyword
    matched_pages = defaultdict(int)  # slug -> match_count
    page_titles = {}  # slug -> title

    for kw in keywords:
        cur.execute("""
            SELECT DISTINCT kd.source_ref, kd.title
            FROM rag.knowledge_chunk kc
            JOIN rag.knowledge_document kd ON kd.id = kc.document_id
            WHERE kd.is_active = true
              AND (kc.content ILIKE %s OR kd.title ILIKE %s)
        """, (f"%{kw}%", f"%{kw}%"))
        for slug, title in cur.fetchall():
            matched_pages[slug] += 1
            page_titles[slug] = title

    # Coverage score: what fraction of keywords matched
    # Sort by match count (coverage) descending, then by title
    sorted_pages = sorted(matched_pages.items(), key=lambda x: (-x[1], x[0]))

    # Priority: pages that match ALL original keywords
    all_kw_count = len(keywords)
    priority = [(slug, title) for slug, count in sorted_pages
                if count >= min(all_kw_count, 2) for title in [page_titles.get(slug, slug)]]
    normal = [(slug, title) for slug, count in sorted_pages
              if count < min(all_kw_count, 2) for title in [page_titles.get(slug, slug)]]

    return {
        "priority": priority,
        "normal": normal,
        "all_slugs": {slug: page_titles.get(slug, slug) for slug in matched_pages},
    }


# 鈹€鈹€ Channel B: Vector Search 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def channel_b_vector(cur, query_embedding: list[float], top_k: int = VECTOR_TOP_K) -> list[tuple]:
    """Channel B: Vector search returning [(slug, title, score)]."""
    vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    cur.execute("""
        SELECT kd.source_ref, kd.title, 1 - (kc.embedding <=> %s::vector) AS sim
        FROM rag.knowledge_chunk kc
        JOIN rag.knowledge_document kd ON kd.id = kc.document_id
        WHERE kd.is_active = true
        ORDER BY kc.embedding <=> %s::vector
        LIMIT %s
    """, (vec_str, vec_str, top_k))
    return [(r[0], r[1], r[2]) for r in cur.fetchall()]


# 鈹€鈹€ Channel C: Graph Expansion 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def channel_c_graph(cur, seed_slugs: list[str], min_shared_tags: int = GRAPH_SHARED_TAG_MIN) -> list[tuple]:
    """Channel C: Graph expansion from seed pages via wikilink + shared_tag."""
    if not seed_slugs:
        return []

    # Get wiki_page IDs for seed slugs
    placeholders = ",".join(["%s"] * len(seed_slugs))
    cur.execute(f"""
        SELECT id, slug, title FROM rag.wiki_page
        WHERE slug IN ({placeholders})
    """, seed_slugs)
    seed_pages = cur.fetchall()
    seed_ids = [str(p[0]) for p in seed_pages]
    seed_id_set = set(seed_ids)

    if not seed_ids:
        return []

    # Find neighbors via wikilink
    ph = ",".join(["%s"] * len(seed_ids))
    cur.execute(f"""
        SELECT
            CASE WHEN wl.from_page_id::text IN ({ph}) THEN wl.to_page_id::text
                 ELSE wl.from_page_id::text END AS neighbor_id,
            wl.relation_type,
            COUNT(*) AS strength
        FROM rag.wiki_link wl
        WHERE wl.from_page_id::text IN ({ph})
           OR wl.to_page_id::text IN ({ph})
        GROUP BY neighbor_id, wl.relation_type
        ORDER BY strength DESC
    """, seed_ids * 3)
    neighbor_scores = defaultdict(lambda: {"WIKILINK": 0, "SHARED_TAG": 0})
    for neighbor_id, relation_type, strength in cur.fetchall():
        if neighbor_id not in seed_id_set:
            neighbor_scores[neighbor_id][relation_type] = strength

    # Filter: keep neighbors with WIKILINK OR SHARED_TAG >= min
    qualified = []
    for nid, scores in neighbor_scores.items():
        if scores["WIKILINK"] > 0 or scores["SHARED_TAG"] >= min_shared_tags:
            total = scores["WIKILINK"] * 2 + scores["SHARED_TAG"]
            qualified.append((nid, total))

    qualified.sort(key=lambda x: -x[1])

    # Get page info for qualified neighbors
    results = []
    for nid, score in qualified[:5]:  # top-5 graph neighbors
        cur.execute("SELECT slug, title FROM rag.wiki_page WHERE id::text = %s", (nid,))
        row = cur.fetchone()
        if row:
            results.append((row[0], row[1], score))

    return results


# 鈹€鈹€ RRF Fusion 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def rrf_fusion(grep_results: dict, vector_results: list[tuple], graph_results: list[tuple]) -> list[tuple]:
    """Weighted RRF fusion of all three channels."""
    rrf_scores = defaultdict(float)
    page_info = {}  # slug -> title

    # Priority pages (all keywords match) get a huge boost
    for slug, title in grep_results.get("priority", []):
        rrf_scores[slug] += 1000  # Priority boost
        page_info[slug] = title

    # Normal grep results: RRF with weight
    for rank, (slug, title) in enumerate(grep_results.get("normal", []), 1):
        rrf_scores[slug] += GREP_WEIGHT * (1.0 / (RRF_K + rank))
        page_info[slug] = title

    # Vector results: RRF with weight
    for rank, (slug, title, sim) in enumerate(vector_results, 1):
        rrf_scores[slug] += VECTOR_WEIGHT * (1.0 / (RRF_K + rank))
        page_info[slug] = title

    # Graph expansion: lower weight, appended after
    for rank, (slug, title, strength) in enumerate(graph_results, 1):
        rrf_scores[slug] += 0.5 * (1.0 / (RRF_K + rank))
        page_info[slug] = title

    # Sort by RRF score descending
    sorted_results = sorted(rrf_scores.items(), key=lambda x: -x[1])
    return [(slug, page_info.get(slug, slug), score) for slug, score in sorted_results]


def truncate(text: str, max_len: int = 80) -> str:
    text = text.replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def run_test(query: str, cur):
    """Run a single query through the three-channel hybrid retrieval."""
    expected = EXPECTED.get(query, [])

    print(f"\n{'='*70}")
    print(f"Q: {query}")
    print(f"Expected: {expected}")
    print(f"{'='*70}")

    # Extract keywords
    keywords = extract_keywords(query)
    print(f"\n[Keywords] {keywords}")

    # Channel A: Grep
    grep_results = channel_a_grep(cur, keywords)
    priority = grep_results.get("priority", [])
    normal = grep_results.get("normal", [])
    print(f"\n[Channel A: Grep]")
    print(f"  Priority (all kw match): {[t for _, t in priority]}")
    print(f"  Normal (top-5): {[t for _, t in normal[:5]]}")

    # Channel B: Vector
    try:
        qvec = embed_query(query)
        vector_results = channel_b_vector(cur, qvec)
    except Exception as e:
        print(f"\n[Channel B: Vector] ERROR: {e}")
        vector_results = []
    print(f"\n[Channel B: Vector]")
    for i, (slug, title, sim) in enumerate(vector_results[:5], 1):
        print(f"  {i}. [{sim:.4f}] {title}")

    # Channel C: Graph expansion (from top grep+vector seeds)
    seed_slugs = list(set(
        [s for s, _ in priority] +
        [s for s, _ in normal[:GRAPH_SEED_TOP_N]] +
        [s for s, _, _ in vector_results[:GRAPH_SEED_TOP_N]]
    ))[:GRAPH_SEED_TOP_N]
    graph_results = channel_c_graph(cur, seed_slugs)
    print(f"\n[Channel C: Graph] (seeds: {seed_slugs})")
    for slug, title, score in graph_results:
        print(f"  + {title} (score={score})")

    # RRF Fusion
    final = rrf_fusion(grep_results, vector_results, graph_results)
    print(f"\n[RRF Fusion Top-10]")
    for i, (slug, title, score) in enumerate(final[:10], 1):
        in_expected = " *" if title in expected else ""
        print(f"  {i}. [{score:.4f}] {title}{in_expected}")

    # Evaluation
    top3_titles = {t for _, t, _ in final[:3]}
    top5_titles = {t for _, t, _ in final[:5]}
    hits_at_3 = len(top3_titles & set(expected))
    hits_at_5 = len(top5_titles & set(expected))

    # Check if any expected page is in priority
    priority_titles = {t for _, t in priority}
    priority_hits = len(priority_titles & set(expected))

    print(f"\n[Eval] hits@3={hits_at_3}/{min(3, len(expected))}, "
          f"hits@5={hits_at_5}/{min(5, len(expected))}, "
          f"priority_hits={priority_hits}/{len(expected)}")

    return {
        "query": query,
        "hits_at_3": hits_at_3,
        "hits_at_5": hits_at_5,
        "expected_count": len(expected),
        "priority_hits": priority_hits,
        "top3": list(top3_titles),
    }


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM rag.knowledge_chunk")
            chunk_count = cur.fetchone()[0]
            print(f"Knowledge base: {chunk_count} chunks")

            if chunk_count == 0:
                print("No data found.")
                return

            results = []
            for q in TEST_QUERIES:
                r = run_test(q, cur)
                results.append(r)

            # Summary
            print(f"\n{'='*70}")
            print("SUMMARY")
            print(f"{'='*70}")
            total_h3 = sum(r["hits_at_3"] for r in results)
            total_h5 = sum(r["hits_at_5"] for r in results)
            total_expected = sum(min(3, r["expected_count"]) for r in results)
            total_expected5 = sum(min(5, r["expected_count"]) for r in results)
            total_priority = sum(r["priority_hits"] for r in results)
            total_exp_all = sum(r["expected_count"] for r in results)

            print(f"  hits@3: {total_h3}/{total_expected} = {total_h3/total_expected:.1%}")
            print(f"  hits@5: {total_h5}/{total_expected5} = {total_h5/total_expected5:.1%}")
            print(f"  priority_hits: {total_priority}/{total_exp_all} = {total_priority/total_exp_all:.1%}")

            print(f"\n  Per query:")
            for r in results:
                status = "OK" if r["hits_at_3"] >= min(2, r["expected_count"]) else "WEAK"
                print(f"    [{status}] {r['query']}: hits@3={r['hits_at_3']}, priority={r['priority_hits']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

