"""
Grep (keyword) search channel with phrase-first matching + token-level fallback.
"""
import re

from retrieval.fmm_tokenizer import FMMTokenizer


class GrepSearcher:
    """Phrase-first: complete query as contiguous substring → priority.
    Token-level ILIKE matching only as fallback → normal."""

    def __init__(self, tokenizer: FMMTokenizer):
        self.tokenizer = tokenizer

    @staticmethod
    def _normalize_phrase(text: str) -> str:
        return re.sub(r"\s+", "", text.strip().lower())

    def _compute_phrase_priority(
        self,
        *,
        title: str,
        query: str,
        body_match: bool,
    ) -> tuple[int, float]:
        """Score phrase matches so exact/near-exact title hits rank before body hits."""

        normalized_title = self._normalize_phrase(title)
        normalized_query = self._normalize_phrase(query)

        if normalized_title == normalized_query:
            return (400, 1.0)
        if normalized_title.startswith(normalized_query):
            return (350, 0.98)
        if normalized_query in normalized_title:
            return (300, 0.95)
        if body_match:
            return (200, 0.9)
        return (100, 0.85)

    _STOPWORDS = frozenset(
        "什么 是 的 和 与 如何 怎样 怎么 了 吗 呢 啊 请问 请".split()
    )
    _PUNCT_RE = re.compile(r"[，。？！、；：“”‘’（）\[\]【】\s]+")

    def search(self, cur, query: str, domain: str = "COMPUTER_SCIENCE",
               coverage_min: float = 0.0) -> dict:
        """
        Returns:
          - priority: [(slug, title, coverage, tokens_matched), ...] — phrase matches only
          - normal:   [(slug, title, coverage, tokens_matched), ...] — token-level fallback
        """
        query_lower = query.lower()

        # Phase 1: Phrase search — complete query as contiguous substring
        priority = self._phrase_search(cur, query, query_lower, domain)

        # Phase 1.5: FMM-term sub-phrase search — each recognized term as a phrase
        if not priority:
            priority = self._term_phrase_search(cur, query_lower, domain)

        # Phase 2: Token-level fallback — only when phrase search finds nothing
        normal = []
        if not priority:
            normal = self._token_search(cur, query_lower, domain, coverage_min)

        return {"priority": priority, "normal": normal}

    def _term_phrase_search(self, cur, query_lower: str, domain: str) -> list:
        """Search for FMM-recognized terms as individual phrases in titles/content."""
        cleaned = self._clean_query(query_lower)
        if not cleaned:
            return []

        tokens = self.tokenizer.tokenize(cleaned)
        terms = [t for t in tokens if t.term_type != "CHAR" and len(t.text) >= 2]
        if not terms:
            return []

        # For each recognized term, search as phrase in titles and content
        phrase_results: dict[str, dict] = {}
        for token in terms:
            # Title match (higher priority)
            cur.execute("""
                SELECT source_ref AS slug, title
                FROM rag.knowledge_document
                WHERE title ILIKE %s AND domain = %s
            """, (f"%{token.text}%", domain))
            for slug, title in cur.fetchall():
                priority_score, coverage = self._compute_phrase_priority(
                    title=title, query=token.text, body_match=False,
                )
                # Boost by IDF: more specific terms get higher priority
                boosted_score = priority_score + token.idf * 10
                current = phrase_results.get(slug)
                if current is None or boosted_score > current["priority_score"]:
                    phrase_results[slug] = {
                        "title": title,
                        "coverage": coverage,
                        "priority_score": boosted_score,
                        "tokens": [token.text],
                    }

            # Content match (lower priority)
            cur.execute("""
                SELECT DISTINCT kd.source_ref AS slug, kd.title
                FROM rag.knowledge_chunk kc
                JOIN rag.knowledge_document kd ON kd.id = kc.document_id
                WHERE kc.content ILIKE %s AND kd.domain = %s
            """, (f"%{token.text}%", domain))
            for slug, title in cur.fetchall():
                if slug in phrase_results:
                    continue  # title match already exists, skip lower-priority content match
                priority_score, coverage = self._compute_phrase_priority(
                    title=title, query=token.text, body_match=True,
                )
                boosted_score = priority_score + token.idf * 5
                phrase_results[slug] = {
                    "title": title,
                    "coverage": coverage,
                    "priority_score": boosted_score,
                    "tokens": [token.text],
                }

        ranked = sorted(
            phrase_results.items(),
            key=lambda item: (item[1]["priority_score"], item[1]["coverage"]),
            reverse=True,
        )
        return [
            (slug, info["title"], info["coverage"], info["tokens"])
            for slug, info in ranked
        ]

    def _clean_query(self, text: str) -> str:
        """Remove stopwords and punctuation, keep meaningful terms."""
        segments = self._PUNCT_RE.split(text)
        kept: list[str] = []
        for seg in segments:
            # Remove stopwords from within each segment
            cleaned_seg = seg
            for sw in self._STOPWORDS:
                cleaned_seg = cleaned_seg.replace(sw, "")
            if len(cleaned_seg) >= 2:
                kept.append(cleaned_seg)
        return "".join(kept)

    def _phrase_search(self, cur, query: str, query_lower: str, domain: str) -> list:
        """Search for the complete query as a contiguous phrase in content and titles."""
        phrase_results: dict[str, dict] = {}

        # Search in chunk content (coverage=1.0 for full phrase match in body)
        cur.execute("""
            SELECT DISTINCT kd.source_ref AS slug, kd.title
            FROM rag.knowledge_chunk kc
            JOIN rag.knowledge_document kd ON kd.id = kc.document_id
            WHERE kc.content ILIKE %s AND kd.domain = %s
        """, (f"%{query}%", domain))
        for slug, title in cur.fetchall():
            priority_score, coverage = self._compute_phrase_priority(
                title=title,
                query=query,
                body_match=True,
            )
            phrase_results[slug] = {
                "title": title,
                "coverage": coverage,
                "priority_score": priority_score,
                "tokens": [query],
            }

        # Search in document titles (coverage=0.9 for title-only match)
        cur.execute("""
            SELECT source_ref AS slug, title
            FROM rag.knowledge_document
            WHERE title ILIKE %s AND domain = %s
        """, (f"%{query}%", domain))
        for slug, title in cur.fetchall():
            priority_score, coverage = self._compute_phrase_priority(
                title=title,
                query=query,
                body_match=False,
            )
            current = phrase_results.get(slug)
            if current is None or priority_score > current["priority_score"]:
                phrase_results[slug] = {
                    "title": title,
                    "coverage": coverage,
                    "priority_score": priority_score,
                    "tokens": [query],
                }

        ranked = sorted(
            phrase_results.items(),
            key=lambda item: (
                item[1]["priority_score"],
                item[1]["coverage"],
                -len(item[1]["title"]),
            ),
            reverse=True,
        )
        return [
            (slug, info["title"], info["coverage"], info["tokens"])
            for slug, info in ranked
        ]

    def _token_search(self, cur, query_lower: str, domain: str,
                      coverage_min: float) -> list:
        """Fallback: token-level ILIKE with IDF-weighted coverage scoring."""
        tokens = self.tokenizer.tokenize(query_lower)
        if not tokens:
            return []

        known = [t for t in tokens if t.term_type != "CHAR"]
        if not known:
            known = tokens

        total_idf = sum(t.idf for t in known)
        if total_idf == 0:
            return []

        matched_docs: dict[str, dict] = {}
        for token in known:
            cur.execute("""
                SELECT DISTINCT kd.source_ref AS slug, kd.title
                FROM rag.knowledge_chunk kc
                JOIN rag.knowledge_document kd ON kd.id = kc.document_id
                WHERE kc.content ILIKE %s AND kd.domain = %s
            """, (f"%{token.text}%", domain))
            for slug, title in cur.fetchall():
                if slug not in matched_docs:
                    matched_docs[slug] = {"title": title, "tokens_matched": set(), "idf_sum": 0.0}
                matched_docs[slug]["tokens_matched"].add(token.text)
                matched_docs[slug]["idf_sum"] += token.idf

        results = []
        for slug, doc in matched_docs.items():
            coverage = doc["idf_sum"] / total_idf if total_idf > 0 else 0
            if coverage < coverage_min:
                continue
            tokens_matched = sorted(doc["tokens_matched"])
            results.append((slug, doc["title"], round(coverage, 4), tokens_matched))

        results.sort(key=lambda x: x[2], reverse=True)
        return results
