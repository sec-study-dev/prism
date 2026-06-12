# DeFi Protocol Categories

This is the seed category set for PRISM Stage 0 corpus selection.
12-15 categories chosen to span the breadth of DeFi protocol designs we want
PRISM to cover. The category slug (lowercase kebab-case) is the value used
in protocol metadata `categories[]`.

| Slug | Name | Examples (illustrative) |
|---|---|---|
| `dex-amm` | AMM DEX | Uniswap v2, PancakeSwap, Balancer |
| `dex-clmm` | Concentrated-Liquidity DEX | Uniswap v3/v4, Trader Joe v2 |
| `lending` | Money Markets / Lending | Aave, Compound, Morpho, Venus |
| `lst` | Liquid Staking | Lido, Rocket Pool, Ankr |
| `lrt` | Liquid Restaking | EigenLayer + Renzo / Kelp / EtherFi |
| `yield-vault` | Yield Aggregators / Vaults (incl. ERC-4626) | Yearn, Pendle, Beefy |
| `stablecoin-cdp` | Stablecoin Minter (CDP) | MakerDAO, Liquity, Frax |
| `perp` | Perpetual Futures | GMX, dYdX, Level, ApolloX |
| `bridge` | Cross-chain Bridge | Across, Stargate, Synapse |
| `oracle` | Price Oracle | Chainlink, Pyth, Binance Oracle |
| `launchpad` | Token Launch / IDO | (TBD) |
| `gauge-ve` | Liquidity Gauging (ve/gauge) | Curve, Convex, Velodrome |
| `rwa` | Real-World Assets | Ondo, Centrifuge |
| `insurance` | Insurance / Cover | Nexus Mutual, Cover |

A protocol may belong to **one or more** categories. Multi-category
protocols (e.g., Pendle is both a yield-vault and a derivatives platform)
should list all applicable categories.

Tier-A target is **10 protocols, one per most-important category**.
Tier-B is the remaining ~50 protocols across all categories.
