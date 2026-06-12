import time
from pipeline.stage2.cli import build_nodes
from pipeline.stage2.edges import derive_edges
from pipeline.stage2.graph import build_graph, to_json


def _ir(i):
    return {
        "id": f"proto{i % 10}.mech{i}", "chain": "ethereum" if i % 2 else "bsc",
        "trigger": {"kind": "function-call", "entry_point": "C.f"},
        "state_reads": [{"contract": "C", "variable": "v", "purpose": "reads share price"}],
        "state_writes": [{"contract": "C", "variable": "v", "purpose": "writes share price"}],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [{"kind": "token-standard", "ref": "USDC"}],
        "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "t", "status": "passing"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "L1"}],
    }


def _build(irs):
    nodes = build_nodes(irs)
    edges = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i != j:
                edges += derive_edges(a, b)
    return build_graph(nodes, edges)


def test_determinism_byte_identical_under_shuffle():
    irs = [_ir(i) for i in range(60)]
    a = to_json(_build(irs))
    b = to_json(_build(list(reversed(irs))))
    assert a == b


def test_scale_300_nodes_under_time_budget():
    irs = [_ir(i) for i in range(300)]
    t0 = time.perf_counter()
    g = _build(irs)
    elapsed = time.perf_counter() - t0
    assert elapsed < 10.0, f"build took {elapsed:.1f}s"
    assert len(g["nodes"]) == 300
