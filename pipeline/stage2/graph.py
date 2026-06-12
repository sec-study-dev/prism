"""Stage 2 graph assembly, deterministic serialization, and DOT export."""
from __future__ import annotations

import json

from .model import Edge, Node
from .resources import canonical_id

GRAPH_VERSION = "stage2-v1"

_EDGE_COLORS = {
    "sequential-dep": "blue", "state-share": "green",
    "invariant-coupling": "red", "layering": "purple",
}


def _res_list(rs):
    return [r.to_dict() for r in sorted(rs, key=lambda x: (x.kind, x.id, x.origin))]


def _node_dict(n: Node) -> dict:
    return {
        "id": n.id, "chain": n.chain, "protocol": n.protocol,
        "tags": sorted(n.tags),
        "ports": {
            "produces": _res_list(n.ports.produces),
            "consumes": _res_list(n.ports.consumes),
        },
    }


def _edge_dict(e: Edge) -> dict:
    return {
        "src": e.src, "dst": e.dst, "type": e.type, "directed": e.directed,
        "chain": e.chain, "shared_resources": _res_list(e.shared_resources),
        "provenance": list(e.provenance),
    }


def _edge_key(e: Edge) -> tuple:
    return (e.src, e.dst, e.type,
            tuple(sorted(canonical_id(r) for r in e.shared_resources)))


def build_graph(nodes: list[Node], edges: list[Edge]) -> dict:
    # normalize() may emit the same resource under multiple origins (e.g. a token
    # appearing both as a deps entry and a balance-check precondition), so edge
    # derivation can yield identical edges. Collapse them here by
    # (src, dst, type, shared-resource identities); provenance is not part of the
    # key, so duplicate edges that differ only in provenance string are merged.
    seen, unique = set(), []
    for e in sorted(edges, key=lambda e: (e.src, e.dst, e.type)):
        key = _edge_key(e)
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    return {
        "version": GRAPH_VERSION,
        "nodes": [_node_dict(n) for n in sorted(nodes, key=lambda n: n.id)],
        "edges": [_edge_dict(e) for e in unique],
    }


def to_json(graph: dict) -> str:
    return json.dumps(graph, indent=2, sort_keys=True) + "\n"


def to_dot(graph: dict) -> str:
    lines = ["digraph mechanism_graph {"]
    by_chain: dict[str, list[str]] = {}
    for n in graph["nodes"]:
        by_chain.setdefault(n["chain"], []).append(n["id"])
    for chain, ids in sorted(by_chain.items()):
        lines.append(f'  subgraph cluster_{chain} {{ label="{chain}";')
        for node_id in sorted(ids):
            lines.append(f'    "{node_id}";')
        lines.append("  }")
    for e in graph["edges"]:
        extra = "" if e["directed"] else " dir=none"
        color = _EDGE_COLORS.get(e["type"], "black")
        lines.append(f'  "{e["src"]}" -> "{e["dst"]}" [color={color}{extra}];')
    lines.append("}")
    return "\n".join(lines) + "\n"
