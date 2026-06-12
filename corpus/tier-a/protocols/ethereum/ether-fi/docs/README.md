# ether.fi — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.ether.fi
- Source: https://github.com/etherfi-protocol

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $3.751B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
eETH is a rebasing LRT tracking ETH staking plus EigenLayer restaking rewards; weETH is the accumulating wrapper with exchange rate weETH.getEETHByWeETH(). The protocol supports multi-layer wrapping (ETH → eETH → weETH), which can be deposited into lending protocols as collateral, creating a deep composability chain where changes at any layer propagate downstream.
