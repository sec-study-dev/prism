# Lido — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.lido.fi
- V3 whitepaper draft: https://hackmd.io/@lido/v3-whitepaper
- Source: https://github.com/lidofinance

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $18.762B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
stETH is a rebasing token whose total supply increases daily as the oracle committee reports validator rewards, adjusting all holder balances proportionally. wstETH maintains constant balance with an increasing per-share exchange rate; wstETH.stEthPerToken() is the canonical pricing function consumed by Aave, Compound, MakerDAO, Pendle, and virtually every DeFi protocol accepting wstETH as collateral.
