import pytest
from pipeline.stage2.resources import Resource, canonical_id, same_resource, RESOURCE_KINDS


def test_unknown_kind_rejected():
    with pytest.raises(ValueError):
        Resource("bogus", "x")


def test_token_identity_case_and_whitespace_insensitive():
    a = Resource("token", "  0xAbC ", origin="deps[0]")
    b = Resource("token", "0xabc", origin="preconditions[1]")
    assert same_resource(a, b)
    assert canonical_id(a) == "token:0xabc"


def test_protocol_state_namespaced_not_equal_across_protocols():
    a = Resource("protocol-state", "aave-v3.Pool.reserves")
    b = Resource("protocol-state", "morpho-blue.Pool.reserves")
    assert not same_resource(a, b)


def test_kind_separates_identity():
    assert not same_resource(Resource("token", "x"), Resource("oracle", "x"))


def test_to_dict_emits_from_key_and_omits_empty_type():
    r = Resource("oracle", "chainlink-eth", origin="deps[2]")
    assert r.to_dict() == {"kind": "oracle", "id": "chainlink-eth", "from": "deps[2]"}
    r2 = Resource("token", "DAI", "uint256", "state_writes[0]")
    assert r2.to_dict()["solidity_type"] == "uint256"


def test_all_kinds_constructable():
    for k in RESOURCE_KINDS:
        Resource(k, "x")
