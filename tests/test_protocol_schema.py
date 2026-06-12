"""Tests for the protocol-metadata JSON Schema."""
import json
from pathlib import Path

import jsonschema
import pytest


REQUIRED_FIELDS = {
    "name", "chain", "categories", "tvl_usd_at_snapshot",
    "repo_url", "doc_urls", "snapshot_block", "tier",
}


def test_protocol_schema_file_exists(protocol_schema_path: Path):
    assert protocol_schema_path.exists()


def test_protocol_schema_is_valid_jsonschema(protocol_schema: dict):
    jsonschema.Draft202012Validator.check_schema(protocol_schema)


def test_protocol_schema_required_fields(protocol_schema: dict):
    assert set(protocol_schema.get("required", [])) == REQUIRED_FIELDS


@pytest.fixture
def good_protocol() -> dict:
    return {
        "name": "Example",
        "chain": "ethereum",
        "categories": ["dex"],
        "tvl_usd_at_snapshot": 100_000_000,
        "repo_url": "https://github.com/example/protocol",
        "doc_urls": ["https://docs.example.com"],
        "snapshot_block": 22000000,
        "tier": "A",
    }


def test_good_protocol_validates(protocol_schema: dict, good_protocol: dict):
    jsonschema.validate(good_protocol, protocol_schema)


def test_protocol_missing_tier_rejected(protocol_schema: dict, good_protocol: dict):
    del good_protocol["tier"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_protocol, protocol_schema)


def test_protocol_negative_tvl_rejected(protocol_schema: dict, good_protocol: dict):
    good_protocol["tvl_usd_at_snapshot"] = -1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_protocol, protocol_schema)


def test_protocol_unknown_chain_rejected(protocol_schema: dict, good_protocol: dict):
    good_protocol["chain"] = "solana"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_protocol, protocol_schema)


# Tier-A completeness invariants (per spec §8.3 and plan Task 6)

PRIORITY_CATEGORIES = {
    "dex-amm", "dex-clmm", "lending", "lst", "lrt",
    "yield-vault", "stablecoin-cdp", "perp", "bridge", "gauge-ve",
}


def test_tier_a_has_at_least_twenty_protocols(repo_root: Path):
    tier_a = repo_root / "corpus" / "tier-a" / "protocols"
    metadata_files = list(tier_a.rglob("metadata.json"))
    assert len(metadata_files) >= 20, (
        f"Tier-A must contain ≥20 protocols (≥10 per chain), found {len(metadata_files)}"
    )


def test_tier_a_all_metadata_valid(protocol_schema: dict, repo_root: Path):
    tier_a = repo_root / "corpus" / "tier-a" / "protocols"
    validator = jsonschema.Draft202012Validator(protocol_schema)
    for f in tier_a.rglob("metadata.json"):
        data = json.loads(f.read_text())
        errors = list(validator.iter_errors(data))
        assert not errors, f"{f}: {[e.message for e in errors]}"


def test_tier_a_all_marked_tier_A(repo_root: Path):
    tier_a = repo_root / "corpus" / "tier-a" / "protocols"
    for f in tier_a.rglob("metadata.json"):
        data = json.loads(f.read_text())
        assert data["tier"] == "A", f"{f}: tier should be 'A', got {data['tier']}"


def test_tier_a_chain_balance(repo_root: Path):
    tier_a = repo_root / "corpus" / "tier-a" / "protocols"
    counts = {"ethereum": 0, "bsc": 0}
    for f in tier_a.rglob("metadata.json"):
        counts[json.loads(f.read_text())["chain"]] += 1
    assert counts["ethereum"] >= 10, f"too few Ethereum protocols: {counts}"
    assert counts["bsc"] >= 10, f"too few BSC protocols: {counts}"


def test_tier_a_priority_category_coverage(repo_root: Path):
    """Each chain should cover ≥7 of 10 priority categories.

    Gaps allowed for chains without qualifying protocols (e.g., LRT on BSC);
    document gaps in selection notes.
    """
    tier_a = repo_root / "corpus" / "tier-a" / "protocols"
    per_chain: dict[str, set[str]] = {"ethereum": set(), "bsc": set()}
    for f in tier_a.rglob("metadata.json"):
        data = json.loads(f.read_text())
        cats = set(data["categories"])
        per_chain[data["chain"]].update(cats & PRIORITY_CATEGORIES)
    for chain, anchored in per_chain.items():
        assert len(anchored) >= 7, (
            f"{chain} covers only {len(anchored)} of 10 priority categories: {anchored}"
        )
