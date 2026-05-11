"""Measure synonym-group impact on grep retrieval with transactional ablation.

Usage:
  python knowledge/benchmark_synonym_impact.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from knowledge.settings_helper import configure_dashscope_api_key
from retrieval.fmm_tokenizer import FMMTokenizer
from retrieval.grep_searcher import GrepSearcher

RUNTIME_CONFIG = configure_dashscope_api_key()
DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
DOMAIN = RUNTIME_CONFIG.retrieval_domain

TEST_CASES = [
    ("NAC 是什么？", "802.1X"),
    ("DHE 和 ECDHE 有什么区别？", "Diffie-Hellman"),
    ("ESP 在 IPSec 中起什么作用？", "IPSec"),
    ("KDC 在 Kerberos 里负责什么？", "Kerberos"),
    ("PBR 物理渲染是什么？", "PBR"),
]


def collect_titles(result: dict) -> list[str]:
    titles = [item[1] for item in result.get("priority", [])[:3]]
    if len(titles) < 3:
        titles.extend(item[1] for item in result.get("normal", [])[: 3 - len(titles)])
    return titles


def hits_at_3(records: list[dict]) -> int:
    return sum(1 for item in records if item["hit"])


def run_queries(cur) -> list[dict]:
    tokenizer = FMMTokenizer()
    tokenizer.load_from_db(cur, DOMAIN)
    searcher = GrepSearcher(tokenizer)
    rows = []
    for query, expected in TEST_CASES:
        result = searcher.search(cur, query, DOMAIN)
        top_titles = collect_titles(result)
        rows.append(
            {
                "query": query,
                "expected": expected,
                "top_titles": top_titles,
                "hit": any(expected.lower() in title.lower() for title in top_titles),
            }
        )
    return rows


def main() -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                with_synonyms = run_queries(cur)

        conn.rollback()
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM rag.synonym_group")
                without_synonyms = run_queries(cur)
                conn.rollback()
    finally:
        conn.close()

    report = {
        "with_synonyms_hits_at_3": hits_at_3(with_synonyms),
        "without_synonyms_hits_at_3": hits_at_3(without_synonyms),
        "with_synonyms": with_synonyms,
        "without_synonyms": without_synonyms,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
