# Convex Finance — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.convexfinance.com
- Source: https://github.com/convex-eth/platform

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $568.87M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Convex wraps Curve LP positions to distribute boosted CRV without requiring LPs to individually lock veCRV. cvxCRV is permanently locked CRV (no unlock); vlCVX (vote-locked CVX, 16-week lock) controls how Convex votes its ~53% veCRV stash, effectively controlling which Curve pools receive CRV emissions. A bribery market (Votium/Hidden Hand) prices gauge votes on-chain.
