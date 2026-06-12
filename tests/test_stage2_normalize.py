from pipeline.stage2.normalize import normalize
from pipeline.stage2.resources import canonical_id


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


def _ids(rs):
    return {canonical_id(r) for r in rs}


def test_oracle_and_token_and_flashloan_deps():
    ir = _ir(deps=[
        {"kind": "oracle", "ref": "chainlink-eth-usd"},
        {"kind": "token-standard", "ref": "USDC"},
        {"kind": "flashloan-provider", "ref": "aave-v3"},
    ])
    p = normalize(ir)
    assert _ids(p.consumes) == {
        "oracle:chainlink-eth-usd", "token:usdc", "flashloan:aave-v3"}


def test_flashloan_tag_produces_loaned_tokens():
    ir = _ir(tags=["flashloan"], deps=[{"kind": "token-standard", "ref": "DAI"}])
    p = normalize(ir)
    assert "token:dai" in _ids(p.produces)


def test_state_write_share_price_is_price_resource():
    ir = _ir(state_writes=[{"contract": "Vault", "variable": "totalAssets",
                            "purpose": "drives share price per share"}])
    p = normalize(ir)
    assert "price:proto.vault.totalassets" in _ids(p.produces)


def test_state_write_plain_is_protocol_state():
    ir = _ir(state_writes=[{"contract": "Pool", "variable": "config",
                            "purpose": "stores admin config"}])
    p = normalize(ir)
    assert "protocol-state:proto.pool.config" in _ids(p.produces)


def test_state_read_price_is_oracle():
    ir = _ir(state_reads=[{"contract": "Pool", "variable": "latestAnswer",
                           "purpose": "reads oracle price feed"}])
    p = normalize(ir)
    assert "oracle:proto.pool.latestanswer" in _ids(p.consumes)


def test_precondition_balance_check_consumes_token_with_precond_origin():
    ir = _ir(deps=[{"kind": "token-standard", "ref": "WETH"}],
             preconditions=[{"kind": "balance-check",
                             "expression": "balanceOf(this) >= amount"}])
    p = normalize(ir)
    weth = [r for r in p.consumes if r.id == "WETH" and r.origin.startswith("preconditions")]
    assert weth, "expected a precondition-origin token consume"
