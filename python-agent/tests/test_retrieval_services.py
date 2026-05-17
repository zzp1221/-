from src.ai_modules.retrieval import HybridRetrievalService, QueryRewriteService


class FakeRetriever:
    def retrieve(self, query: str) -> dict:
        return {
            "query": query,
            "channels": {
                "grep": {
                    "priority": [
                        ("composite-index", "联合索引", 1.0, ["联合索引"]),
                    ]
                },
                "vector": [
                    ("db-index", "数据库索引导学", 0.91),
                    ("composite-index", "联合索引", 0.8),
                ],
                "graph": [],
            },
            "top": [
                ("db-index", "数据库索引导学", 0.91),
                ("composite-index", "联合索引", 0.8),
            ],
        }


class EmptyRetriever:
    def retrieve(self, query: str) -> dict:
        return {"query": query, "top": []}


class DuplicateTitleRetriever:
    def retrieve(self, query: str) -> dict:
        return {
            "query": query,
            "channels": {
                "grep": {
                    "priority": [
                        ("doc-a", "联合索引", 0.95, ["联合索引"]),
                    ]
                },
                "vector": [
                    ("doc-b", "联合索引", 0.91, {"snippet": "联合索引用于提升多字段查询效率"}),
                ],
                "graph": [],
            },
            "top": [
                ("doc-a", "联合索引", 0.95, {"snippet": "联合索引用于提升多字段查询效率"}),
                ("doc-b", "联合索引", 0.91, {"snippet": "联合索引用于提升多字段查询效率"}),
            ],
        }


class CountingRetriever:
    def __init__(self) -> None:
        self.calls = 0

    def retrieve(self, query: str) -> dict:
        self.calls += 1
        return {
            "query": query,
            "channels": {
                "grep": {"priority": [("cache-doc", "Cache Doc", 1.0, ["cache"])]},
                "vector": [],
                "graph": [],
            },
            "top": [("cache-doc", "Cache Doc", 1.0)],
        }


def test_query_rewrite_service_injects_learning_context() -> None:
    service = QueryRewriteService()

    result = service.rewrite(
        {
            "query": "联合索引",
            "learningContext": {"course": "数据库原理", "chapter": "索引"},
        }
    )

    assert result.original_query == "联合索引"
    assert result.rewritten_query == "数据库原理 联合索引"
    assert "联合索引" in result.keywords


def test_query_rewrite_service_prefers_resource_business_fields_over_resource_type() -> None:
    service = QueryRewriteService()

    result = service.rewrite(
        {
            "resourceType": "DOCUMENT",
            "course": "Java 程序设计",
            "difficulty": "intermediate",
            "keyPoints": "并发编程",
            "learningContext": {"course": "Java 程序设计", "chapter": "并发编程"},
        }
    )

    assert result.original_query == "Java 程序设计 并发编程 intermediate"
    assert result.rewritten_query == "Java 程序设计 并发编程 intermediate"
    assert "DOCUMENT" not in result.original_query


def test_hybrid_retrieval_service_normalizes_documents() -> None:
    service = HybridRetrievalService(retriever=FakeRetriever())

    result = service.retrieve(
        query="联合索引",
        rewritten_query="数据库原理 索引 联合索引",
        keywords=["数据库原理", "索引", "联合索引"],
    )

    assert result.documents[0].slug == "composite-index"
    assert result.documents[0].channel == "phrase"
    assert result.documents[0].match_type == "title_exact"
    assert "联合索引" in result.sources_summary


def test_hybrid_retrieval_service_falls_back_when_no_results() -> None:
    service = HybridRetrievalService(retriever=EmptyRetriever())

    result = service.retrieve(
        query="联合索引",
        rewritten_query="数据库原理 索引 联合索引",
        keywords=["数据库原理", "索引", "联合索引"],
    )

    assert result.documents[0].channel == "fallback"


def test_hybrid_retrieval_service_caches_raw_results_without_mutation_leak() -> None:
    retriever = CountingRetriever()
    service = HybridRetrievalService(retriever=retriever)

    first = service.retrieve_raw("cache-query-unique")
    first["top"].append(("mutated", "Mutated", 0.1))
    second = service.retrieve_raw("cache-query-unique")

    assert retriever.calls == 1
    assert second["top"] == [("cache-doc", "Cache Doc", 1.0)]


def test_hybrid_retrieval_service_deduplicates_same_title_documents() -> None:
    service = HybridRetrievalService(retriever=DuplicateTitleRetriever())

    result = service.retrieve(
        query="联合索引",
        rewritten_query="数据库原理 索引 联合索引",
        keywords=["数据库原理", "索引", "联合索引"],
    )

    assert len(result.documents) == 1
    assert result.documents[0].title == "联合索引"
