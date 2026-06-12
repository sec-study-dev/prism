import json
import pytest
from pipeline.stage2.loader import load_mechanisms, LoadError


def _valid_ir(mech_id):
    return {
        "id": mech_id, "chain": "ethereum",
        "trigger": {"kind": "function-call", "entry_point": "C.f"},
        "state_reads": [], "state_writes": [],
        "preconditions": [], "postconditions": [],
        "invariants_held": [], "invariants_at_risk": [],
        "deps": [], "tags": ["function-callable"],
        "poc": {"path": "x", "test_name": "t", "status": "passing"},
        "provenance": [{"kind": "code", "url_or_path": "x", "section_or_lines": "L1"}],
    }


def _write(db, chain, slug, mech_id, ir):
    d = db / chain / slug / mech_id
    d.mkdir(parents=True)
    (d / f"{mech_id}.json").write_text(json.dumps(ir))
    (d / f"{mech_id}.metrics.json").write_text('{"mechanism_id": "%s"}' % mech_id)
    return d


def test_missing_db_returns_empty(tmp_path):
    assert load_mechanisms(tmp_path / "nope") == []


def test_loads_ir_and_skips_metrics(tmp_path):
    _write(tmp_path, "ethereum", "aave-v3", "aave-v3.flash", _valid_ir("aave-v3.flash"))
    out = load_mechanisms(tmp_path)
    assert len(out) == 1 and out[0]["id"] == "aave-v3.flash"


def test_invalid_ir_raises(tmp_path):
    _write(tmp_path, "ethereum", "x", "x.bad", {"id": "x.bad"})  # missing required fields
    with pytest.raises(LoadError):
        load_mechanisms(tmp_path)


def test_sorted_order(tmp_path):
    import json as _json
    # path order (a_proto/... before z_proto/...) is the OPPOSITE of id order,
    # so this only passes if results are sorted by id, not by file path.
    (tmp_path / "a_proto" / "s").mkdir(parents=True)
    (tmp_path / "a_proto" / "s" / "m.json").write_text(_json.dumps(_valid_ir("z.last")))
    (tmp_path / "z_proto" / "s").mkdir(parents=True)
    (tmp_path / "z_proto" / "s" / "m.json").write_text(_json.dumps(_valid_ir("a.first")))
    assert [m["id"] for m in load_mechanisms(tmp_path)] == ["a.first", "z.last"]


def test_malformed_json_raises(tmp_path):
    d = tmp_path / "ethereum" / "x" / "x.broken"
    d.mkdir(parents=True)
    (d / "x.broken.json").write_text("{ not valid json")
    with pytest.raises(LoadError):
        load_mechanisms(tmp_path)
