"""Tests for Criterion A: benchmark M/mixed coverage."""
from pathlib import Path
import json
import pytest

from pipeline.stage1.evaluation.criterion_a import compute_coverage, CoverageResult


def _ev(subset_class: str, protocols: list[str], mechanisms: list[str]) -> dict:
    return {
        "event_id": f"e-{subset_class}-{len(mechanisms)}",
        "subset_class": subset_class,
        "involved_protocols": protocols,
        "involved_mechanisms": mechanisms,
    }


def test_no_M_mixed_events_returns_one(tmp_path: Path):
    events = [_ev("B", ["X"], ["swap"])]
    db = {}
    tier_a_protocols = ["X"]
    res = compute_coverage(events, db, tier_a_protocols)
    assert res.total_relevant == 0
    assert res.coverage_ratio == 1.0


def test_full_coverage():
    events = [_ev("M", ["Aave V3"], ["share-asset-pricing"])]
    db = {
        "aave-v3": [{"tags": ["share-asset-pricing"], "id": "aave_v3.x"}]
    }
    res = compute_coverage(events, db, ["Aave V3"])
    assert res.covered == 1
    assert res.coverage_ratio == 1.0


def test_partial_coverage():
    events = [
        _ev("M", ["Aave V3"], ["share-asset-pricing"]),
        _ev("mixed", ["Curve Finance"], ["oracle-coupling"]),
    ]
    db = {
        "aave-v3": [{"tags": ["share-asset-pricing"], "id": "aave_v3.x"}]
    }
    res = compute_coverage(events, db, ["Aave V3", "Curve Finance"])
    assert res.covered == 1
    assert res.total_relevant == 2
    assert res.coverage_ratio == 0.5


def test_event_outside_tier_a_excluded():
    events = [_ev("M", ["NotInTierA"], ["share-asset-pricing"])]
    db = {}
    res = compute_coverage(events, db, ["Aave V3"])
    assert res.total_relevant == 0
