"""Validate benchmark event JSON files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "benchmark" / "benchmark-event.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate benchmark events")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    seen_tx: dict[str, Path] = {}

    for p in args.paths:
        files = sorted(p.rglob("*.json")) if p.is_dir() else [p]
        for f in files:
            data = json.loads(f.read_text())
            for e in validator.iter_errors(data):
                loc = "/".join(map(str, e.path)) or "<root>"
                errors.append(f"{f}: {loc}: {e.message}")
            # Cross-file uniqueness
            eid = data.get("event_id")
            if eid and eid in seen_ids:
                errors.append(f"{f}: duplicate event_id '{eid}' (also in {seen_ids[eid]})")
            elif eid:
                seen_ids[eid] = f
            tx = data.get("tx_hash")
            if tx and tx in seen_tx:
                errors.append(f"{f}: duplicate tx_hash '{tx}' (also in {seen_tx[tx]})")
            elif tx:
                seen_tx[tx] = f
            # M/mixed must have rationale
            if data.get("subset_class") in {"M", "mixed"} and not data.get("classification_rationale"):
                errors.append(
                    f"{f}: subset_class is '{data['subset_class']}' but classification_rationale is empty"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK ({len(seen_ids)} events validated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
