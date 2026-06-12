"""Preflight readiness check for the Stage 1 pipeline.

Verifies every external dependency the real-LLM run needs before spending
budget: API keys, archive RPC access at the Tier-A snapshot blocks, the
Foundry toolchain, and a live verified-source fetch for the target protocol.

Usage:
    set -a; source .env; set +a
    python -m scripts.preflight \
        --metadata corpus/tier-a/protocols/ethereum/aave-v3/metadata.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.stage1.config import ETH_SNAPSHOT_BLOCK, BSC_SNAPSHOT_BLOCK  # noqa: E402
from pipeline.stage1.prepare import prepare_protocol  # noqa: E402


def _rpc_block_present(rpc_url: str, block: int) -> bool:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBlockByNumber",
        "params": [hex(block), False],
    }
    r = requests.post(rpc_url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json().get("result") is not None


def check_anthropic_key() -> tuple[bool, bool, str]:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True, True, "ANTHROPIC_API_KEY set"
    return False, True, "ANTHROPIC_API_KEY unset — required for the LLM pipeline"


def check_etherscan() -> tuple[bool, bool, str]:
    if not os.environ.get("ETHERSCAN_API_KEY"):
        return False, True, "ETHERSCAN_API_KEY unset"
    try:
        from tools.etherscan import EtherscanClient

        src = EtherscanClient().get_source_code(
            "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2", "ethereum"
        )
        name = src.get("ContractName", "?")
        return True, True, f"live fetch OK (resolved {name})"
    except Exception as e:  # noqa: BLE001
        return False, True, f"fetch failed: {e}"


def check_rpc(label: str, env_var: str, block: int) -> tuple[bool, bool, str]:
    url = os.environ.get(env_var)
    if not url:
        return False, True, f"{env_var} unset"
    try:
        if _rpc_block_present(url, block):
            return True, True, f"archive OK at block {block}"
        return False, True, f"block {block} returned null (not archive?)"
    except Exception as e:  # noqa: BLE001
        return False, True, f"{label} RPC error: {e}"


def check_forge() -> tuple[bool, bool, str]:
    forge = shutil.which("forge") or str(Path.home() / ".foundry" / "bin" / "forge")
    if Path(forge).exists():
        return True, True, f"forge found at {forge}"
    return False, True, "forge not found (run foundryup)"


def check_source_prepare(metadata_path: Path) -> tuple[bool, bool, str]:
    if not os.environ.get("ETHERSCAN_API_KEY"):
        return False, True, "skipped — needs ETHERSCAN_API_KEY"
    try:
        bundle = prepare_protocol(metadata_path)
    except Exception as e:  # noqa: BLE001
        return False, True, f"prepare failed: {e}"
    if not bundle.contracts:
        return False, False, "no contracts in metadata (degraded run only)"
    if "No verified on-chain source" in bundle.source_blob:
        return False, True, "fell back to placeholder source"
    return True, True, (
        f"{len(bundle.contracts)} contract(s), "
        f"{len(bundle.source_blob):,} chars of real source"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 1 preflight readiness check")
    parser.add_argument(
        "--metadata",
        type=Path,
        default=REPO_ROOT
        / "corpus/tier-a/protocols/ethereum/aave-v3/metadata.json",
        help="Protocol metadata.json to validate source prep against",
    )
    args = parser.parse_args()

    checks = [
        ("Anthropic API key", check_anthropic_key()),
        ("Etherscan", check_etherscan()),
        ("ETH archive RPC", check_rpc("ETH", "ETH_RPC_URL", ETH_SNAPSHOT_BLOCK)),
        ("BSC archive RPC", check_rpc("BSC", "BSC_RPC_URL", BSC_SNAPSHOT_BLOCK)),
        ("Foundry (forge)", check_forge()),
        (f"Source prep ({args.metadata.parent.name})", check_source_prepare(args.metadata)),
    ]

    print("PRISM Stage 1 — preflight\n")
    all_required_ok = True
    for label, (ok, required, detail) in checks:
        mark = "PASS" if ok else ("FAIL" if required else "WARN")
        print(f"  [{mark}] {label:32s} {detail}")
        if required and not ok:
            all_required_ok = False

    print()
    if all_required_ok:
        print("READY — all required checks pass; the pipeline can run.")
        return 0
    print("NOT READY — resolve the FAIL items above before running the pipeline.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
