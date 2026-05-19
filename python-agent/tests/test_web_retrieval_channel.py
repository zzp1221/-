from retrieval.rrf_fusion import RRFFusion
from retrieval.hybrid_retriever import HybridRetriever


class _EmptyGrep:
    def search(self, cur, query: str, domain: str) -> dict:
        return {"priority": [], "normal": []}


class _EmptyVector:
    def search_all(self, cur, query: str, *, top_k: int, domain: str) -> list:
        return []


class _EmptyGraph:
    def expand(self, cur, seed_slugs: list, *, top_n: int) -> list:
        return []


class _FailingWeb:
    def search(self, query: str, top_k: int = 5) -> list:
        raise AssertionError("Tavily search should only run when web search is enabled")


def test_rrf_fusion_includes_opt_in_web_channel() -> None:
    fusion = RRFFusion()

    results = fusion.fuse(
        grep_results={"priority": [], "normal": []},
        vector_results=[],
        graph_results=[],
        web_results=[
            ("https://example.com/python", "Python latest release", 0.8, {"snippet": "Example"}),
        ],
        top_n=3,
    )

    assert results == [("https://example.com/python", "Python latest release", 0.0246)]


def test_hybrid_retriever_does_not_call_web_channel_by_default() -> None:
    retriever = HybridRetriever(db_config={})
    retriever._grep = _EmptyGrep()
    retriever._vector = _EmptyVector()
    retriever._graph = _EmptyGraph()
    retriever._web = _FailingWeb()
    retriever._rrf = RRFFusion()
    retriever._initialized = True

    result = retriever.retrieve(cur=object(), query="python release")

    assert result["webSearchEnabled"] is False
    assert result["channels"]["web"] == []
