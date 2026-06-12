# Synthetix V3 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.synthetix.io
- Source: https://github.com/Synthetixio/synthetix-v3

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $40.97M (sub-threshold; accepted by user decision)

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Synthetix V3 uses a modular vault-pool-market architecture. Perps V3 settles via async orders (keeper-filled at next available oracle price), and uses a velocity-based funding rate model where funding rate momentum accumulates over time based on market skew rather than a simple skew-proportional formula.
