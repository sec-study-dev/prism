"""Tests for Etherscan/BscScan client."""
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import responses

from tools.etherscan import EtherscanClient, ChainConfig


def test_chain_config_ethereum():
    c = ChainConfig.for_chain("ethereum")
    assert c.api_url == "https://api.etherscan.io/v2/api"
    assert c.chain_id == 1


def test_chain_config_bsc():
    c = ChainConfig.for_chain("bsc")
    assert c.api_url == "https://api.etherscan.io/v2/api"
    assert c.chain_id == 56


def test_chain_config_unknown_raises():
    with pytest.raises(ValueError, match="unknown chain"):
        ChainConfig.for_chain("solana")


@responses.activate
def test_get_source_code_returns_verified(tmp_path: Path):
    addr = "0x1234567890abcdef1234567890abcdef12345678"
    responses.add(
        responses.GET,
        "https://api.etherscan.io/v2/api",
        json={
            "status": "1",
            "message": "OK",
            "result": [{
                "SourceCode": "contract X {}",
                "ContractName": "X",
                "ABI": "[]",
                "Implementation": "",
            }],
        },
        status=200,
    )
    client = EtherscanClient(api_key="test", cache_dir=tmp_path)
    source = client.get_source_code(addr, chain="ethereum")
    assert source["ContractName"] == "X"


@responses.activate
def test_get_source_code_caches_result(tmp_path: Path):
    addr = "0x1234567890abcdef1234567890abcdef12345678"
    responses.add(
        responses.GET,
        "https://api.etherscan.io/v2/api",
        json={"status": "1", "message": "OK", "result": [{"ContractName": "X", "SourceCode": "", "ABI": "[]", "Implementation": ""}]},
        status=200,
    )
    client = EtherscanClient(api_key="test", cache_dir=tmp_path)
    client.get_source_code(addr, chain="ethereum")
    cached = client.get_source_code(addr, chain="ethereum")
    assert cached["ContractName"] == "X"
    assert len(responses.calls) == 1


@responses.activate
def test_get_source_code_handles_proxy(tmp_path: Path):
    proxy_addr = "0x1111111111111111111111111111111111111111"
    impl_addr = "0x2222222222222222222222222222222222222222"
    responses.add(
        responses.GET,
        "https://api.etherscan.io/v2/api",
        json={
            "status": "1",
            "message": "OK",
            "result": [{
                "SourceCode": "proxy",
                "ContractName": "Proxy",
                "ABI": "[]",
                "Implementation": impl_addr,
            }],
        },
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.etherscan.io/v2/api",
        json={
            "status": "1",
            "message": "OK",
            "result": [{
                "SourceCode": "impl",
                "ContractName": "Impl",
                "ABI": "[]",
                "Implementation": "",
            }],
        },
        status=200,
    )
    client = EtherscanClient(api_key="test", cache_dir=tmp_path)
    result = client.get_source_code(proxy_addr, chain="ethereum", follow_proxy=True)
    assert result["ContractName"] == "Impl"
