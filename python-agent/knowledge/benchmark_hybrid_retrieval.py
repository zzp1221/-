"""Benchmark hybrid retrieval quality and latency.

Usage:
  python knowledge/benchmark_hybrid_retrieval.py
  python knowledge/benchmark_hybrid_retrieval.py --mode current --runs 3
  python knowledge/benchmark_hybrid_retrieval.py --output benchmark.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg2
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.grep_searcher import GrepSearcher
from retrieval.graph_expander import GraphExpander
from retrieval.rrf_fusion import RRFFusion

DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
TOP_K = 5
TRANSIENT_ERROR_MARKERS = (
    "SSLError",
    "EOF occurred in violation of protocol",
    "ConnectionError",
    "ReadTimeout",
)

QUESTIONS = [
    ("操作系统", "什么是死锁？银行家算法如何避免死锁？", ["死锁", "银行家算法"]),
    ("操作系统", "解释虚拟内存的工作原理和页面置换算法", ["虚拟内存", "页面置换"]),
    ("操作系统", "进程和线程的区别是什么？什么时候用多线程什么时候用多进程？", ["进程", "线程"]),
    ("操作系统", "Docker容器和虚拟机有什么区别？", ["容器", "Docker", "虚拟化"]),
    ("数据库原理", "什么是MVCC？MySQL和PostgreSQL的MVCC实现有什么区别？", ["MVCC", "并发控制"]),
    ("数据库原理", "B+树索引的原理是什么？为什么MySQL选择B+树而不是红黑树？", ["B+树", "索引"]),
    ("数据结构", "红黑树的插入和删除操作是怎么维护平衡的？", ["红黑树", "平衡"]),
    ("数据结构", "KMP算法的核心思想是什么？next数组怎么求？", ["KMP", "字符串匹配"]),
    ("计算机网络", "TCP三次握手和四次挥手的过程是什么？为什么不能两次握手？", ["TCP", "三次握手"]),
    ("计算机网络", "HTTPS的TLS握手过程是怎样的？", ["TLS", "HTTPS", "握手"]),
    ("编译原理", "LL(1)和LR(1)语法分析的区别是什么？", ["LL", "LR", "语法分析"]),
    ("编译原理", "垃圾回收算法有哪些？分代回收是怎么工作的？", ["GC", "垃圾回收", "分代"]),
    ("算法设计与分析", "动态规划和贪心算法的区别是什么？什么时候用哪个？", ["动态规划", "贪心"]),
    ("算法设计与分析", "Dijkstra算法和Bellman-Ford算法的区别？", ["Dijkstra", "Bellman-Ford", "最短路径"]),
    ("程序设计", "Go语言的Goroutine和Channel是怎么工作的？", ["Go", "Goroutine", "Channel"]),
    ("程序设计", "Rust的所有权和借用检查是怎么保证内存安全的？", ["Rust", "所有权", "借用"]),
    ("离散数学", "什么是谓词逻辑？和命题逻辑有什么区别？", ["谓词逻辑", "命题逻辑"]),
    ("信息安全", "TLS 1.3的握手过程和TLS 1.2有什么区别？", ["TLS", "握手"]),
    ("分布式系统", "Raft共识算法的Leader选举过程是怎样的？", ["Raft", "共识", "选举"]),
    ("计算机图形学", "什么是PBR物理渲染？", ["PBR", "物理渲染"]),
]


def is_relevant(result: tuple, keywords: list[str]) -> bool:
    slug_lower = str(result[0]).lower()
    title_lower = str(result[1]).lower()
    return any(
        keyword.lower() in slug_lower or keyword.lower() in title_lower
        for keyword in keywords
    )


def percentile_ms(values_ms: list[float], ratio: float) -> float:
    if not values_ms:
        return 0.0
    ordered = sorted(values_ms)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * ratio)))
    return round(ordered[index], 2)


def find_first_relevant_rank(results: list[tuple], keywords: list[str]) -> int | None:
    for rank, item in enumerate(results, start=1):
        if is_relevant(item, keywords):
            return rank
    return None


def summarize_queries(per_query: list[dict], latencies_ms: list[float]) -> dict:
    total = len(per_query)
    hits_at_1 = sum(1 for item in per_query if item["top1_relevant"])
    hits_at_3 = sum(1 for item in per_query if item["top3_relevant"])
    first_recall_hits = sum(1 for item in per_query if item["first_relevant_rank"] is not None)
    reciprocal_ranks = [
        (1.0 / item["first_relevant_rank"]) if item["first_relevant_rank"] is not None else 0.0
        for item in per_query
    ]
    return {
        "total_queries": total,
        "hits_at_1": hits_at_1,
        "hits_at_3": hits_at_3,
        "hits_at_1_pct": round(hits_at_1 / total * 100, 2),
        "hits_at_3_pct": round(hits_at_3 / total * 100, 2),
        "top1_pct": round(hits_at_1 / total * 100, 2),
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "first_recall_rate_pct": round(first_recall_hits / total * 100, 2),
        "avg_latency_ms": round(statistics.mean(latencies_ms), 2),
        "median_latency_ms": round(statistics.median(latencies_ms), 2),
        "p95_latency_ms": percentile_ms(latencies_ms, 0.95),
        "max_latency_ms": round(max(latencies_ms), 2),
    }


def aggregate_runs(run_reports: list[dict]) -> dict:
    metric_names = (
        "top1_pct",
        "mrr",
        "first_recall_rate_pct",
        "hits_at_3_pct",
        "avg_latency_ms",
        "median_latency_ms",
        "p95_latency_ms",
        "max_latency_ms",
    )
    averages = {
        metric: round(
            statistics.mean(report["summary"][metric] for report in run_reports),
            4 if metric == "mrr" else 2,
        )
        for metric in metric_names
    }
    return {
        "runs": len(run_reports),
        "averages": averages,
        "per_run": [report["summary"] for report in run_reports],
    }


@contextmanager
def benchmark_mode(mode: str):
    original_rrf_init = RRFFusion.__init__
    original_lookup = GrepSearcher._lookup_synonym_terms
    original_has_graph_features = getattr(GraphExpander, "_has_graph_features", None)

    if mode == "rollback_candidate":
        def baseline_rrf_init(
            self,
            k: int = 60,
            grep_weight: float = 3.0,
            vector_weight: float = 5.0,
            graph_weight: float = 0.5,
        ):
            original_rrf_init(
                self,
                k=k,
                grep_weight=grep_weight,
                vector_weight=vector_weight,
                graph_weight=graph_weight,
            )

        def no_synonym_terms(self, cur, query_lower: str, domain: str):
            return []

        def disable_graph_features(self, cur) -> bool:
            return False

        RRFFusion.__init__ = baseline_rrf_init
        GrepSearcher._lookup_synonym_terms = no_synonym_terms
        GraphExpander._has_graph_features = disable_graph_features

    try:
        yield
    finally:
        RRFFusion.__init__ = original_rrf_init
        GrepSearcher._lookup_synonym_terms = original_lookup
        if original_has_graph_features is None:
            if hasattr(GraphExpander, "_has_graph_features"):
                delattr(GraphExpander, "_has_graph_features")
        else:
            GraphExpander._has_graph_features = original_has_graph_features


def retrieve_with_retry(retriever: HybridRetriever, cur, question: str, retries: int = 1) -> tuple[dict, float, int]:
    attempts = 0
    while True:
        attempts += 1
        started = time.perf_counter()
        try:
            result = retriever.retrieve(cur, question)
            elapsed_ms = (time.perf_counter() - started) * 1000
            return result, elapsed_ms, attempts
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            if attempts > retries + 1:
                raise
            message = f"{type(exc).__name__}: {exc}"
            if not any(marker in message for marker in TRANSIENT_ERROR_MARKERS):
                raise
            time.sleep(0.6)


def run_benchmark(mode: str = "current") -> dict:
    conn = psycopg2.connect(**DB_CONFIG)
    retriever = HybridRetriever(DB_CONFIG, top_k=5)
    latencies_ms: list[float] = []
    per_query: list[dict] = []

    try:
        with benchmark_mode(mode):
            with conn:
                with conn.cursor() as cur:
                    for course, question, keywords in QUESTIONS:
                        result, elapsed_ms, attempts = retrieve_with_retry(retriever, cur, question)
                        latencies_ms.append(elapsed_ms)

                        top = result.get("top", [])
                        top1_relevant = bool(top and is_relevant(top[0], keywords))
                        top3_relevant = any(is_relevant(item, keywords) for item in top[:3])
                        first_relevant_rank = find_first_relevant_rank(top[:TOP_K], keywords)

                        per_query.append(
                            {
                                "course": course,
                                "question": question,
                                "keywords": keywords,
                                "latency_ms": round(elapsed_ms, 2),
                                "attempts": attempts,
                                "top1_relevant": top1_relevant,
                                "top3_relevant": top3_relevant,
                                "first_relevant_rank": first_relevant_rank,
                                "top_titles": [item[1] for item in top[:TOP_K]],
                            }
                        )
    finally:
        conn.close()

    summary = summarize_queries(per_query, latencies_ms)
    return {"summary": summary, "queries": per_query}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("current", "rollback_candidate"),
        default="current",
    )
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    run_reports = [run_benchmark(mode=args.mode) for _ in range(args.runs)]
    aggregate = aggregate_runs(run_reports)
    report = {
        "mode": args.mode,
        "aggregate": aggregate,
        "runs": run_reports,
    }

    print(f"Hybrid Retrieval Benchmark [{args.mode}]")
    print(json.dumps(report["aggregate"], ensure_ascii=False, indent=2))

    if args.output is not None:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()
