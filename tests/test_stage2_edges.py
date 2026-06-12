from pipeline.stage2.edges import derive_edges, type_compatible
from pipeline.stage2.normalize import normalize
from pipeline.stage2.model import Node
from pipeline.stage2.resources import Resource


def _ir(**over):
    base = {
        "id": "proto.mech", "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "C.f"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "t", "status": "passing"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "L1"}],
    }
    base.update(over)
    return base


def _node(ir):
    return Node(id=ir["id"], chain=ir["chain"], protocol=ir["id"].split(".", 1)[0],
                tags=ir.get("tags", []), ports=normalize(ir), ir=ir)


def test_no_self_or_cross_chain_edges():
    a = _node(_ir(id="a.x", tags=["flashloan"], deps=[{"kind": "token-standard", "ref": "DAI"}]))
    assert derive_edges(a, a) == []
    b = _node(_ir(id="b.y", chain="bsc"))
    assert derive_edges(a, b) == []


def test_sequential_dep_flashloan_to_consumer():
    a = _node(_ir(id="aave.fl", tags=["flashloan"], deps=[{"kind": "token-standard", "ref": "DAI"}]))
    b = _node(_ir(id="curve.swap", deps=[{"kind": "token-standard", "ref": "DAI"}],
                  preconditions=[{"kind": "balance-check", "expression": "bal>=amt"}]))
    edges = derive_edges(a, b)
    seq = [e for e in edges if e.type == "sequential-dep"]
    assert seq and seq[0].src == "aave.fl" and seq[0].dst == "curve.swap"
    assert seq[0].directed is True
    assert any("token" == r.kind for r in seq[0].shared_resources)


def test_state_share_symmetric_single_direction():
    w = [{"contract": "Pool", "variable": "reserves", "purpose": "pool reserves"}]
    a = _node(_ir(id="curve.donate", state_writes=w))
    b = _node(_ir(id="curve.skew", state_writes=w))
    ab = [e for e in derive_edges(a, b) if e.type == "state-share"]
    ba = [e for e in derive_edges(b, a) if e.type == "state-share"]
    assert len(ab) == 1 and ba == []  # emitted once, on a.id < b.id only


def test_invariant_coupling_price_at_risk():
    a = _node(_ir(id="curve.donate",
                  state_writes=[{"contract": "Pool", "variable": "vp",
                                 "purpose": "virtual price per share"}],
                  invariants_at_risk=[{"expression": "vp monotonic",
                                       "risk_context": "donation", "scope": "protocol-wide"}]))
    b = _node(_ir(id="curve.reader",
                  state_reads=[{"contract": "Pool", "variable": "vp",
                                "purpose": "reads share price"}]))
    edges = [e for e in derive_edges(a, b) if e.type == "invariant-coupling"]
    assert edges and edges[0].shared_resources[0].kind == "price"


def test_layering_via_protocol_dep():
    a = _node(_ir(id="etherfi.lrt", deps=[{"kind": "protocol", "ref": "lido"}]))
    b = _node(_ir(id="lido.stake"))
    edges = [e for e in derive_edges(a, b) if e.type == "layering"]
    assert edges and edges[0].directed is True and edges[0].dst == "lido.stake"


def test_type_gate_blocks_incompatible():
    p = Resource("protocol-state", "x.C.v", "uint256")
    c = Resource("protocol-state", "x.C.v", "address")
    assert not type_compatible(p, c)
    assert type_compatible(Resource("token", "DAI"), Resource("token", "DAI", "address"))


def test_invariant_coupling_fires_when_bearer_has_larger_id():
    # reader has the SMALLER id; the invariant-bearer has the LARGER id.
    reader = _node(_ir(id="curve.aaa",
                       state_reads=[{"contract": "Pool", "variable": "vp",
                                     "purpose": "reads share price"}]))
    bearer = _node(_ir(id="curve.zzz",
                       state_writes=[{"contract": "Pool", "variable": "vp",
                                      "purpose": "virtual price per share"}],
                       invariants_at_risk=[{"expression": "vp monotonic",
                                            "risk_context": "donation",
                                            "scope": "protocol-wide"}]))
    # CLI calls both orderings; the coupling (bearer -> reader) must appear exactly once.
    edges = derive_edges(reader, bearer) + derive_edges(bearer, reader)
    ic = [e for e in edges if e.type == "invariant-coupling"]
    assert len(ic) == 1, f"expected exactly one invariant-coupling edge, got {len(ic)}"
    assert ic[0].src == "curve.zzz" and ic[0].dst == "curve.aaa"
