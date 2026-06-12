# THENA — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://thena.fi/docs
- Source: https://github.com/ThenafiBNB

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL (DefiLlama): $4.36M (sub-threshold; accepted by user decision)

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
THENA implements Solidly-derived ve(3,3) on BSC: veTHE is a vote-escrowed NFT (representing locked THE plus time). veTHE holders vote weekly on gauge weights to direct THE emissions, with 80% of protocol fees going to veTHE voters. The bribery equilibrium makes vote-buying economically rational for protocols that can extract more than 80% of a pool's fees.
