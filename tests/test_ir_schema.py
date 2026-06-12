"""Tests for the meta-IR JSON Schema."""
import json
from pathlib import Path

import jsonschema
import pytest


def test_schema_file_exists(ir_schema_path: Path):
    assert ir_schema_path.exists(), f"schema not found at {ir_schema_path}"


def test_schema_is_valid_json_schema(ir_schema: dict):
    """The schema document itself must be a valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(ir_schema)


def test_schema_declares_required_top_level_fields(ir_schema: dict):
    required = set(ir_schema.get("required", []))
    expected = {
        "id", "chain", "trigger",
        "state_reads", "state_writes",
        "preconditions", "postconditions",
        "invariants_held", "invariants_at_risk",
        "deps", "tags", "poc", "provenance",
    }
    assert required == expected


@pytest.fixture(scope="session")
def valid_examples_dir(repo_root: Path) -> Path:
    return repo_root / "ir-schema" / "examples"


@pytest.fixture(scope="session")
def invalid_examples_dir(repo_root: Path) -> Path:
    return repo_root / "ir-schema" / "invalid-examples"


def _load_json_files(directory: Path) -> list[tuple[str, dict]]:
    return [(p.name, json.loads(p.read_text())) for p in sorted(directory.glob("*.json"))]


def test_at_least_five_valid_examples_exist(valid_examples_dir: Path):
    files = list(valid_examples_dir.glob("*.json"))
    assert len(files) >= 5, f"expected ≥5 examples, found {len(files)}"


def test_all_valid_examples_pass_schema(ir_schema: dict, valid_examples_dir: Path):
    validator = jsonschema.Draft202012Validator(ir_schema)
    for name, data in _load_json_files(valid_examples_dir):
        errors = list(validator.iter_errors(data))
        assert not errors, f"{name}: {[e.message for e in errors]}"


def test_invalid_examples_are_rejected(ir_schema: dict, invalid_examples_dir: Path):
    validator = jsonschema.Draft202012Validator(ir_schema)
    files = _load_json_files(invalid_examples_dir)
    assert len(files) >= 3, "need at least 3 invalid examples to test rejection"
    for name, data in files:
        errors = list(validator.iter_errors(data))
        assert errors, f"{name}: expected schema rejection but it passed"
