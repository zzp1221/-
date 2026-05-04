"""
Generic batch loader: reads resource JSON files and runs the import pipeline.
Usage: python knowledge/load_batch.py knowledge/batch4_part1.json
"""
import sys, json
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.import_pipeline import run_import


def main():
    if len(sys.argv) < 2:
        print("Usage: python knowledge/load_batch.py <json_file> [--dry-run]")
        sys.exit(1)

    json_path = sys.argv[1]
    label = Path(json_path).stem

    with open(json_path, "r", encoding="utf-8") as f:
        resources = json.load(f)

    print(f"Loaded {len(resources)} resources from {json_path}")
    run_import(resources, label)


if __name__ == "__main__":
    main()
