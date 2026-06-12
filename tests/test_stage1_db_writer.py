"""Tests for atomic DB writer (3-file unit)."""
import json
from pathlib import Path
import pytest

from pipeline.stage1.db.writer import write_mechanism, DBWriteError


@pytest.fixture
def ir() -> dict:
    return {
        "id": "aave_v3.flash_loan_simple",
        "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "Pool.flashLoanSimple"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "test_flash_loan_simple", "status": "passing"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "1"}],
    }


@pytest.fixture
def metrics() -> dict:
    return {
        "mechanism_id": "aave_v3.flash_loan_simple",
        "consensus_level": "unanimous-3of3",
        "consensus_rounds": 0,
        "subagent_proposals": {"A": "p1", "B": "p2", "C": "p3"},
        "extraction_pass": 2, "pass2_attempts": 1, "poc_attempts": 1,
        "flagged_reasons": ["non-function-callable-tag"],
        "provenance_quality": "doc-and-code-consistent",
        "extraction_pipeline_version": "stage1-v1.0",
        "extracted_at": "2026-05-26T12:00:00Z",
    }


def test_writes_three_files(tmp_path: Path, ir, metrics):
    write_mechanism(
        ir=ir, metrics=metrics, poc_source="contract X {}",
        db_root=tmp_path, protocol_slug="aave-v3",
    )
    base = tmp_path / "ethereum" / "aave-v3" / "aave_v3.flash_loan_simple"
    assert (base / "aave_v3.flash_loan_simple.json").exists()
    assert (base / "aave_v3.flash_loan_simple.t.sol").exists()
    assert (base / "aave_v3.flash_loan_simple.metrics.json").exists()


def test_atomic_rollback_on_metrics_validation_fail(tmp_path: Path, ir, metrics):
    metrics["consensus_level"] = "invalid"
    with pytest.raises(DBWriteError):
        write_mechanism(
            ir=ir, metrics=metrics, poc_source="contract X {}",
            db_root=tmp_path, protocol_slug="aave-v3",
        )
    base = tmp_path / "ethereum" / "aave-v3" / "aave_v3.flash_loan_simple"
    assert not (base / "aave_v3.flash_loan_simple.json").exists()
    assert not (base / "aave_v3.flash_loan_simple.t.sol").exists()


def test_ir_id_mismatch_rejected(tmp_path: Path, ir, metrics):
    metrics["mechanism_id"] = "different.id"
    with pytest.raises(DBWriteError, match="id mismatch"):
        write_mechanism(
            ir=ir, metrics=metrics, poc_source="contract X {}",
            db_root=tmp_path, protocol_slug="aave-v3",
        )
