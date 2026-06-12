"""Validate protocol metadata JSON files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "corpus" / "protocol-metadata.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate protocol metadata JSON files")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    errors: list[str] = []
    for p in args.paths:
        files = sorted(p.rglob("metadata.json")) if p.is_dir() else [p]
        for f in files:
            data = json.loads(f.read_text())
            for e in validator.iter_errors(data):
                loc = "/".join(map(str, e.path)) or "<root>"
                errors.append(f"{f}: {loc}: {e.message}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
