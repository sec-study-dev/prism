# Curve Finance — Documentation Index

Primary sources (used by Stage 1 for mechanism extraction):

- Official docs: https://docs.curve.finance
- Knowledge hub: https://resources.curve.finance
- Gauge contracts: https://docs.curve.finance/dao/gauges/overview
- Source: https://github.com/curvefi

Snapshot:
- Block: 22500000
- Reference date: 2026-05-25
- TVL (DefiLlama): $1.549B

Mechanism summary (see metadata.json `special_mechanism_summary` for canonical version):
Curve uses the StableSwap invariant for near-zero slippage on correlated assets. The ve/gauge system (veCRV time-lock, weekly gauge weight votes) directs CRV emissions to pools. crvUSD's LLAMMA continuously converts collateral to stablecoin as price falls, avoiding cliff liquidations and making its exchange rate readable by downstream protocols.
