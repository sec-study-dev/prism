"""Etherscan/BscScan API client with local cache.

Uses Etherscan V2 unified API (single endpoint, chainid parameter).
Docs: https://docs.etherscan.io/etherscan-v2
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass(frozen=True)
class ChainConfig:
    chain_id: int
    api_url: str

    @classmethod
    def for_chain(cls, chain: str) -> "ChainConfig":
        if chain == "ethereum":
            return cls(chain_id=1, api_url="https://api.etherscan.io/v2/api")
        if chain == "bsc":
            return cls(chain_id=56, api_url="https://api.etherscan.io/v2/api")
        raise ValueError(f"unknown chain: {chain}")


class EtherscanClient:
    def __init__(self, api_key: str | None = None, cache_dir: Path | None = None):
        self.api_key = api_key or os.environ.get("ETHERSCAN_API_KEY", "")
        self.cache_dir = cache_dir or (Path.home() / ".cache" / "prism" / "etherscan")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, *parts: str) -> Path:
        h = hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]
        return self.cache_dir / f"{h}.json"

    def _cached_get(self, key_parts: tuple[str, ...], fetch_fn) -> Any:
        cache_path = self._cache_key(*key_parts)
        if cache_path.exists():
            return json.loads(cache_path.read_text())
        result = fetch_fn()
        cache_path.write_text(json.dumps(result, indent=2))
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _api_get(self, params: dict[str, str]) -> dict:
        cfg = ChainConfig.for_chain(params["_chain"])
        del params["_chain"]
        params["chainid"] = str(cfg.chain_id)
        params["apikey"] = self.api_key
        r = requests.get(cfg.api_url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "1":
            raise RuntimeError(f"Etherscan error: {data.get('message')} / {data.get('result')}")
        return data

    def get_source_code(self, address: str, chain: str, follow_proxy: bool = True) -> dict:
        """Fetch verified source + ABI for a contract address.

        If follow_proxy and the contract is a proxy with Implementation set,
        recursively fetch the implementation's source.
        """
        def fetch():
            return self._api_get({
                "_chain": chain,
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
            })
        data = self._cached_get(("source", chain, address), fetch)
        result = data["result"][0]
        impl = result.get("Implementation", "").strip()
        if follow_proxy and impl and impl != "0x" and impl != address:
            return self.get_source_code(impl, chain, follow_proxy=True)
        return result

    def get_abi(self, address: str, chain: str) -> list[dict]:
        source = self.get_source_code(address, chain)
        abi_str = source.get("ABI", "")
        if not abi_str or abi_str == "Contract source code not verified":
            return []
        return json.loads(abi_str)
