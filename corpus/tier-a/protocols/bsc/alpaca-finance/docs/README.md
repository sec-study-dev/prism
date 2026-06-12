# Alpaca Finance — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.alpacafinance.org
- Source: https://github.com/alpaca-finance

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $45.23M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Alpaca Finance offers leveraged yield farming — users borrow from Alpaca lending vaults (ibTokens with ERC-4626-style exchange rate appreciation) to open 3–6x leveraged LP positions on PancakeSwap. The Automated Vault (Alpaca 2.0) auto-rebalances leveraged positions, and Alpaca's own liquidation engine handles undercollateralized leveraged positions.
