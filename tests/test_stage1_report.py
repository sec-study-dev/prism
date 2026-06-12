"""Tests for the evaluation report builder."""
import json
from pathlib import Path
import pytest

from pipeline.stage1.evaluation.report import build_report, _load_db


def test_load_db_empty_when_missing(tmp_path: Path):
    missing = tmp_path / "does-not-exist"
    db = _load_db(missing)
    assert db == {}


def test_load_db_reads_ir_with_sibling_sol(tmp_path: Path):
    mech_dir = tmp_path / "ethereum" / "aave-v3" / "aave_v3.flash"
    mech_dir.mkdir(parents=True)
    (mech_dir / "aave_v3.flash.json").write_text(json.dumps({"id": "aave_v3.flash", "tags": ["function-callable"]}))
    (mech_dir / "aave_v3.flash.t.sol").write_text("contract X {}")
    (mech_dir / "aave_v3.flash.metrics.json").write_text(json.dumps({"mechanism_id": "aave_v3.flash"}))
    db = _load_db(tmp_path)
    assert "aave-v3" in db
    assert len(db["aave-v3"]) == 1
    assert db["aave-v3"][0]["id"] == "aave_v3.flash"


def test_load_db_skips_metrics_json(tmp_path: Path):
    mech_dir = tmp_path / "ethereum" / "aave-v3" / "aave_v3.flash"
    mech_dir.mkdir(parents=True)
    (mech_dir / "aave_v3.flash.json").write_text(json.dumps({"id": "aave_v3.flash", "tags": []}))
    (mech_dir / "aave_v3.flash.t.sol").write_text("contract X {}")
    (mech_dir / "aave_v3.flash.metrics.json").write_text(json.dumps({"mechanism_id": "aave_v3.flash"}))
    db = _load_db(tmp_path)
    # Only 1 IR, metrics.json not counted as a mechanism
    assert len(db["aave-v3"]) == 1


def test_build_report_empty_db(tmp_path: Path):
    out = tmp_path / "report.md"
    summary = build_report(
        db_root=tmp_path / "empty",
        benchmark_events=[
            {"event_id": "e1", "subset_class": "M",
             "involved_protocols": ["Aave V3"], "involved_mechanisms": ["share-asset-pricing"]}
        ],
        tier_a_protocol_names=["Aave V3"],
        gold_paths={},
        audit_form_pass_rate=None,
        output_path=out,
    )
    assert out.exists()
    # 1 relevant M event, 0 covered (empty DB)
    assert summary["criterion_a"]["total"] == 1
    assert summary["criterion_a"]["covered"] == 0
    assert summary["criterion_a"]["passes"] is False
    assert summary["criterion_c"]["passes"] is False
