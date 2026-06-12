import json
from pathlib import Path
from pipeline.stage2.cli import build_nodes
from pipeline.stage2.edges import derive_edges

FIX = Path(__file__).parent / "fixtures" / "stage2"


def _all_edges(nodes):
    out = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i != j:
                out += derive_edges(a, b)
    return out


def _edge_set(edges):
    return {(e.src, e.dst, e.type) for e in edges}


def test_flashloan_swap_pricing_composition_is_connected():
    irs = json.loads((FIX / "composition_flashloan_swap_pricing.json").read_text())
    edges = _all_edges(build_nodes(irs))
    es = _edge_set(edges)
    # flashloan funds the swap (token USDC produced -> consumed as precondition)
    assert ("aave-v3.flash-loan", "curve.exchange", "sequential-dep") in es
    # donation and swap co-write pool balances (state-share, symmetric, single direction)
    share = [(s, d) for (s, d, t) in es if t == "state-share"]
    assert ("curve.exchange", "curve.virtual-price-donation") in share \
        or ("curve.virtual-price-donation", "curve.exchange") in share
    # the 3 mechanisms form one connected component
    nodes_in_edges = {n for (s, d, _) in es for n in (s, d)}
    assert {"aave-v3.flash-loan", "curve.exchange", "curve.virtual-price-donation"} <= nodes_in_edges


def test_five_motivating_examples_load_and_normalize(repo_root):
    from pipeline.stage2.normalize import normalize
    examples = sorted((repo_root / "ir-schema" / "examples").glob("0*.json"))
    assert len(examples) == 5
    for ex in examples:
        ir = json.loads(ex.read_text())
        ports = normalize(ir)  # must not raise
        assert ports is not None


def test_benchmark_event_composition_reconstructs_connected_subgraph():
    """G2-C: Harvest Finance 2020-10-26 share-price manipulation (subset_class=mixed).

    The attack chain: flashloan acquires USDC → curve exchange skews pool
    reserve ratio (inflating/deflating virtual_price) → vault deposit receives
    mis-priced shares → vault withdraw extracts profit after price restoration.

    Expected edges:
    - sequential-dep: flashloan → exchange  (USDC token produced → balance-check)
    - sequential-dep: exchange  → vault-deposit  (USDC token → balance-check)
    - state-share:    vault-deposit ↔ vault-withdraw  (both write HarvestVault.shares)
    All four mechanisms must appear in the edge set (connected subgraph).
    """
    irs = json.loads(
        (FIX / "composition_harvest-2020-10-26-share-price-manip.json").read_text()
    )
    edges = _all_edges(build_nodes(irs))
    es = _edge_set(edges)

    assert es, "expected at least one composability edge among the event's mechanisms"

    # flashloan funds the Curve swap via USDC sequential-dep
    assert ("harvest-finance.flashloan", "curve-finance.exchange", "sequential-dep") in es, \
        "flashloan should sequential-dep into curve exchange (USDC token)"

    # Curve exchange funds vault deposit via USDC sequential-dep
    assert ("curve-finance.exchange", "harvest-finance.vault-deposit", "sequential-dep") in es, \
        "curve exchange should sequential-dep into vault deposit (USDC token)"

    # deposit and withdraw share the same vault shares state (state-share, symmetric)
    share_pairs = [(s, d) for (s, d, t) in es if t == "state-share"]
    assert (
        ("harvest-finance.vault-deposit", "harvest-finance.vault-withdraw") in share_pairs
        or ("harvest-finance.vault-withdraw", "harvest-finance.vault-deposit") in share_pairs
    ), "vault-deposit and vault-withdraw should state-share over HarvestVault.shares"

    # connectivity: all 4 mechanism nodes appear in the edge set
    ids = {ir["id"] for ir in irs}
    nodes_in_edges = {n for (s, d, _) in es for n in (s, d)}
    assert ids <= nodes_in_edges, \
        f"disconnected mechanisms: {ids - nodes_in_edges}"
