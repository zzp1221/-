"""Populate rag.synonym_group from wiki page aliases.

Usage:
  python knowledge/populate_synonym_groups.py
  python knowledge/populate_synonym_groups.py --dry-run
"""
from __future__ import annotations

import json
import sys

import psycopg2
from psycopg2.extras import execute_values

from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()
DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
DOMAIN = RUNTIME_CONFIG.retrieval_domain


def connect():
    return psycopg2.connect(**DB_CONFIG)


def decode_aliases(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value.strip()] if value.strip() else []
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("Populate rag.synonym_group from wiki aliases")
    print("=" * 60)

    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT title, aliases
                    FROM rag.wiki_page
                    WHERE is_active = true AND domain = %s
                """, (DOMAIN,))
                rows = cur.fetchall()

                groups = []
                for title, aliases in rows:
                    variants = [
                        alias for alias in decode_aliases(aliases)
                        if alias and alias.strip() and alias.strip() != title
                    ]
                    unique_variants = list(dict.fromkeys(variants))
                    if not unique_variants:
                        continue
                    groups.append(
                        (
                            DOMAIN,
                            title,
                            json.dumps(unique_variants, ensure_ascii=False),
                            "WIKI_FILTERED",
                        )
                    )

                print(f"Prepared synonym groups: {len(groups)}")
                if groups[:5]:
                    print("Examples:")
                    for domain, canonical, variants, _ in groups[:5]:
                        print(f"  {canonical} -> {variants}")

                if dry_run:
                    print("\n[DRY RUN] Skip database write")
                    return

                cur.execute(
                    "DELETE FROM rag.synonym_group WHERE domain = %s AND course_id IS NULL",
                    (DOMAIN,),
                )
                execute_values(
                    cur,
                    """
                    INSERT INTO rag.synonym_group (
                        domain, canonical_term, variants, source_kind
                    ) VALUES %s
                    """,
                    groups,
                )
                print(f"Inserted synonym groups: {len(groups)}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
