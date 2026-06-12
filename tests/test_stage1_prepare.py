"""Tests for per-protocol source preparation."""
import json

import pytest

from pipeline.stage1.prepare import _parse_etherscan_sources, prepare_protocol


class FakeEtherscan:
    """Stand-in for EtherscanClient: returns canned getsourcecode results."""

    def __init__(self, by_address: dict[str, dict]):
        self.by_address = by_address

    def get_source_code(self, address, chain, follow_proxy=True):
        return self.by_address[address]


def test_parse_plain_single_file():
    out = _parse_etherscan_sources("contract A { uint x; }")
    assert out == {"main.sol": "contract A { uint x; }"}


def test_parse_standard_json_double_brace():
    sc = "{" + json.dumps({
        "language": "Solidity",
        "sources": {
            "src/A.sol": {"content": "contract A {}"},
            "src/B.sol": {"content": "contract B {}"},
        },
    }) + "}"
    out = _parse_etherscan_sources(sc)
    assert out == {"src/A.sol": "contract A {}", "src/B.sol": "contract B {}"}


def test_parse_bare_json_object():
    sc = json.dumps({"C.sol": {"content": "contract C {}"}})
    out = _parse_etherscan_sources(sc)
    assert out == {"C.sol": "contract C {}"}


def test_parse_empty():
    assert _parse_etherscan_sources("") == {}


def _write_metadata(tmp_path, contracts):
    proto_dir = tmp_path / "aave-v3"
    proto_dir.mkdir()
    meta = {
        "name": "Aave V3",
        "chain": "ethereum",
        "categories": ["lending"],
        "tvl_usd_at_snapshot": 1,
        "repo_url": "https://example.com/repo",
        "doc_urls": [],
        "snapshot_block": 22500000,
        "tier": "A",
        "contracts": contracts,
    }
    mp = proto_dir / "metadata.json"
    mp.write_text(json.dumps(meta))
    return mp


def test_prepare_fetches_real_source(tmp_path):
    addr = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    fake = FakeEtherscan({
        addr: {
            "ContractName": "PoolInstance",
            "SourceCode": "contract Pool { function flashLoan() external {} }",
        }
    })
    mp = _write_metadata(tmp_path, [{"name": "Pool", "address": addr}])
    bundle = prepare_protocol(mp, etherscan_client=fake, source_root=tmp_path / "src")

    assert "No verified on-chain source" not in bundle.source_blob
    assert "PoolInstance" in bundle.source_blob
    assert "flashLoan" in bundle.source_blob
    assert bundle.source_dir is not None
    assert bundle.source_path is not None and bundle.source_path.exists()
    assert bundle.contracts == [{"name": "Pool", "address": addr}]


def test_prepare_falls_back_without_contracts(tmp_path):
    mp = _write_metadata(tmp_path, [])
    bundle = prepare_protocol(mp, etherscan_client=FakeEtherscan({}),
                              source_root=tmp_path / "src")
    assert "No verified on-chain source" in bundle.source_blob
    assert bundle.source_dir is None
    assert bundle.source_path is None


def test_prepare_respects_total_char_budget(tmp_path, monkeypatch):
    monkeypatch.setattr("pipeline.stage1.prepare.SOURCE_TOTAL_CHARS", 500)
    monkeypatch.setattr("pipeline.stage1.prepare.SOURCE_PER_CONTRACT_CHARS", 400)
    big = "// x\n" + ("a" * 10_000)
    contracts, mapping = [], {}
    for i in range(5):
        a = f"0x{i:040x}"
        contracts.append({"name": f"C{i}", "address": a})
        mapping[a] = {"ContractName": f"C{i}", "SourceCode": big}
    mp = _write_metadata(tmp_path, contracts)
    bundle = prepare_protocol(mp, etherscan_client=FakeEtherscan(mapping),
                              source_root=tmp_path / "src")
    # blob is bounded near the total budget (headers add a little slack)
    assert len(bundle.source_blob) <= 700


def test_prepare_skips_failed_contract(tmp_path):
    good = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    bad = "0x0000000000000000000000000000000000000bad"

    class Flaky(FakeEtherscan):
        def get_source_code(self, address, chain, follow_proxy=True):
            if address == bad:
                raise RuntimeError("not verified")
            return self.by_address[address]

    fake = Flaky({good: {"ContractName": "Pool", "SourceCode": "contract Pool {}"}})
    mp = _write_metadata(tmp_path, [
        {"name": "Bad", "address": bad},
        {"name": "Pool", "address": good},
    ])
    bundle = prepare_protocol(mp, etherscan_client=fake, source_root=tmp_path / "src")
    assert "contract Pool" in bundle.source_blob
