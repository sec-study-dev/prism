"""Stage 2 edge derivation: the 4 composability edge types over normalized ports."""
from __future__ import annotations

import re

from .model import Edge, Node
from .resources import Resource, same_resource

_PRECOND_ORIGIN = re.compile(r"^(preconditions|trigger\.conditions)\[")
_WRAP_TAGS = {"lending", "lst", "lrt", "yield-vault", "stablecoin-cdp"}
_SYSTEMIC = {"protocol-wide", "cross-protocol"}

_TYPE_GROUPS = [
    {"uint", "uint256", "uint128", "uint96", "uint160"},
    {"int", "int256"},
    {"address"},
    {"bool"},
]


def type_compatible(a: Resource, b: Resource) -> bool:
    if a.kind == "token" or b.kind == "token":
        return True  # token matched by identity; type implicit (balance)
    if not a.solidity_type or not b.solidity_type:
        return True  # unknown type -> do not block
    ta, tb = a.solidity_type.lower(), b.solidity_type.lower()
    if ta == tb:
        return True
    return any(ta in g and tb in g for g in _TYPE_GROUPS)


def _match(produced, consumed):
    for p in produced:
        for c in consumed:
            if same_resource(p, c) and type_compatible(p, c):
                yield p, c


def _has_systemic_at_risk(node: Node) -> bool:
    return any(inv.get("scope") in _SYSTEMIC
               for inv in node.ir.get("invariants_at_risk", []))


def _layering(a: Node, b: Node, chain: str) -> list[Edge]:
    out: list[Edge] = []
    for i, d in enumerate(a.ir.get("deps", [])):
        if d["kind"] in ("protocol", "mechanism") and d["ref"] in (b.protocol, b.id):
            out.append(Edge(a.id, b.id, "layering", True, chain, [],
                            [f"src.deps[{i}]->{d['ref']}"]))
    if _WRAP_TAGS & set(b.tags):
        for p, c in _match(a.ports.produces, b.ports.consumes):
            if p.kind == "token":
                out.append(Edge(a.id, b.id, "layering", True, chain, [p],
                                [f"src.{p.origin} (underlying) ↔ dst.{c.origin}"]))
    return out


def derive_edges(a: Node, b: Node) -> list[Edge]:
    if a.id == b.id or a.chain != b.chain:
        return []
    chain = a.chain
    edges: list[Edge] = []

    # sequential-dep (directed): a produces R, b consumes R as a precondition/trigger
    for p, c in _match(a.ports.produces, b.ports.consumes):
        if _PRECOND_ORIGIN.search(c.origin):
            edges.append(Edge(a.id, b.id, "sequential-dep", True, chain,
                              [p], [f"src.{p.origin} ↔ dst.{c.origin}"]))

    # symmetric edges: emit once, on a.id < b.id
    if a.id < b.id:
        # state-share: both write the same protocol-state/price/token resource
        # both sides are produces here; _match just intersects by resource identity
        for p, q in _match(a.ports.produces, b.ports.produces):
            if p.kind in ("protocol-state", "price", "token"):
                edges.append(Edge(a.id, b.id, "state-share", False, chain,
                                  [p], [f"src.{p.origin} ↔ dst.{q.origin}"]))
        # invariant-coupling: one side has a systemic at-risk invariant on a price/oracle
        # the other side reads. The trigger is asymmetric, so check BOTH assignments of
        # which side is the invariant bearer (the bearer is not necessarily the smaller id).
        for bearer, reader in ((a, b), (b, a)):
            if not _has_systemic_at_risk(bearer):
                continue
            for r in bearer.ports.produces:
                if r.kind in ("price", "oracle"):
                    for other in reader.ports.consumes:
                        if same_resource(r, other):
                            edges.append(Edge(bearer.id, reader.id, "invariant-coupling", False,
                                              chain, [r],
                                              [f"src.invariants_at_risk ↔ dst.{other.origin}"]))
                            break

    # layering (directed): a deps -> b protocol/mechanism, or a's token is b's underlying
    edges += _layering(a, b, chain)
    return edges
