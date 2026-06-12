"""Tests for Criterion C: sample audit tooling."""
import json
from pathlib import Path
import pytest

from pipeline.stage1.evaluation.criterion_c import (
    sample_audit_items, AuditItem, render_audit_form, compute_audit_pass_rate
)


def test_sample_3_per_protocol(tmp_path: Path):
    for proto in ["proto1", "proto2"]:
        for i in range(5):
            d = tmp_path / "ethereum" / proto / f"{proto}.m{i}"
            d.mkdir(parents=True)
            (d / f"{proto}.m{i}.json").write_text(json.dumps({"id": f"{proto}.m{i}", "tags": ["function-callable"]}))

    items = sample_audit_items(db_root=tmp_path, exclude_protocols={"gold-protocol"}, k_per_protocol=3, seed=42)
    assert len(items) == 6
    for it in items:
        assert it.mechanism_id.startswith("proto")


def test_exclude_gold_protocols(tmp_path: Path):
    for proto in ["proto1", "gold-protocol"]:
        for i in range(3):
            d = tmp_path / "ethereum" / proto / f"{proto}.m{i}"
            d.mkdir(parents=True)
            (d / f"{proto}.m{i}.json").write_text(json.dumps({"id": f"{proto}.m{i}", "tags": ["x"]}))
    items = sample_audit_items(db_root=tmp_path, exclude_protocols={"gold-protocol"}, k_per_protocol=2, seed=42)
    assert all("gold-protocol" not in it.protocol_slug for it in items)


def test_pass_rate_computation():
    items = [
        AuditItem(protocol_slug="p1", chain="ethereum", mechanism_id="p1.m1",
                  ir_path=None, sol_path=None, metrics_path=None, judgment=None),
    ]
    items[0].judgment = "real"
    items.append(AuditItem("p1", "ethereum", "p1.m2", None, None, None, "real"))
    items.append(AuditItem("p1", "ethereum", "p1.m3", None, None, None, "false-positive"))
    rate = compute_audit_pass_rate(items)
    assert abs(rate - 2/3) < 1e-9


def test_render_form_produces_markdown(tmp_path: Path):
    item = AuditItem("p1", "ethereum", "p1.m1",
                     tmp_path / "ir.json", tmp_path / "p.sol", tmp_path / "m.json", None)
    md = render_audit_form([item], output_path=tmp_path / "audit.md")
    assert "p1.m1" in md
    assert "real / false-positive" in md.lower() or "real / false" in md
