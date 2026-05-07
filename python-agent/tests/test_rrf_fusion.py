from retrieval.rrf_fusion import RRFFusion


def test_rrf_fusion_keeps_grep_matches_in_ranked_results() -> None:
    fusion = RRFFusion()

    results = fusion.fuse(
        grep_results={
            "priority": [("程序设计/并发编程", "并发编程", 0.95, ["并发编程"])],
            "normal": [],
        },
        vector_results=[],
        graph_results=[],
        top_n=3,
    )

    assert results
    assert results[0][0] == "程序设计/并发编程"
