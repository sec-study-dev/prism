"""Check that all tags used in IR JSON files are declared in seed-tags.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_TAGS_PATH = REPO_ROOT / "ir-schema" / "seed-tags.md"
TAG_HEADING_RE = re.compile(r"^####\s+`([a-z][a-z0-9-]*)`", re.MULTILINE)


def load_seed_tags() -> set[str]:
    return set(TAG_HEADING_RE.findall(SEED_TAGS_PATH.read_text()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify IR tag coverage")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    seed = load_seed_tags()
    used: dict[str, set[str]] = {}

    for p in args.paths:
        files = sorted(p.rglob("*.json")) if p.is_dir() else [p]
        for f in files:
            data = json.loads(f.read_text())
            for tag in data.get("tags", []):
                used.setdefault(tag, set()).add(str(f))

    unknown = {t: paths for t, paths in used.items() if t not in seed}
    if unknown:
        for t, paths in sorted(unknown.items()):
            print(f"UNKNOWN TAG '{t}' used in:", file=sys.stderr)
            for path in sorted(paths):
                print(f"  {path}", file=sys.stderr)
        return 1
    print(f"OK ({len(used)} tag(s) used, all declared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
