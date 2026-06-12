import jsonschema


def test_schema_file_exists(mechanism_graph_schema_path):
    assert mechanism_graph_schema_path.exists()


def test_schema_is_valid_draft2020(mechanism_graph_schema):
    jsonschema.Draft202012Validator.check_schema(mechanism_graph_schema)


def test_minimal_graph_validates(mechanism_graph_schema):
    g = {
        "version": "stage2-v1",
        "nodes": [{
            "id": "aave-v3.flash-loan", "chain": "ethereum", "protocol": "aave-v3",
            "tags": ["flashloan"],
            "ports": {
                "produces": [{"kind": "token", "id": "DAI", "from": "tags:flashloan"}],
                "consumes": [],
            },
        }],
        "edges": [],
    }
    jsonschema.Draft202012Validator(mechanism_graph_schema).validate(g)


def test_unknown_top_level_field_rejected(mechanism_graph_schema):
    g = {"version": "stage2-v1", "nodes": [], "edges": [], "extra": 1}
    errs = list(jsonschema.Draft202012Validator(mechanism_graph_schema).iter_errors(g))
    assert errs


def test_unknown_edge_type_rejected(mechanism_graph_schema):
    g = {"version": "stage2-v1", "nodes": [],
         "edges": [{"src": "a.x", "dst": "b.y", "type": "bogus", "directed": True,
                    "chain": "ethereum", "shared_resources": [], "provenance": []}]}
    errs = list(jsonschema.Draft202012Validator(mechanism_graph_schema).iter_errors(g))
    assert errs


def test_missing_required_edge_field_rejected(mechanism_graph_schema):
    g = {"version": "stage2-v1", "nodes": [],
         "edges": [{"src": "a.x", "dst": "b.y", "type": "layering", "directed": True,
                    "chain": "ethereum", "shared_resources": []}]}  # 缺 provenance
    errs = list(jsonschema.Draft202012Validator(mechanism_graph_schema).iter_errors(g))
    assert errs
