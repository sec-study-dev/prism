"""Shared base for PRISM AST visitors (built on slither / SlithIR)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from crytic_compile import CryticCompile
from crytic_compile.platform.solc import Solc
from slither import Slither


@dataclass
class VisitorResult:
    hits: list[dict[str, Any]] = field(default_factory=list)


class ASTVisitorBase:
    """Base class for PRISM AST visitors.

    Subclasses override scan_contract() to inspect a single Contract object
    from slither. The base class handles loading and aggregation.

    Note: We compile via the Solc platform directly to avoid crytic-compile
    auto-detecting a Foundry project (foundry.toml) and attempting to invoke
    ``forge``, which may not be installed.
    """

    name: str = "base"

    def scan(self, source_path: Path) -> list[dict[str, Any]]:
        cc = CryticCompile(Solc(str(source_path)))
        sl = Slither(cc)
        result = VisitorResult()
        for contract in sl.contracts:
            self.scan_contract(contract, result)
        return result.hits

    def scan_contract(self, contract, result: VisitorResult) -> None:
        raise NotImplementedError
