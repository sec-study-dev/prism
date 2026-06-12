# PRISM Tier-A Selection Rubric

A protocol qualifies for the PRISM corpus iff it satisfies **all four**
criteria below. Tier-A targets **≥10 Ethereum + ≥10 BSC** protocols
(total ≥20), with each chain aiming to cover all 10 priority categories
(see `categories.md`).

## Criteria (all required)

### C1. TVL threshold

- Ethereum: TVL ≥ **$50,000,000** at the chosen `snapshot_block`
- BSC: TVL ≥ **$20,000,000** at the chosen `snapshot_block`

Source of TVL: DefiLlama protocol page at the snapshot date, or equivalent
on-chain measurement.

### C2. Analyzability

- Source code is public (verified on Etherscan/BscScan or open repository)
- A non-trivial spec/whitepaper/documentation site exists (at least 5 pages
  of substantive content)

### C3. Mechanism distinctiveness

At least one of the following is true (free-form judgment; record in
`special_mechanism_summary`):

- Native stablecoin minting/redemption with custom collateral logic
- Rebase or auto-compounding share semantics
- Custom liquidation curve, auction, or partial-liquidation logic
- Lifecycle hook system (e.g., v4-style)
- Multi-layer wrapping (LST/LRT/CDP layering)
- Restaking or shared-security layering
- Non-trivial yield strategy with internal accounting (e.g., Pendle PT/YT)
- Bridge with custom message verification
- Custom ve/gauge or points emission curve
- Other distinctive mechanism — document why

### C3'. Combination potential (extension of C3, used to rank candidates)

Within candidates that satisfy C3, prefer those whose mechanisms have
**high a priori potential to combine with other DeFi mechanisms to form
profit strategies**. This is a judgment call grounded in DeFi mechanics
and financial intuition. Indicators that increase combination potential:

- Mechanism reads external state (oracle price, another protocol's share
  ratio, another protocol's reward index) — composability surface
- Mechanism returns value computed from a numerical invariant that other
  protocols may rely on (e.g., LRT exchange rate consumed by CDPs)
- Mechanism has accounting timing windows where other operations can
  insert between read and write (flash accounting, batch buffers)
- Mechanism allows "donation" patterns or unaccounted transfers that
  shift internal ratios
- Mechanism has emergency/admin paths that weaken normal constraints
- Mechanism is freshly introduced or rarely audited (novelty correlates
  with composability assumptions not yet stress-tested)

Record combination-potential reasoning in the candidate notes file
(below) for each selected protocol.

### C4. Category coverage

Tier-A target: **≥10 Ethereum + ≥10 BSC** (total ≥20). Each chain should
aim to cover all 10 priority categories. If a priority category has no
qualifying protocol on a given chain (e.g., LRT on BSC), that category
may be skipped on that chain — document the gap in the selection notes.

The 10 priority categories:

1. `dex-amm` — broadest historical attack surface
2. `dex-clmm` — concentrated-liquidity novelty
3. `lending` — core composability hub
4. `lst` — share-asset pricing baseline
5. `lrt` — structural layering exemplar
6. `yield-vault` — ERC-4626 + integrated yield
7. `stablecoin-cdp` — minting semantics
8. `perp` — funding-rate + index-price dynamics
9. `bridge` — message verification + token bookkeeping
10. `gauge-ve` — emission and reward accounting

Tier-B may include the remaining categories and additional protocols within
already-covered categories.

## Selection process

1. Candidate generation: for each priority category × each chain, list
   2–3 candidates satisfying C1–C3. Document for each candidate:
   - TVL (DefiLlama snapshot)
   - `special_mechanism_summary` (per C3)
   - Combination-potential reasoning (per C3')
   - Source links: repo, docs, audit reports
2. Curate: select the final Tier-A from the candidates, ensuring:
   - ≥10 Ethereum and ≥10 BSC
   - Each chain covers as many of the 10 priority categories as feasible
   - Within each (chain, category) cell, prefer higher combination
     potential over raw TVL when judgments differ
3. Record metadata for each selected protocol in
   `corpus/tier-a/protocols/<chain>/<protocol-slug>/metadata.json`
4. Download or reference primary documentation locally to
   `corpus/tier-a/protocols/<chain>/<protocol-slug>/docs/` for Stage 1 use
