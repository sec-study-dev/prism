"""Stage 2 orchestrator: build the mechanism graph from mechanism-db."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipeline.stage2.edges import derive_edges
from pipeline.stage2.graph import build_graph, to_dot, to_json
from pipeline.stage2.loader import load_mechanisms
from pipeline.stage2.model import Node
from pipeline.stage2.normalize import normalize


def build_nodes(irs: list[dict]) -> list[Node]:
    nodes: list[Node] = []
    for ir in irs:
        nodes.append(Node(
            id=ir["id"], chain=ir["chain"],
            protocol=ir["id"].split(".", 1)[0],
            tags=ir.get("tags", []), ports=normalize(ir), ir=ir,
        ))
    return nodes


def build(db_root: Path) -> dict:
    nodes = build_nodes(load_mechanisms(db_root))
    edges = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i == j:
                continue
            edges += derive_edges(a, b)
    return build_graph(nodes, edges)


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISM Stage 2 mechanism graph builder")
    parser.add_argument("--db", type=Path, default=Path("mechanism-db"))
    parser.add_argument("--out", type=Path, default=Path("mechanism-graph"))
    args = parser.parse_args()

    graph = build(args.db)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "graph.json").write_text(to_json(graph))
    (args.out / "graph.dot").write_text(to_dot(graph))
    print(f"nodes={len(graph['nodes'])} edges={len(graph['edges'])} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
