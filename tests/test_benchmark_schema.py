"""Tests for the benchmark-event JSON Schema."""
import json
from pathlib import Path

import jsonschema
import pytest

REQUIRED = {
    "event_id", "tx_hash", "chain", "fork_block",
    "involved_protocols", "involved_mechanisms",
    "profit_usd", "victim_set",
    "event_type", "disclosure_date",
    "subset_class", "sources",
}


def test_benchmark_schema_exists(benchmark_schema_path: Path):
    assert benchmark_schema_path.exists()


def test_benchmark_schema_is_valid(benchmark_schema: dict):
    jsonschema.Draft202012Validator.check_schema(benchmark_schema)


def test_benchmark_schema_required(benchmark_schema: dict):
    assert set(benchmark_schema.get("required", [])) == REQUIRED


@pytest.fixture
def good_event() -> dict:
    return {
        "event_id": "example-001",
        "tx_hash": "0x" + "a" * 64,
        "chain": "ethereum",
        "fork_block": 18000000,
        "involved_protocols": ["example-dex"],
        "involved_mechanisms": ["swap", "flashloan"],
        "profit_usd": 100000,
        "victim_set": ["example-dex-treasury"],
        "event_type": "exploit",
        "disclosure_date": "2024-01-01",
        "subset_class": "B",
        "sources": [
            {"kind": "defihacklabs", "url": "https://example.com/case"}
        ]
    }


def test_good_event_validates(benchmark_schema: dict, good_event: dict):
    jsonschema.validate(good_event, benchmark_schema)


def test_bad_tx_hash_rejected(benchmark_schema: dict, good_event: dict):
    good_event["tx_hash"] = "0xshort"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_event, benchmark_schema)


def test_invalid_subset_class_rejected(benchmark_schema: dict, good_event: dict):
    good_event["subset_class"] = "Z"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_event, benchmark_schema)


def test_missing_sources_rejected(benchmark_schema: dict, good_event: dict):
    good_event["sources"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(good_event, benchmark_schema)


def test_benchmark_has_50_to_200_events(repo_root: Path):
    events_dir = repo_root / "benchmark" / "events"
    files = list(events_dir.rglob("*.json"))
    assert 50 <= len(files) <= 200, f"benchmark size out of range: {len(files)}"


def test_benchmark_all_events_valid(benchmark_schema: dict, repo_root: Path):
    events_dir = repo_root / "benchmark" / "events"
    validator = jsonschema.Draft202012Validator(benchmark_schema)
    for f in events_dir.rglob("*.json"):
        data = json.loads(f.read_text())
        errors = list(validator.iter_errors(data))
        assert not errors, f"{f}: {[e.message for e in errors]}"


def test_benchmark_class_distribution(repo_root: Path):
    """At least some events in M and mixed; not 100% B."""
    events_dir = repo_root / "benchmark" / "events"
    counts = {"M": 0, "B": 0, "mixed": 0}
    for f in events_dir.rglob("*.json"):
        counts[json.loads(f.read_text())["subset_class"]] += 1
    total = sum(counts.values())
    m_plus_mixed = counts["M"] + counts["mixed"]
    # Spec §9.4 expects M ≈ 20-30% of total; allow 15-40% as Stage 0 tolerance
    assert m_plus_mixed >= total * 0.15, (
        f"M+mixed too low: {counts}; expected ≥15% of {total}"
    )
    assert m_plus_mixed <= total * 0.40, (
        f"M+mixed too high (overclassification?): {counts}; expected ≤40% of {total}"
    )


def test_benchmark_uniqueness(repo_root: Path):
    events_dir = repo_root / "benchmark" / "events"
    ids: set[str] = set()
    txs: set[str] = set()
    for f in events_dir.rglob("*.json"):
        data = json.loads(f.read_text())
        assert data["event_id"] not in ids, f"duplicate event_id: {data['event_id']}"
        assert data["tx_hash"] not in txs, f"duplicate tx_hash: {data['tx_hash']}"
        ids.add(data["event_id"])
        txs.add(data["tx_hash"])


def test_benchmark_rationale_present_for_M_and_mixed(repo_root: Path):
    events_dir = repo_root / "benchmark" / "events"
    for f in events_dir.rglob("*.json"):
        data = json.loads(f.read_text())
        if data["subset_class"] in {"M", "mixed"}:
            r = data.get("classification_rationale", "")
            assert r and len(r) >= 20, (
                f"{f}: subset_class={data['subset_class']} requires "
                f"classification_rationale ≥ 20 chars"
            )
