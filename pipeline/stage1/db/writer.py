"""Atomic 3-file writer for mechanism DB entries (spec §10 rule 10)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import jsonschema

from pipeline.stage1.config import IR_SCHEMA_PATH, SIDECAR_SCHEMA_PATH


class DBWriteError(Exception):
    pass


def _load_validator(schema_path: Path) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(json.loads(schema_path.read_text()))


def write_mechanism(
    *,
    ir: dict,
    metrics: dict,
    poc_source: str,
    db_root: Path,
    protocol_slug: str,
) -> Path:
    """Write IR JSON, PoC .t.sol, and metrics JSON atomically.

    All-or-nothing: if any pre-write validation fails, no files are written.
    Returns the mechanism's directory.
    """
    if ir["id"] != metrics["mechanism_id"]:
        raise DBWriteError(
            f"id mismatch: ir.id={ir['id']} metrics.mechanism_id={metrics['mechanism_id']}"
        )

    ir_validator = _load_validator(IR_SCHEMA_PATH)
    metrics_validator = _load_validator(SIDECAR_SCHEMA_PATH)

    ir_errs = list(ir_validator.iter_errors(ir))
    if ir_errs:
        raise DBWriteError(f"IR schema invalid: {[e.message for e in ir_errs[:3]]}")

    m_errs = list(metrics_validator.iter_errors(metrics))
    if m_errs:
        raise DBWriteError(f"metrics schema invalid: {[e.message for e in m_errs[:3]]}")

    chain = ir["chain"]
    mech_id = ir["id"]
    target_dir = db_root / chain / protocol_slug / mech_id
    target_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = [
        (target_dir / f"{mech_id}.json", json.dumps(ir, indent=2)),
        (target_dir / f"{mech_id}.t.sol", poc_source),
        (target_dir / f"{mech_id}.metrics.json", json.dumps(metrics, indent=2)),
    ]
    tmp_paths: list = []
    try:
        for final, content in files_to_write:
            fd, tmp_name = tempfile.mkstemp(dir=str(target_dir), prefix=".tmp_", text=True)
            tmp_path = Path(tmp_name)
            with open(fd, "w") as f:
                f.write(content)
            tmp_paths.append((tmp_path, final))
        for tmp_path, final in tmp_paths:
            tmp_path.replace(final)
        return target_dir
    except Exception as e:
        for tmp_path, _ in tmp_paths:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        raise DBWriteError(f"write failed: {e}") from e
