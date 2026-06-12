"""Detect functions lacking expected require/access-control checks (heuristic)."""
from __future__ import annotations

from .base import ASTVisitorBase, VisitorResult


# Function name patterns suggesting privileged operations
PRIVILEGED_PATTERNS = ("setowner", "setadmin", "transferownership", "upgrade",
                       "pause", "unpause", "emergencywithdraw", "rescue",
                       "setfee", "setprice", "setoracle", "addminter",
                       "removeminter", "setvault")


class MissingRequireDetector(ASTVisitorBase):
    name = "missing-require-detector"

    def scan_contract(self, contract, result: VisitorResult) -> None:
        for fn in contract.functions:
            if not fn.visibility in ("external", "public"):
                continue
            if fn.is_constructor:
                continue
            self._check_batch_transfer(contract, fn, result)
            self._check_mint_cap(contract, fn, result)
            self._check_access_control(contract, fn, result)

    def _check_batch_transfer(self, contract, fn, result) -> None:
        fname = fn.name.lower()
        if "batch" not in fname or "transfer" not in fname:
            return
        has_aggregate_check = self._has_aggregate_balance_check(fn)
        if not has_aggregate_check:
            result.hits.append({
                "function": f"{contract.name}.{fn.name}",
                "expected_check": "require(sum(amounts) <= _balances[msg.sender]) or per-iteration overflow-safe accounting",
                "severity": "high",
            })

    def _check_mint_cap(self, contract, fn, result) -> None:
        if fn.name.lower() != "mint":
            return
        has_cap_check = self._has_supply_cap_check(fn)
        if not has_cap_check:
            result.hits.append({
                "function": f"{contract.name}.{fn.name}",
                "expected_check": "require(totalSupply + amount <= SUPPLY_CAP) or analogous supply check",
                "severity": "medium",
            })

    def _check_access_control(self, contract, fn, result) -> None:
        fname = fn.name.lower()
        if not any(p in fname for p in PRIVILEGED_PATTERNS):
            return
        if fn.modifiers:
            return
        # No modifiers -- check function body for require(msg.sender == ...)
        try:
            src = fn.source_mapping.content or ""
        except Exception:
            src = ""
        if "msg.sender" in src and "require" in src:
            return
        result.hits.append({
            "function": f"{contract.name}.{fn.name}",
            "expected_check": "access control (onlyOwner / require(msg.sender == authorized))",
            "severity": "high",
        })

    def _has_aggregate_balance_check(self, fn) -> bool:
        try:
            src = fn.source_mapping.content or ""
        except Exception:
            return False
        return ("sum" in src.lower() and "require" in src) or "totalAmount" in src

    def _has_supply_cap_check(self, fn) -> bool:
        try:
            src = fn.source_mapping.content or ""
        except Exception:
            return False
        lower = src.lower()
        return any(k in lower for k in ("cap", "max", "supply") if "require" in lower)
