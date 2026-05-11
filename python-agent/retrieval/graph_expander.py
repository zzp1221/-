"""
Graph expansion channel: traverse rag.wiki_link from seed pages.
"""
class GraphExpander:
    """Expand from seed slugs via WIKILINK and SHARED_TAG relations."""

    def expand(self, cur, seed_slugs: list[str], top_n: int = 5,
               min_shared_tags: int = 3) -> list[tuple]:
        """
        Returns top_n neighbors as [(slug, title, score), ...].
        Score = WIKILINK_count * 2 + SHARED_TAG_count.
        """
        if not seed_slugs:
            return []

        # Get wiki page IDs for seed slugs
        cur.execute("""
            SELECT id, slug, title FROM rag.wiki_page
            WHERE slug = ANY(%s) AND is_active = true
        """, (seed_slugs,))
        seed_rows = cur.fetchall()
        if not seed_rows:
            return []

        seed_ids = [row[0] for row in seed_rows]
        seed_slug_set = {row[1] for row in seed_rows}

        # Find neighbors via WIKILINK and SHARED_TAG
        cur.execute("""
            SELECT
                wl2.slug AS neighbor_slug,
                wl2.title AS neighbor_title,
                SUM(CASE WHEN l.relation_type = 'WIKILINK' THEN 2 ELSE 1 END) AS score
            FROM rag.wiki_link l
            JOIN rag.wiki_page wl2 ON wl2.id = l.to_page_id
            WHERE l.from_page_id::text = ANY(%s)
              AND wl2.is_active = true
              AND wl2.slug != ALL(%s)
            GROUP BY wl2.slug, wl2.title
            ORDER BY score DESC
            LIMIT %s
        """, (seed_ids, seed_slugs, top_n * 2))

        neighbors = {}
        for neighbor_slug, neighbor_title, score in cur.fetchall():
            if neighbor_slug not in seed_slug_set:
                neighbors[neighbor_slug] = (neighbor_slug, neighbor_title, int(score))

        # Sort by score and return top_n
        return sorted(neighbors.values(), key=lambda x: x[2], reverse=True)[:top_n]
