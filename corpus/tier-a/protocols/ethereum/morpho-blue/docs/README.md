# Morpho Blue — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.morpho.org
- Source: https://github.com/morpho-org/morpho-blue

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $3.843B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Morpho Blue is a singleton contract with isolated, immutable markets fixed at creation by five parameters (collateral, loan asset, oracle, IRM, LLTV). Interest accrues as shares that appreciate relative to assets (ERC-4626-style), and each market settles independently with no post-deployment governance changes possible.
