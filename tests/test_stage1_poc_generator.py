"""Tests for PoC generator (template selection + LLM fill)."""
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from pipeline.stage1.poc.generator import generate_poc, _pick_template


def test_pick_template_validation_gap():
    p = _pick_template(["function-callable", "validation-gap"])
    assert p.name == "validation-gap.t.sol.template"


def test_pick_template_falls_back_to_function_callable():
    p = _pick_template(["function-callable"])
    assert p.name == "function-callable.t.sol.template"


def test_pick_template_share_asset_priority():
    p = _pick_template(["function-callable", "share-asset-pricing", "oracle-coupling"])
    assert p.name == "share-asset-pricing.t.sol.template"


def test_generate_strips_markdown_fences():
    llm = MagicMock()
    llm.complete.return_value = "```solidity\ncontract X {}\n```"
    ir = {
        "id": "x.y", "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "X.f"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "y", "status": "draft"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "1"}],
    }
    out = generate_poc(llm_client=llm, ir=ir, source_blob="")
    assert out.startswith("contract X")
    assert "```" not in out
