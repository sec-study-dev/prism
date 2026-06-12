# Level Finance — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.level.finance
- Source: https://github.com/LevelFinance

Snapshot:
- Block: 50000000
- Reference date: 2026-05-25
- TVL: ~$4M (approximate, post-2023-incident decline; sub-threshold, accepted by user decision)

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Level Finance is a fully on-chain GMX-style perpetual DEX. Liquidity is split into
senior/mezzanine/junior risk tranches over one shared multi-asset pool (LLP); traders
take leveraged positions directly against the pool. Tranche share prices all read the
same underlying reserves, a dynamic fee model prices the pool's net skew, and a Level
Oracle supplies the mark prices used for settlement and liquidation. Selected as the
BSC perp Tier-A representative (replacing ApeX, whose perp engine is off-chain/CLOB and
not extractable as verified on-chain source).
