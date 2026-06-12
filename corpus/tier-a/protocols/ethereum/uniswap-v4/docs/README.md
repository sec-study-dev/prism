# Uniswap V4 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.uniswap.org/contracts/v4/overview
- Whitepaper: https://app.uniswap.org/whitepaper-v4.pdf
- Source: https://github.com/Uniswap/v4-core

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $501.44M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Uniswap V4 is a singleton architecture with lifecycle hooks (before/afterSwap, before/afterAddLiquidity, etc.) and flash accounting via EIP-1153 transient storage. Balances are only settled at lock-scope end, enabling mid-execution token borrowing without collateral. Supports native ETH and dynamic per-transaction fees set by hook contracts.
