"""Tests for Pass 1 single-subagent discovery."""
import json
from unittest.mock import MagicMock
import pytest

from pipeline.stage1.pass1.discovery import discover_stubs
from pipeline.stage1.pass1.stub import Stub
from pipeline.stage1.llm.budget import BudgetTracker


def _fake_llm(returns: str):
    client = MagicMock()
    client.complete.return_value = returns
    return client


def test_discover_returns_parsed_stubs():
    fake_stubs = json.dumps([
        {
            "stub_id": "aave_v3.flash_loan_simple",
            "chain": "ethereum",
            "trigger_kind": "function-call",
            "entry_point": "Pool.flashLoanSimple",
            "state_reads_coarse": ["reserves"],
            "state_writes_coarse": ["fees"],
            "candidate_tags": ["function-callable"]
        }
    ])
    llm = _fake_llm(fake_stubs)
    stubs = discover_stubs(
        llm_client=llm,
        persona_prompt="auditor persona",
        protocol_name="Aave V3",
        protocol_chain="ethereum",
        source_blob="contract X {}",
        docs_blob="docs",
    )
    assert len(stubs) == 1
    assert stubs[0].stub_id == "aave_v3.flash_loan_simple"


def test_discover_skips_invalid_stubs():
    bad = json.dumps([
        {"stub_id": "Bad", "chain": "ethereum"},
        {"stub_id": "good.x", "chain": "ethereum", "trigger_kind": "function-call",
         "entry_point": "X.f", "state_reads_coarse": [], "state_writes_coarse": [],
         "candidate_tags": ["function-callable"]},
    ])
    llm = _fake_llm(bad)
    stubs = discover_stubs(
        llm_client=llm,
        persona_prompt="x",
        protocol_name="X",
        protocol_chain="ethereum",
        source_blob="",
        docs_blob="",
    )
    assert len(stubs) == 1
    assert stubs[0].stub_id == "good.x"


def test_discover_handles_non_json_response():
    llm = _fake_llm("not json at all")
    stubs = discover_stubs(
        llm_client=llm,
        persona_prompt="x",
        protocol_name="X",
        protocol_chain="ethereum",
        source_blob="",
        docs_blob="",
    )
    assert stubs == []


def test_discover_extracts_json_block_from_markdown():
    response = (
        'Here are the stubs:\n\n'
        '```json\n'
        '[\n'
        '  {"stub_id": "x.y", "chain": "ethereum", "trigger_kind": "function-call",\n'
        '   "entry_point": "X.y", "state_reads_coarse": [], "state_writes_coarse": [],\n'
        '   "candidate_tags": ["function-callable"]}\n'
        ']\n'
        '```\n\n'
        'Hope this helps!'
    )
    llm = _fake_llm(response)
    stubs = discover_stubs(
        llm_client=llm,
        persona_prompt="x",
        protocol_name="X",
        protocol_chain="ethereum",
        source_blob="",
        docs_blob="",
    )
    assert len(stubs) == 1
