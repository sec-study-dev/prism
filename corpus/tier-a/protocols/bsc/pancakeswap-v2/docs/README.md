# PancakeSwap V2 — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.pancakeswap.finance
- Source: https://github.com/pancakeswap/pancake-smart-contracts

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $1.823B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Standard xy=k AMM with 0.17% base fee to LPs and 0.03% to treasury, plus StableSwap pools using a Curve-style amplified bonding curve for stablecoin pairs. PancakeSwap V2 is BSC's largest AMM and the primary flash loan source for BSC-native arbitrage, with its BNB/stablecoin prices consumed as secondary oracles by Venus and Lista.
