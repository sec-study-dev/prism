"""Detect cross-contract storage reads and oracle reads."""
from __future__ import annotations

from .base import ASTVisitorBase, VisitorResult


ORACLE_KEYWORDS = ("latestAnswer", "latestRoundData", "price", "exchangeRate",
                   "getReserves", "totalAssets", "pricePerShare",
                   "convertToAssets", "convertToShares")


class ExternalStateReader(ASTVisitorBase):
    name = "external-state-reader"

    def scan_contract(self, contract, result: VisitorResult) -> None:
        for fn in contract.functions:
            for call in fn.high_level_calls:
                try:
                    target_contract = call[0]
                    target_fn = call[1]
                    tc_name = target_contract.name if hasattr(target_contract, "name") else str(target_contract)
                    tf_name = target_fn.name if hasattr(target_fn, "name") else str(target_fn)
                except (IndexError, AttributeError):
                    continue
                heuristic = self._classify_purpose(tc_name, tf_name)
                result.hits.append({
                    "caller_function": f"{contract.name}.{fn.name}",
                    "source_contract": tc_name,
                    "source_variable": tf_name,
                    "purpose_heuristic": heuristic,
                })

    def _classify_purpose(self, contract_name: str, fn_name: str) -> str:
        lower_fn = fn_name.lower()
        if "oracle" in contract_name.lower() or "latestanswer" in lower_fn or "price" in lower_fn:
            return "price-oracle"
        if "exchangerate" in lower_fn or "pricepershare" in lower_fn:
            return "share-asset-rate"
        if "totalassets" in lower_fn or "totalsupply" in lower_fn:
            return "supply-or-assets-read"
        if "balanceof" in lower_fn:
            return "balance-read"
        if "getreserves" in lower_fn:
            return "amm-reserves"
        return "external-state-read"
