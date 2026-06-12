# Sky Lending (MakerDAO/Sky) — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://developers.sky.money
- User docs: https://docs.sky.money
- Source: https://github.com/makerdao

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $5.732B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Multi-collateral CDP with PSM (1:1 swap between USDS and approved stablecoins), D3M (Direct Deposit Module that autonomously mints/burns USDS into external lending protocols to control on-chain borrowing rates), and SSR/DSR Savings Rate applied to deposited USDS. The D3M makes Sky a direct rate-setter in Aave money markets.
