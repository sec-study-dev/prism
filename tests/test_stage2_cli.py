import json
import jsonschema
from pipeline.stage2.cli import build, build_nodes


def _ir(mech_id, chain="ethereum", **over):
    base = {
        "id": mech_id, "chain": chain,
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


def test_build_nodes_sets_protocol_and_ports():
    nodes = build_nodes([_ir("aave-v3.flash")])
    assert nodes[0].protocol == "aave-v3"
    assert nodes[0].ports is not None


def test_build_end_to_end_produces_valid_graph(tmp_path, monkeypatch, mechanism_graph_schema):
    irs = [
        _ir("aave-v3.flash", tags=["flashloan"], deps=[{"kind": "token-standard", "ref": "DAI"}]),
        _ir("curve.swap", deps=[{"kind": "token-standard", "ref": "DAI"}],
            preconditions=[{"kind": "balance-check", "expression": "bal>=amt"}]),
        _ir("pcs.swap", chain="bsc"),
    ]
    monkeypatch.setattr("pipeline.stage2.cli.load_mechanisms", lambda db: irs)
    g = build(tmp_path)
    jsonschema.Draft202012Validator(mechanism_graph_schema).validate(g)
    assert len(g["nodes"]) == 3
    seq = [e for e in g["edges"] if e["type"] == "sequential-dep"]
    assert any(e["src"] == "aave-v3.flash" and e["dst"] == "curve.swap" for e in seq)
    # no cross-chain edges to the bsc node
    assert all(e["chain"] == "ethereum" for e in g["edges"])
