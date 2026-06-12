# Pendle Finance — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.pendle.finance
- Academy: https://pendle.gitbook.io/pendle-academy
- Source: https://github.com/pendle-finance

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $1.124B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Pendle splits yield-bearing tokens into PT (Principal Token, zero-coupon bond redeemable 1:1 at maturity) and YT (Yield Token, streams all yield to holder until maturity). The AMM uses a custom asymptotic curve pricing PT at a time-value discount to par, and a SY (Standardized Yield) wrapper abstracts ERC-4626 and custom yield sources for uniform yield computation.
