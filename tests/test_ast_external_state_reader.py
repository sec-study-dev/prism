"""Tests for external-state-reader AST visitor."""
from pathlib import Path
import pytest
from tools.ast_visitors.external_state_reader import ExternalStateReader


@pytest.fixture(scope="session")
def oracle_fixture(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "contracts" / "oracle_consumer.sol"


def test_detects_oracle_read(oracle_fixture: Path):
    detector = ExternalStateReader()
    hits = detector.scan(oracle_fixture)
    fn_set = {h["caller_function"] for h in hits}
    assert any("readPrice" in f for f in fn_set)


def test_detects_external_vault_rate(oracle_fixture: Path):
    detector = ExternalStateReader()
    hits = detector.scan(oracle_fixture)
    fn_set = {h["caller_function"] for h in hits}
    assert any("readRateAndCompute" in f for f in fn_set)


def test_ignores_pure_local_reads(oracle_fixture: Path):
    detector = ExternalStateReader()
    hits = detector.scan(oracle_fixture)
    fn_set = {h["caller_function"] for h in hits}
    assert not any("pureLocal" in f for f in fn_set)


def test_output_shape(oracle_fixture: Path):
    detector = ExternalStateReader()
    hits = detector.scan(oracle_fixture)
    for h in hits:
        for key in ["caller_function", "source_contract", "source_variable", "purpose_heuristic"]:
            assert key in h
