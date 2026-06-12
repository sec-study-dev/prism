"""Tests for share-asset-pricing-detector AST visitor."""
from pathlib import Path

import pytest

from tools.ast_visitors.share_asset_pricing import ShareAssetPricingDetector


@pytest.fixture(scope="session")
def vault_fixture(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "contracts" / "vault.sol"


def test_detector_finds_convertToShares(vault_fixture: Path):
    detector = ShareAssetPricingDetector()
    hits = detector.scan(vault_fixture)
    fn_names = {h["function"] for h in hits}
    assert "convertToShares" in fn_names


def test_detector_finds_convertToAssets(vault_fixture: Path):
    detector = ShareAssetPricingDetector()
    hits = detector.scan(vault_fixture)
    fn_names = {h["function"] for h in hits}
    assert "convertToAssets" in fn_names


def test_detector_ignores_plain_transfer(vault_fixture: Path):
    detector = ShareAssetPricingDetector()
    hits = detector.scan(vault_fixture)
    fn_names = {h["function"] for h in hits}
    assert "plainTransfer" not in fn_names


def test_detector_output_shape(vault_fixture: Path):
    detector = ShareAssetPricingDetector()
    hits = detector.scan(vault_fixture)
    for h in hits:
        assert "contract" in h
        assert "function" in h
        assert "formula" in h
        assert "external_state_dep" in h


def test_detector_detects_external_dep(vault_fixture: Path):
    detector = ShareAssetPricingDetector()
    hits = detector.scan(vault_fixture)
    shares_hit = next(h for h in hits if h["function"] == "convertToShares")
    assert "balanceOf" in shares_hit["external_state_dep"] or \
           "totalAssets" in shares_hit["external_state_dep"]
