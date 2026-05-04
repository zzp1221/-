"""
Run all batch4 import scripts in sequence.
Part 4 (VIDEO) is a Python file; Parts 1-3 are JSON files.
"""
import sys, json, os, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from knowledge.import_pipeline import run_import


def load_json_batch(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    dry = "--dry-run" in sys.argv
    base = os.path.dirname(__file__)

    batches = []

    # Part 4: VIDEO (Python file)
    part4_py = os.path.join(base, "import_batch4_part4.py")
    if os.path.exists(part4_py):
        batches.append(("part4_video", "python", part4_py))

    # Parts 1-3: JSON files
    for name in ["batch4_part1", "batch4_part2", "batch4_part3"]:
        json_path = os.path.join(base, f"{name}.json")
        if os.path.exists(json_path):
            batches.append((name, "json", json_path))

    print(f"Found {len(batches)} batches to process")
    total = 0

    for label, kind, path in batches:
        print(f"\n{'='*60}")
        print(f"Processing: {label} ({kind})")

        if kind == "json":
            resources = load_json_batch(path)
            print(f"  Loaded {len(resources)} resources")
            if not dry:
                run_import(resources, label)
            else:
                types = {}
                for r in resources:
                    t = r["type"]
                    types[t] = types.get(t, 0) + 1
                print(f"  Types: {types}")
            total += len(resources)

        elif kind == "python":
            # Import and run the Python batch file
            if dry:
                # Just count resources
                import importlib.util
                spec = importlib.util.spec_from_file_location("batch", path)
                mod = importlib.util.module_from_spec(spec)
                # We can't easily exec without running, so just parse
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                count = content.count("RESOURCES.append(")
                print(f"  Contains {count} resources (dry run, not executing Python)")
                total += count
            else:
                result = subprocess.run(
                    [sys.executable, path],
                    capture_output=False, text=True, timeout=3600
                )
                if result.returncode != 0:
                    print(f"  ERROR: {label} exited with code {result.returncode}")
                else:
                    print(f"  {label} completed successfully")

    print(f"\n{'='*60}")
    print(f"Total resources processed: {total}")
    print(f"Expected final count: {100 + total} (100 existing + {total} new)")


if __name__ == "__main__":
    main()
