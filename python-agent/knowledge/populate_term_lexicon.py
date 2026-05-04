"""
Populate rag.term_lexicon from wiki page tags, titles, and aliases.
Computes IDF = log(N / df) from document frequencies across all wiki pages.
Usage: python populate_term_lexicon.py [--dry-run]
"""
import sys
import math
import json
from collections import defaultdict

import psycopg2
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()

DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
DOMAIN = RUNTIME_CONFIG.retrieval_domain


def connect():
    return psycopg2.connect(**DB_CONFIG)


def normalize_term(term: str) -> str:
    """Normalize a term for case-insensitive matching."""
    return term.strip().lower()


def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("Populate rag.term_lexicon from wiki pages")
    print("=" * 60)

    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                # Fetch all wiki pages: title, tags, aliases, body_md
                cur.execute("""
                    SELECT slug, title, tags, aliases, markdown_content
                    FROM rag.wiki_page WHERE is_active = true AND domain = %s
                """, (DOMAIN,))
                rows = cur.fetchall()
                N = len(rows)
                print(f"\nTotal wiki pages (N): {N}")

                # Collect all terms
                # term -> set of slugs where it appears (for DF computation)
                term_docs: dict[str, set] = defaultdict(set)
                term_meta: dict[str, dict] = {}  # term -> {canonical, term_type, aliases}

                for slug, title, tags, aliases, content in rows:
                    # 1. Title as TERM
                    t = title.strip()
                    if t:
                        nt = normalize_term(t)
                        term_docs[nt].add(slug)
                        term_meta[nt] = {"canonical": t, "term_type": "TERM", "aliases": []}

                    # 2. Tags as TERM (highest quality)
                    tag_list = tags if isinstance(tags, list) else json.loads(tags) if isinstance(tags, str) else []
                    for tag in tag_list:
                        tag = tag.strip()
                        if not tag:
                            continue
                        nt = normalize_term(tag)
                        term_docs[nt].add(slug)
                        if nt not in term_meta:
                            term_meta[nt] = {"canonical": tag, "term_type": "TERM", "aliases": []}

                    # 3. Aliases as ALIAS
                    alias_list = aliases if isinstance(aliases, list) else json.loads(aliases) if isinstance(aliases, str) else []
                    for alias in alias_list:
                        alias = alias.strip()
                        if not alias:
                            continue
                        nt = normalize_term(alias)
                        term_docs[nt].add(slug)
                        if nt not in term_meta:
                            term_meta[nt] = {"canonical": alias, "term_type": "ALIAS", "aliases": []}

                print(f"Unique terms collected: {len(term_docs)}")

                # Compute IDF = log(N / df)
                terms_to_insert = []
                for normalized, slugs in term_docs.items():
                    df = len(slugs)
                    idf = round(math.log(N / df), 4) if df > 0 else 10.0
                    meta = term_meta.get(normalized, {"canonical": normalized, "term_type": "TERM", "aliases": []})
                    terms_to_insert.append((
                        DOMAIN,
                        meta["canonical"],
                        normalized,
                        json.dumps(meta.get("aliases", []), ensure_ascii=False),
                        meta["term_type"],
                        idf,
                    ))

                # Show top/bottom IDF examples
                terms_to_insert.sort(key=lambda x: x[5])
                print("\nLow IDF (common terms, top 10):")
                for t in terms_to_insert[:10]:
                    print(f"  {t[2]:30s}  IDF={t[5]:.4f}  canonical={t[1]}")
                print("\nHigh IDF (rare terms, top 10):")
                for t in terms_to_insert[-10:]:
                    print(f"  {t[2]:30s}  IDF={t[5]:.4f}  canonical={t[1]}")

                if dry_run:
                    print(f"\n[DRY RUN] Would insert {len(terms_to_insert)} terms")
                    return

                # Clear existing and insert
                cur.execute("DELETE FROM rag.term_lexicon WHERE domain = %s", (DOMAIN,))
                from psycopg2.extras import execute_values
                sql = """
                    INSERT INTO rag.term_lexicon (domain, canonical_term, normalized_term, aliases, term_type, idf_score)
                    VALUES %s
                    ON CONFLICT (domain, course_id, normalized_term) DO UPDATE SET
                        canonical_term = EXCLUDED.canonical_term,
                        idf_score = EXCLUDED.idf_score,
                        updated_at = now()
                """
                execute_values(cur, sql, terms_to_insert)
                print(f"\nInserted {len(terms_to_insert)} terms into rag.term_lexicon")

        print("\nDone.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
