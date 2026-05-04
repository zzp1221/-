"""
Batch-generate additional wiki .md pages to expand coverage to ~750 pages.
Each page includes authoritative source citations.
Reads JSON-backed topic definitions via knowledge.wiki_topics.
Usage: python expand_wiki.py [--dry-run]
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure python-agent is on sys.path for both direct and module execution
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared topic definitions
from knowledge.wiki_topics import TOPICS

WIKI_ROOT = Path(__file__).parent.parent.parent / "wiki"
DATE = "2026-05-02"


def build_md_content(title: str, course: str, chapter: str, difficulty: str,
                     tags: list, aliases: list, source: str,
                     sections: list, updated_at: str = DATE) -> str:
    """Build a full .md file from topic metadata and content sections."""
    fm_lines = ["---"]
    fm_lines.append(f'title: "{title}"')
    fm_lines.append(f"course: {course}")
    fm_lines.append(f"chapter: {chapter}")
    fm_lines.append(f"difficulty: {difficulty}")
    fm_lines.append(f"tags: [{', '.join(tags)}]")
    if aliases:
        fm_lines.append(f"aliases: [{', '.join(aliases)}]")
    fm_lines.append(f'source: "{source}"')
    fm_lines.append(f"updated_at: {updated_at}")
    fm_lines.append("---")
    fm_lines.append("")

    body_lines = []
    for heading, content in sections:
        body_lines.append(f"## {heading}")
        body_lines.append("")
        body_lines.append(content.strip())
        body_lines.append("")

    return "\n".join(fm_lines + body_lines)


def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print(f"Wiki Expansion -> {len(TOPICS)} new pages")
    print("=" * 60)

    created = 0
    skipped = 0
    for item in TOPICS:
        dir_name, file_stem, title, course, chapter, difficulty, tags, aliases, source, sections = item
        file_name = f"{file_stem}.md"

        target_dir = WIKI_ROOT / dir_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        if target_path.exists():
            skipped += 1
            continue

        content = build_md_content(title, course, chapter, difficulty, tags, aliases, source, sections)
        if not dry_run:
            target_path.write_text(content, encoding="utf-8")
        created += 1

    print(f"\nNew pages: {created}")
    print(f"Skipped (already exist): {skipped}")

    if dry_run:
        print("\n[Dry run — no files written]")
    else:
        total = len(list(WIKI_ROOT.rglob("*.md")))
        print(f"Wiki total after expansion: {total}")


if __name__ == "__main__":
    main()
