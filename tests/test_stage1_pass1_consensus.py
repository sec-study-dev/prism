"""Tests for 3-subagent consensus protocol."""
from unittest.mock import MagicMock
import json
import pytest

from pipeline.stage1.pass1.consensus import (
    run_consensus, ConsensusResult, _stub_key,
)
from pipeline.stage1.pass1.stub import Stub


def _stub(sid: str, tags: list[str] = None) -> Stub:
    return Stub(
        stub_id=sid,
        chain="ethereum",
        trigger_kind="function-call",
        entry_point=f"{sid.split('.')[1]}.fn",
        state_reads_coarse=[],
        state_writes_coarse=[],
        candidate_tags=tags or ["function-callable"],
    )


def _fake_discover(returns_by_persona: dict[str, list[Stub]]):
    def _impl(*, persona_prompt: str, **kwargs):
        if "auditor" in persona_prompt.lower():
            return returns_by_persona.get("A", [])
        if "architect" in persona_prompt.lower():
            return returns_by_persona.get("B", [])
        if "developer" in persona_prompt.lower():
            return returns_by_persona.get("C", [])
        return []
    return _impl


def test_unanimous_all_three_agree(monkeypatch):
    stubs_A = [_stub("aave_v3.flash_loan")]
    stubs_B = [_stub("aave_v3.flash_loan")]
    stubs_C = [_stub("aave_v3.flash_loan")]
    monkeypatch.setattr(
        "pipeline.stage1.pass1.consensus.discover_stubs",
        _fake_discover({"A": stubs_A, "B": stubs_B, "C": stubs_C}),
    )
    res = run_consensus(
        llm_client=MagicMock(),
        protocol_name="Aave V3",
        protocol_chain="ethereum",
        source_blob="",
        docs_blob="",
    )
    assert len(res.stubs) == 1
    assert res.consensus_levels[_stub_key(stubs_A[0])] == "unanimous-3of3"
    assert res.rounds == 0


def test_majority_two_of_three(monkeypatch):
    stubs_A = [_stub("aave_v3.fl")]
    stubs_B = [_stub("aave_v3.fl")]
    stubs_C = []
    monkeypatch.setattr(
        "pipeline.stage1.pass1.consensus.discover_stubs",
        _fake_discover({"A": stubs_A, "B": stubs_B, "C": stubs_C}),
    )
    res = run_consensus(
        llm_client=MagicMock(),
        protocol_name="Aave V3",
        protocol_chain="ethereum",
        source_blob="",
        docs_blob="",
        max_rounds=5,
    )
    assert len(res.stubs) == 1
    assert res.consensus_levels[_stub_key(stubs_A[0])] == "majority-2of3"


def test_stub_key_normalization():
    s1 = _stub("aave_v3.flash_loan_simple")
    s2 = _stub("aave_v3.flash_loan_simple")
    assert _stub_key(s1) == _stub_key(s2)
