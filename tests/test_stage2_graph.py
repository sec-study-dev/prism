import json
import jsonschema
from pipeline.stage2.graph import build_graph, to_json, to_dot, GRAPH_VERSION
from pipeline.stage2.model import Node, Edge, Ports
from pipeline.stage2.resources import Resource


def _n(i):
    return Node(id=i, chain="ethereum", protocol=i.split(".")[0], tags=["t"],
                ports=Ports(produces=[Resource("token", "DAI", origin="tags:flashloan")],
                            consumes=[]), ir={})


def test_build_graph_shape_and_version():
    g = build_graph([_n("b.y"), _n("a.x")], [])
    assert g["version"] == GRAPH_VERSION
    assert [n["id"] for n in g["nodes"]] == ["a.x", "b.y"]  # sorted by id


def test_serialization_is_deterministic_under_reorder():
    nodes = [_n("a.x"), _n("b.y")]
    e1 = Edge("a.x", "b.y", "layering", True, "ethereum", [], ["p"])
    g_forward = to_json(build_graph(nodes, [e1]))
    g_reordered = to_json(build_graph(list(reversed(nodes)), [e1]))
    assert g_forward == g_reordered  # byte-identical


def test_output_validates_against_schema(mechanism_graph_schema):
    g = build_graph([_n("a.x")], [Edge("a.x", "a.x", "state-share", False, "ethereum", [], [])])
    jsonschema.Draft202012Validator(mechanism_graph_schema).validate(g)


def test_dot_has_chain_cluster_and_edge():
    g = build_graph([_n("a.x"), _n("b.y")],
                    [Edge("a.x", "b.y", "sequential-dep", True, "ethereum", [], [])])
    dot = to_dot(g)
    assert "subgraph cluster_ethereum" in dot
    assert '"a.x" -> "b.y"' in dot


def test_duplicate_edges_collapsed():
    # same (src, dst, type, resources) but different provenance -> one edge
    e1 = Edge("a.x", "b.y", "layering", True, "ethereum", [], ["from deps[0]"])
    e2 = Edge("a.x", "b.y", "layering", True, "ethereum", [], ["from preconditions[0]"])
    g = build_graph([_n("a.x"), _n("b.y")], [e1, e2])
    assert len([x for x in g["edges"] if x["type"] == "layering"]) == 1
