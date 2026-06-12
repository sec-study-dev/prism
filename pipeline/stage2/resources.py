"""Canonical resource taxonomy for the Stage 2 mechanism graph."""
from __future__ import annotations

import re
from dataclasses import dataclass

RESOURCE_KINDS = {
    "token", "oracle", "price", "flashloan", "protocol-state", "invariant",
}

_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    return _WS.sub("", s.strip().lower())


@dataclass(frozen=True)
class Resource:
    kind: str
    id: str
    solidity_type: str | None = None
    origin: str = ""  # IR field path within its mechanism, e.g. "state_writes[2]"

    def __post_init__(self):
        if self.kind not in RESOURCE_KINDS:
            raise ValueError(f"unknown resource kind: {self.kind}")

    def to_dict(self) -> dict:
        d = {"kind": self.kind, "id": self.id, "from": self.origin}
        if self.solidity_type:
            d["solidity_type"] = self.solidity_type
        return d


def canonical_id(r: Resource) -> str:
    return f"{r.kind}:{_norm(r.id)}"


def same_resource(a: Resource, b: Resource) -> bool:
    return canonical_id(a) == canonical_id(b)
