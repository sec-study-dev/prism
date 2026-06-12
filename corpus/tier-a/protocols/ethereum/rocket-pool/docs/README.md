# Rocket Pool — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.rocketpool.net
- Source: https://github.com/rocket-pool

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $534.67M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
rETH is a non-rebasing accumulating token with exchange rate rETH.getExchangeRate() increasing over time as staking rewards accrue. Node operators must post both ETH and RPL collateral (RPL is a protocol-level collateral asset), and the Saturn upgrade (Feb 2026) introduced MEV smoothing and new validator lifecycle hooks.
