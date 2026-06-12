# PancakeSwap Infinity — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.pancakeswap.finance/infinity
- Source: https://github.com/pancakeswap/pancake-smart-contracts

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $79.85M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
PancakeSwap Infinity is a hook-based singleton AMM (modeled on Uniswap V4) on BSC, supporting V2-style, V3-style, and custom hook-defined pool curves within the same contract. Flash accounting settles balances only at lock-scope end. Freshly deployed (2024), composability assumptions have not been fully stress-tested in production.
