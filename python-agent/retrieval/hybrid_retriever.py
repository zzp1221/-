"""
Hybrid Retriever: orchestrates grep + vector + graph channels with RRF fusion.
"""
import psycopg2
from retrieval.fmm_tokenizer import FMMTokenizer
from retrieval.grep_searcher import GrepSearcher
from retrieval.vector_searcher import VectorSearcher
from retrieval.graph_expander import GraphExpander
from retrieval.rrf_fusion import RRFFusion


class HybridRetriever:
    """3-channel hybrid retrieval with weighted RRF fusion."""

    def __init__(self, db_config: dict, domain: str = "COMPUTER_SCIENCE",
                 top_k: int = 10, graph_seed_n: int = 3):
        self.db_config = db_config
        self.domain = domain
        self.top_k = top_k
        self.graph_seed_n = graph_seed_n

        # Lazy init
        self._tokenizer: FMMTokenizer = None
        self._grep: GrepSearcher = None
        self._vector: VectorSearcher = None
        self._graph: GraphExpander = None
        self._rrf: RRFFusion = None
        self._initialized = False

    def _init(self, cur):
        if self._initialized:
            return
        self._tokenizer = FMMTokenizer()
        n = self._tokenizer.load_from_db(cur, self.domain)
        self._grep = GrepSearcher(self._tokenizer)
        self._vector = VectorSearcher()
        self._graph = GraphExpander()
        self._rrf = RRFFusion()
        self._initialized = True
        print(f"  [HybridRetriever] Loaded {n} terms from term_lexicon")

    def retrieve(self, cur, query: str) -> dict:
        """Run all 3 channels and fuse. Returns structured results."""
        self._init(cur)

        # Channel A: Grep (keyword + coverage)
        grep_results = self._grep.search(cur, query, self.domain)

        # Channel B: Vector (semantic) — search both knowledge + resource
        vector_all = self._vector.search_all(cur, query, top_k=self.top_k, domain=self.domain)
        # Strip source tag for RRF: [(slug, title, similarity), ...]
        vector_results = [(r[0], r[1], r[2]) for r in vector_all]

        # Channel C: Graph expansion from top seeds
        grep_slugs = [r[0] for r in grep_results.get("priority", [])[:self.graph_seed_n]]
        vec_slugs = [r[0] for r in vector_results[:self.graph_seed_n]]
        seed_slugs = list(dict.fromkeys(grep_slugs + vec_slugs))[:self.graph_seed_n]
        graph_results = self._graph.expand(cur, seed_slugs, top_n=5)

        # RRF Fusion
        fused = self._rrf.fuse(grep_results, vector_results, graph_results)

        return {
            "query": query,
            "channels": {
                "grep": {
                    "priority": grep_results.get("priority", []),
                    "normal_count": len(grep_results.get("normal", [])),
                },
                "vector": [(r[0], r[1], r[2], r[3]) for r in vector_all[:5]],
                "graph": graph_results,
            },
            "fused": fused,
            "top": fused[:5],
        }

    def retrieve_flat(self, cur, query: str) -> list[tuple]:
        """Simple flat list of top fused results."""
        return self.retrieve(cur, query)["top"]
