# Lista DAO — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.bsc.lista.org
- CDP docs: https://docs.bsc.lista.org/introduction/collateral-debt-position-lisusd
- Source: https://github.com/lista-dao/lista-dao

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $603.2M

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Lista DAO combines slisBNB liquid staking (BNB delegated to validators, rewards reflected via increasing slisBNB/BNB exchange rate) with lisUSD CDP minting backed by slisBNB collateral. A PSM module allows 1:1 lisUSD ↔ USDT/USDC swaps, and the collateral oracle reads slisBNB exchange rate directly from ListaStakeManager rather than an external oracle.
