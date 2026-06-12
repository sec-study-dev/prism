# Aave V3 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://aave.com/docs
- Technical paper: https://github.com/aave/aave-v3-core/tree/master/techpaper
- Source: https://github.com/aave/aave-v3-core

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $11.182B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Aave V3 uses a utilization-based kink interest model with separate LTV and liquidation threshold parameters. E-Mode (efficiency mode) allows correlated assets to borrow at near-100% LTV, collapsing the collateral margin. An integrated flash loan module allows borrowing any amount up to pool reserves within one transaction for a 0.05% fee.
