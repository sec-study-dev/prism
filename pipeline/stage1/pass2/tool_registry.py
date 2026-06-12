"""Pass 2 tool registry: tools exposed to the extraction agent.

For v1, tools are exposed as structured context blobs assembled before the
LLM call (rather than tool-calling). The agent receives:
- slither output (call graph, detectors, inheritance)
- 3 PRISM AST visitor outputs
- Etherscan source / ABI snippet
- Foundry storage-layout (if available)
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.ast_visitors.share_asset_pricing import ShareAssetPricingDetector
from tools.ast_visitors.external_state_reader import ExternalStateReader
from tools.ast_visitors.missing_require import MissingRequireDetector


@dataclass
class ToolContext:
    slither_summary: str = ""
    share_asset_pricing_hits: list[dict] = None
    external_state_reads: list[dict] = None
    missing_requires: list[dict] = None
    storage_layout: str = ""

    def to_prompt_block(self) -> str:
        parts = []
        if self.slither_summary:
            parts.append(f"=== SLITHER SUMMARY ===\n{self.slither_summary}")
        if self.share_asset_pricing_hits:
            parts.append(f"=== SHARE-ASSET-PRICING DETECTOR ===\n{json.dumps(self.share_asset_pricing_hits, indent=2)}")
        if self.external_state_reads:
            parts.append(f"=== EXTERNAL-STATE-READS ===\n{json.dumps(self.external_state_reads, indent=2)}")
        if self.missing_requires:
            parts.append(f"=== MISSING-REQUIRE DETECTOR ===\n{json.dumps(self.missing_requires, indent=2)}")
        if self.storage_layout:
            parts.append(f"=== STORAGE LAYOUT ===\n{self.storage_layout}")
        return "\n\n".join(parts)


class ToolRegistry:
    def __init__(self):
        self.share_asset = ShareAssetPricingDetector()
        self.external = ExternalStateReader()
        self.missing_req = MissingRequireDetector()

    def gather(self, source_path: Path | None) -> ToolContext:
        ctx = ToolContext()
        if source_path and source_path.exists():
            try:
                ctx.share_asset_pricing_hits = self.share_asset.scan(source_path)
                ctx.external_state_reads = self.external.scan(source_path)
                ctx.missing_requires = self.missing_req.scan(source_path)
            except Exception as e:
                ctx.slither_summary = f"AST visitors failed: {e}"
        return ctx
