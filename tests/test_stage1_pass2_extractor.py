"""Tests for Pass 2 deep extraction."""
import json
from unittest.mock import MagicMock
import pytest

from pipeline.stage1.pass2.extractor import extract_ir
from pipeline.stage1.pass2.tool_registry import ToolRegistry
from pipeline.stage1.pass1.stub import Stub


def _stub() -> Stub:
    return Stub(
        stub_id="aave_v3.flash_loan_simple",
        chain="ethereum",
        trigger_kind="function-call",
        entry_point="Pool.flashLoanSimple",
        state_reads_coarse=["reserves"],
        state_writes_coarse=["fees"],
        candidate_tags=["function-callable"],
    )


def test_valid_ir_returned(ir_schema):
    fake_ir = {
        "id": "aave_v3.flash_loan_simple",
        "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "Pool.flashLoanSimple"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "y", "status": "draft"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "L1"}],
    }
    llm = MagicMock()
    llm.complete.return_value = "```json\n" + json.dumps(fake_ir) + "\n```"
    reg = ToolRegistry()
    ir, attempts = extract_ir(
        llm_client=llm, stub=_stub(), tool_registry=reg,
        source_blob="", docs_blob="", ir_schema=ir_schema,
    )
    assert ir is not None
    assert ir["id"] == "aave_v3.flash_loan_simple"
    assert attempts == 1


def test_invalid_ir_retried(ir_schema):
    bad = json.dumps({"id": "Bad"})
    good = json.dumps({
        "id": "aave_v3.flash_loan_simple", "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "X.f"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "y", "status": "draft"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "L1"}],
    })
    llm = MagicMock()
    llm.complete.side_effect = ["```json\n" + bad + "\n```", "```json\n" + good + "\n```"]
    reg = ToolRegistry()
    ir, attempts = extract_ir(
        llm_client=llm, stub=_stub(), tool_registry=reg,
        source_blob="", docs_blob="", ir_schema=ir_schema,
    )
    assert ir is not None
    assert attempts == 2


def test_three_failures_returns_none(ir_schema):
    llm = MagicMock()
    llm.complete.return_value = "not valid json"
    reg = ToolRegistry()
    ir, attempts = extract_ir(
        llm_client=llm, stub=_stub(), tool_registry=reg,
        source_blob="", docs_blob="", ir_schema=ir_schema,
    )
    assert ir is None
    assert attempts == 3


def test_static_analysis_context_injected(ir_schema):
    """gather()'s prompt block must reach the Pass 2 user message."""
    class FakeCtx:
        def to_prompt_block(self):
            return "=== MISSING-REQUIRE DETECTOR ===\n[{\"fn\": \"deposit\"}]"

    class FakeReg:
        def gather(self, source_path):
            return FakeCtx()

    llm = MagicMock()
    llm.complete.return_value = "not valid json"
    extract_ir(
        llm_client=llm, stub=_stub(), tool_registry=FakeReg(),
        source_blob="SRC", docs_blob="DOCS", ir_schema=ir_schema,
    )
    sent = llm.complete.call_args.kwargs["messages"][0].content
    assert "STATIC ANALYSIS CONTEXT" in sent
    assert "MISSING-REQUIRE DETECTOR" in sent
