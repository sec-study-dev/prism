"""Tests for the 4-OR-rule Flagger."""
from pathlib import Path
import json
import pytest

from pipeline.stage1.flagger import Flagger, FlagDecision
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


def test_flags_non_function_callable_tag():
    f = Flagger(benchmark_events=[], cross_protocol_calls=set(), incident_protocols=set())
    s = _stub("aave_v3.flash_loan", tags=["function-callable", "validation-gap"])
    d = f.flag(s)
    assert d.flagged is True
    assert "non-function-callable-tag" in d.reasons


def test_does_not_flag_pure_function_callable():
    f = Flagger(benchmark_events=[], cross_protocol_calls=set(), incident_protocols=set())
    s = _stub("aave_v3.dummy", tags=["function-callable"])
    d = f.flag(s)
    assert d.flagged is False


def test_flags_cross_tier_a_called():
    f = Flagger(
        benchmark_events=[],
        cross_protocol_calls={"aave_v3.flash_loan"},
        incident_protocols=set(),
    )
    s = _stub("aave_v3.flash_loan", tags=["function-callable"])
    d = f.flag(s)
    assert d.flagged is True
    assert "cross-tier-a-called" in d.reasons


def test_flags_benchmark_related():
    benchmark_events = [
        {"involved_protocols": ["Aave V3", "Uniswap V3"], "subset_class": "M",
         "involved_mechanisms": ["share-asset-pricing"]}
    ]
    f = Flagger(benchmark_events=benchmark_events, cross_protocol_calls=set(),
                incident_protocols=set())
    s = _stub("aave_v3.borrow", tags=["function-callable"])
    d = f.flag(s, protocol_name="Aave V3")
    assert d.flagged is True
    assert "benchmark-related" in d.reasons


def test_flags_historical_incident():
    f = Flagger(benchmark_events=[], cross_protocol_calls=set(),
                incident_protocols={"Aave V3"})
    s = _stub("aave_v3.borrow")
    d = f.flag(s, protocol_name="Aave V3")
    assert d.flagged is True
    assert "historical-incident" in d.reasons


def test_multiple_reasons_accumulated():
    f = Flagger(benchmark_events=[], cross_protocol_calls={"aave_v3.fl"},
                incident_protocols={"Aave V3"})
    s = _stub("aave_v3.fl", tags=["function-callable", "validation-gap"])
    d = f.flag(s, protocol_name="Aave V3")
    assert d.flagged is True
    assert len(d.reasons) >= 3
