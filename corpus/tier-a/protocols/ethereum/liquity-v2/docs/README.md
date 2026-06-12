# Liquity V2 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.liquity.org/v2
- Launch blog: https://www.liquity.org/blog/liquity-v2-is-live
- Source: https://github.com/liquity/bold

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $82.19M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Liquity V2 introduces user-set interest rates on individual troves, creating an on-chain interest rate market. BOLD is an immutable stablecoin (no admin keys). The redemption mechanism allows any BOLD holder to redeem against the lowest-interest-rate trove via a sorted linked list ordered by interest rate, making redemption arbitrage the sole peg stability mechanism.
