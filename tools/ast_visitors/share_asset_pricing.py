"""Detect share-asset-pricing formulas (shares * X / Y where Y depends on external state)."""
from __future__ import annotations

from .base import ASTVisitorBase, VisitorResult


class ShareAssetPricingDetector(ASTVisitorBase):
    name = "share-asset-pricing-detector"

    def scan_contract(self, contract, result: VisitorResult) -> None:
        for fn in contract.functions:
            if fn.is_constructor or fn.view is False:
                # Pricing functions are typically view; allow non-view too via heuristic
                pass
            formula_parts = self._find_share_asset_formula(fn)
            if formula_parts:
                ext_dep = self._find_external_state_dep(fn)
                result.hits.append({
                    "contract": contract.name,
                    "function": fn.name,
                    "formula": formula_parts,
                    "external_state_dep": ext_dep,
                })

    def _find_share_asset_formula(self, fn) -> str | None:
        """Heuristic: find binary operations 'A * B / C' where one side is
        totalSupply-like and another is totalAssets-like."""
        import re
        try:
            src = fn.source_mapping.content
        except Exception:
            return None
        if not src:
            return None
        # Match patterns: assets * supply / total, shares * totalAssets() / supply, etc.
        # Each operand may be a plain identifier or a function call like name()
        pattern = re.compile(
            r"([\w.]+(?:\(\))?)\s*\*\s*([\w.]+(?:\(\))?)\s*/\s*([\w.]+(?:\(\))?)"
        )
        matches = pattern.findall(src)
        for m in matches:
            tokens = set(t.lower() for t in m)
            has_supply = any("supply" in t for t in tokens)
            has_assets = any("asset" in t or "total" in t for t in tokens)
            if has_supply and has_assets:
                return f"{m[0]} * {m[1]} / {m[2]}"
        return None

    def _find_external_state_dep(self, fn) -> str:
        """Identify external calls or state reads from other contracts."""
        deps: list[str] = []
        for call in fn.high_level_calls:
            try:
                target_contract = call[0].name if hasattr(call[0], "name") else str(call[0])
                target_fn = call[1].name if hasattr(call[1], "name") else str(call[1])
                deps.append(f"{target_contract}.{target_fn}")
            except (IndexError, AttributeError):
                continue
        # Also collect internal calls that themselves might be external-state-readers
        for call in fn.internal_calls:
            try:
                cname = call.name if hasattr(call, "name") else str(call)
                if "totalAssets" in cname or "Balance" in cname:
                    deps.append(cname)
            except AttributeError:
                continue
        return "; ".join(deps) if deps else "none-detected"
