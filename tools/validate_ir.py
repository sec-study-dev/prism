"""Validate one or more IR JSON files against meta-ir.schema.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "ir-schema" / "meta-ir.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_file(path: Path, validator: jsonschema.Draft202012Validator) -> list[str]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: invalid JSON: {e}"]
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    return [f"{path}: {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IR JSON files")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)

    all_errors: list[str] = []
    for p in args.paths:
        if p.is_dir():
            files = sorted(p.rglob("*.json"))
        else:
            files = [p]
        for f in files:
            all_errors.extend(validate_file(f, validator))

    if all_errors:
        print("\n".join(all_errors), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
