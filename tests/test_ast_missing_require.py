"""Tests for missing-require-detector AST visitor."""
from pathlib import Path
import pytest
from tools.ast_visitors.missing_require import MissingRequireDetector


@pytest.fixture(scope="session")
def missing_fixture(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "contracts" / "missing_validation.sol"


def test_flags_batch_transfer_missing_aggregate(missing_fixture: Path):
    d = MissingRequireDetector()
    hits = d.scan(missing_fixture)
    fns = {h["function"] for h in hits}
    assert any("batchTransfer" in f for f in fns)


def test_flags_mint_missing_supply_cap(missing_fixture: Path):
    d = MissingRequireDetector()
    hits = d.scan(missing_fixture)
    fns = {h["function"] for h in hits}
    assert any("mint" in f for f in fns)


def test_flags_setOwner_missing_access_control(missing_fixture: Path):
    d = MissingRequireDetector()
    hits = d.scan(missing_fixture)
    fns = {h["function"] for h in hits}
    assert any("setOwner" in f for f in fns)


def test_ignores_good_transfer(missing_fixture: Path):
    d = MissingRequireDetector()
    hits = d.scan(missing_fixture)
    fns = {h["function"] for h in hits}
    assert not any("goodTransfer" in f for f in fns)


def test_output_has_severity_and_expected_check(missing_fixture: Path):
    d = MissingRequireDetector()
    hits = d.scan(missing_fixture)
    for h in hits:
        assert "function" in h
        assert "expected_check" in h
        assert "severity" in h
        assert h["severity"] in ("low", "medium", "high")
