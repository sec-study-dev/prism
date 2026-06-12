"""Tests for the sidecar-metrics JSON Schema."""
import json
from pathlib import Path

import jsonschema
import pytest


@pytest.fixture(scope="session")
def sidecar_schema_path(repo_root: Path) -> Path:
    return repo_root / "ir-schema" / "sidecar-metrics.schema.json"


@pytest.fixture(scope="session")
def sidecar_schema(sidecar_schema_path: Path) -> dict:
    return json.loads(sidecar_schema_path.read_text())


def test_sidecar_schema_exists(sidecar_schema_path: Path):
    assert sidecar_schema_path.exists()


def test_sidecar_schema_is_valid(sidecar_schema: dict):
    jsonschema.Draft202012Validator.check_schema(sidecar_schema)


@pytest.fixture
def good_metrics() -> dict:
    return {
        "mechanism_id": "uniswap_v4.swap_with_hook",
        "consensus_level": "unanimous-3of3",
        "consensus_rounds": 0,
        "subagent_proposals": {"A": "x", "B": "y", "C": "z"},
        "extraction_pass": 2,
        "pass2_attempts": 1,
        "poc_attempts": 1,
        "flagged_reasons": ["non-function-callable-tag"],
        "provenance_quality": "doc-and-code-consistent",
        "extraction_pipeline_version": "stage1-v1.0",
        "extracted_at": "2026-05-26T12:00:00Z"
    }


def test_good_metrics_validates(sidecar_schema, good_metrics):
    jsonschema.validate(good_metrics, sidecar_schema)


def test_bad_id_rejected(sidecar_schema, good_metrics):
    good_metrics["mechanism_id"] = "NoDot"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_metrics, sidecar_schema)


def test_consensus_rounds_max_5(sidecar_schema, good_metrics):
    good_metrics["consensus_rounds"] = 6
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_metrics, sidecar_schema)


def test_unknown_flag_reason_rejected(sidecar_schema, good_metrics):
    good_metrics["flagged_reasons"] = ["invalid-reason"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_metrics, sidecar_schema)


def test_empty_flag_reasons_rejected(sidecar_schema, good_metrics):
    good_metrics["flagged_reasons"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_metrics, sidecar_schema)


def test_extraction_pass_one_rejected(sidecar_schema, good_metrics):
    good_metrics["extraction_pass"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_metrics, sidecar_schema)
