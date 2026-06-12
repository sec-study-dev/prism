"""Per-protocol data preparation: fetch docs and deployed source code."""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from pipeline.stage1.config import (
    SOURCE_CACHE_ROOT,
    SOURCE_PER_CONTRACT_CHARS,
    SOURCE_TOTAL_CHARS,
)
from tools.etherscan import EtherscanClient

log = logging.getLogger(__name__)

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]")


@dataclass
class ProtocolBundle:
    name: str
    chain: str
    slug: str
    metadata: dict
    docs_blob: str
    source_blob: str
    snapshot_block: int
    source_dir: Path | None = None
    source_path: Path | None = None
    contracts: list[dict] = field(default_factory=list)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20), reraise=True)
def _fetch_text(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "PRISM/1.0"})
    r.raise_for_status()
    return r.text


def _parse_etherscan_sources(source_code: str) -> dict[str, str]:
    """Normalize an Etherscan ``SourceCode`` field into {filename: content}.

    Etherscan returns one of three shapes:
      1. A plain Solidity/Vyper source string (single verified file).
      2. A Standard-JSON-Input wrapped in an extra brace pair: ``{{ ... }}``.
      3. A bare JSON object mapping path -> {"content": ...} or path -> content.
    """
    sc = source_code.strip()
    if not sc:
        return {}

    if sc.startswith("{{") and sc.endswith("}}"):
        sc_json = sc[1:-1]
    elif sc.startswith("{"):
        sc_json = sc
    else:
        return {"main.sol": sc}

    try:
        parsed = json.loads(sc_json)
    except json.JSONDecodeError:
        return {"main.sol": sc}

    sources = parsed.get("sources", parsed) if isinstance(parsed, dict) else {}
    out: dict[str, str] = {}
    for path, val in sources.items():
        if isinstance(val, dict):
            content = val.get("content", "")
        else:
            content = str(val)
        if content:
            out[path] = content
    return out or {"main.sol": sc}


def _safe_filename(path: str) -> str:
    base = path.replace("\\", "/").split("/")[-1] or "source.sol"
    return _SAFE_NAME_RE.sub("_", base)


def _fetch_source_bundle(
    client: EtherscanClient,
    chain: str,
    contracts: list[dict],
    source_dir: Path,
) -> tuple[str, Path | None]:
    """Fetch verified source for each contract, write to disk, build a blob.

    Returns (source_blob, primary_source_path). primary_source_path points at
    the largest written file (used by the AST visitors); None if nothing was
    written.
    """
    source_dir.mkdir(parents=True, exist_ok=True)
    blob_parts: list[str] = []
    total = 0
    largest: tuple[int, Path] | None = None

    for entry in contracts:
        addr = entry["address"]
        label = entry.get("name", addr)
        try:
            src = client.get_source_code(addr, chain, follow_proxy=True)
        except Exception as e:  # noqa: BLE001 — degrade per-contract, keep going
            log.warning("source fetch failed for %s (%s): %s", label, addr, e)
            continue

        resolved = src.get("ContractName", label)
        files = _parse_etherscan_sources(src.get("SourceCode", "") or "")
        merged = "\n\n".join(
            f"// --- {fname} ---\n{content}" for fname, content in files.items()
        )
        if not merged.strip():
            continue

        contract_dir = source_dir / _safe_filename(label)
        contract_dir.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            fpath = contract_dir / _safe_filename(fname)
            fpath.write_text(content)
            if largest is None or len(content) > largest[0]:
                largest = (len(content), fpath)

        snippet = merged[:SOURCE_PER_CONTRACT_CHARS]
        truncated = len(merged) > SOURCE_PER_CONTRACT_CHARS
        header = (
            f"===== CONTRACT {label} ({resolved}) @ {addr} ====="
            + (f"  [truncated to {SOURCE_PER_CONTRACT_CHARS} chars]" if truncated else "")
        )
        part = f"{header}\n{snippet}"
        if total + len(part) > SOURCE_TOTAL_CHARS:
            part = part[: max(0, SOURCE_TOTAL_CHARS - total)]
            blob_parts.append(part)
            break
        blob_parts.append(part)
        total += len(part)

    blob = "\n\n".join(blob_parts)
    return blob, (largest[1] if largest else None)


def prepare_protocol(
    metadata_path: Path,
    etherscan_client: EtherscanClient | None = None,
    source_root: Path | None = None,
) -> ProtocolBundle:
    metadata = json.loads(metadata_path.read_text())
    slug = metadata_path.parent.name
    chain = metadata["chain"]

    docs_dir = metadata_path.parent / "docs"
    docs_blob_parts = []
    if docs_dir.is_dir():
        for child in sorted(docs_dir.glob("*.md")):
            docs_blob_parts.append(f"=== {child.name} ===\n{child.read_text()}")
    if not docs_blob_parts:
        for url in metadata.get("doc_urls", []):
            try:
                text = _fetch_text(url)
                docs_blob_parts.append(f"=== {url} ===\n{text[:50_000]}")
            except Exception as e:
                log.warning("doc fetch failed for %s: %s", url, e)
    docs_blob = "\n\n".join(docs_blob_parts)

    contracts = metadata.get("contracts", [])
    source_blob = ""
    source_dir: Path | None = None
    source_path: Path | None = None

    client = etherscan_client
    if client is None and os.environ.get("ETHERSCAN_API_KEY"):
        client = EtherscanClient()

    if contracts and client is not None:
        source_dir = (source_root or SOURCE_CACHE_ROOT) / chain / slug
        source_blob, source_path = _fetch_source_bundle(
            client, chain, contracts, source_dir
        )

    if not source_blob:
        source_blob = (
            f"Repository: {metadata.get('repo_url')}\n"
            "No verified on-chain source was fetched "
            "(no contract addresses configured or Etherscan key unset)."
        )

    return ProtocolBundle(
        name=metadata["name"],
        chain=chain,
        slug=slug,
        metadata=metadata,
        docs_blob=docs_blob,
        source_blob=source_blob,
        snapshot_block=metadata["snapshot_block"],
        source_dir=source_dir,
        source_path=source_path,
        contracts=contracts,
    )
