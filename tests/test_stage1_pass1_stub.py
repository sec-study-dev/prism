"""Tests for Pass 1 stub data structure."""
import json
import pytest

from pipeline.stage1.pass1.stub import Stub, parse_stub_json, StubValidationError


def test_stub_required_fields():
    s = Stub(
        stub_id="aave_v3.flash_loan_simple",
        chain="ethereum",
        trigger_kind="function-call",
        entry_point="Pool.flashLoanSimple",
        state_reads_coarse=["reserves"],
        state_writes_coarse=["fees"],
        candidate_tags=["function-callable"],
    )
    assert s.stub_id == "aave_v3.flash_loan_simple"


def test_stub_id_pattern_enforced():
    with pytest.raises(StubValidationError, match="stub_id"):
        Stub(
            stub_id="NoDotInId",
            chain="ethereum",
            trigger_kind="function-call",
            entry_point="X.f",
            state_reads_coarse=[],
            state_writes_coarse=[],
            candidate_tags=["function-callable"],
        )


def test_stub_invalid_chain_rejected():
    with pytest.raises(StubValidationError, match="chain"):
        Stub(
            stub_id="x.y",
            chain="solana",
            trigger_kind="function-call",
            entry_point="X.f",
            state_reads_coarse=[],
            state_writes_coarse=[],
            candidate_tags=["function-callable"],
        )


def test_stub_invalid_trigger_kind():
    with pytest.raises(StubValidationError, match="trigger_kind"):
        Stub(
            stub_id="x.y",
            chain="ethereum",
            trigger_kind="banana",
            entry_point="X.f",
            state_reads_coarse=[],
            state_writes_coarse=[],
            candidate_tags=["function-callable"],
        )


def test_stub_to_json_roundtrip():
    s = Stub(
        stub_id="aave_v3.flash_loan_simple",
        chain="ethereum",
        trigger_kind="function-call",
        entry_point="Pool.flashLoanSimple",
        state_reads_coarse=["reserves"],
        state_writes_coarse=["fees"],
        candidate_tags=["function-callable", "validation-gap"],
    )
    j = s.to_json()
    s2 = parse_stub_json(json.dumps(j))
    assert s2.stub_id == s.stub_id
    assert s2.candidate_tags == s.candidate_tags


def test_parse_stub_json_handles_missing_fields():
    with pytest.raises(StubValidationError):
        parse_stub_json('{"stub_id": "x.y"}')
