# PancakeSwap V3 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.pancakeswap.finance/v3
- Source: https://github.com/pancakeswap/pancake-v3-contracts

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $260.34M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Concentrated liquidity (Uniswap V3 fork) with custom fee tiers (0.01%, 0.05%, 0.25%, 1%) and per-position liquidity tracking. BSC's 3-second block time makes TWAP manipulation cheaper than Ethereum; TWAP output is consumed by Venus Protocol as a secondary oracle, meaning sustained price deviation can influence Venus liquidation thresholds.
