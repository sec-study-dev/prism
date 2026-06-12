"""Load mechanism-db meta-IR JSON files (Stage 2 input)."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from pipeline.stage1.config import IR_SCHEMA_PATH


class LoadError(Exception):
    pass


def load_mechanisms(db_root: Path) -> list[dict]:
    if not db_root.exists():
        return []
    validator = jsonschema.Draft202012Validator(json.loads(IR_SCHEMA_PATH.read_text()))
    out: list[dict] = []
    for f in sorted(db_root.rglob("*.json")):
        if f.name.endswith(".metrics.json"):
            continue
        try:
            ir = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            raise LoadError(f"{f}: malformed JSON: {e}") from e
        errs = list(validator.iter_errors(ir))
        if errs:
            raise LoadError(f"{f}: invalid IR: {errs[0].message}")
        out.append(ir)
    out.sort(key=lambda m: m["id"])
    return out
