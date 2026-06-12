# Balancer V3 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.balancer.fi
- V3-specific docs: https://docs-v3.balancer.fi
- Source: https://github.com/balancer/balancer-v3-monorepo

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): ~$500M+

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Balancer V3 redesigns the Vault to separate accounting from pool logic, wrapping ERC-4626 assets at Vault level. Flash accounting settles balances only at end of a batch operation callback, enabling within-batch uncollateralized borrowing. Lifecycle hooks allow custom logic at swap/liquidity operation points.
