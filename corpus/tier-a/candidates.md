# Tier-A Candidate Pool

**Generated:** 2026-05-25
**Snapshot reference:** DefiLlama as of 2026-05-25, TVL figures from DefiLlama protocol pages fetched live during this session
**Methodology:** Per priority category × per chain, 2–3 candidates; ranked by combination-potential × TVL × mechanism distinctiveness. Selection criteria: see `corpus/selection-rubric.md` §C1–C4 + §C3'.

---

## Ethereum

### dex-amm

#### 1. Curve Finance
- **TVL**: $1.549B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/curvefi
- **Docs**: https://docs.curve.finance (primary), https://resources.curve.finance (knowledge hub)
- **Audits**: Trail of Bits (2020), MixBytes (multiple rounds 2021–2024), ChainSecurity (crvUSD, 2023), multiple community audits on specific pools
- **Recent incidents**: July 2023 — Vyper 0.2.15/0.2.16/0.3.0 reentrancy bug exploited across factory pools, total ~$70M drained (partially recovered to ~$20M net loss). Curve founder Michael Egorov had overleveraged CRV positions that triggered cascading liquidation concerns but were resolved.
- **Special mechanism (C3)**: Curve uses a StableSwap invariant (A × Σ xᵢ + D = A × n^n × D + D^(n+1) / n^n ∏ xᵢ) for near-zero slippage on correlated assets. Separately, it has a custom ve/gauge system (veCRV time-lock, weekly gauge weight votes that direct CRV emissions). crvUSD adds LLAMMA — a continuous liquidation AMM that converts collateral to stablecoin gradually as price falls, avoiding cliff liquidations.
- **Combination potential (C3')**: Extremely high. veCRV votes redirect CRV emissions across all gauges — any protocol that accumulates veCRV (like Convex) can extract economic rent by influencing reward flows. The StableSwap amplification parameter A is governed and adjustable, creating price-impact timing windows. Donation patterns to Curve pools (sending tokens directly to pool contracts) shift the internal D invariant without triggering the normal deposit path, which can enable price manipulation in thinly curated pools. crvUSD's LLAMMA continuously adjusts the oracle band, making its exchange rate readable and exploitable by protocols that consume it as a price source.
- **Categories**: dex-amm, dex-clmm (crvUSD markets), stablecoin-cdp, gauge-ve

#### 2. Balancer V3
- **TVL**: ~$500M+ on Ethereum (DefiLlama, 2026-05-25; Balancer V3 TVL page)
- **Repo**: https://github.com/balancer/balancer-v3-monorepo
- **Docs**: https://docs.balancer.fi (primary), https://docs-v3.balancer.fi (V3 specific)
- **Audits**: Certora (formal verification, 2024), Trail of Bits (2024), Spearbit (2024) — V3 launched late 2024 after extensive audit campaign
- **Recent incidents**: None publicly disclosed for V3. V2 had minor issues but no major exploit.
- **Special mechanism (C3)**: Balancer V3 introduces a redesigned Vault with separating accounting from pool logic: pools are now "yield-bearing vaults" that wrap ERC-4626 assets at the Vault level. The Vault performs internal flash accounting (balances checked only at end of a batch operation), and any imbalance from within the batch can be resolved by the callback. Hooks allow custom logic at swap/add-liquidity/remove-liquidity lifecycle points, similar to Uniswap v4 but for weighted/stable pool configurations.
- **Combination potential (C3')**: The ERC-4626 integration at Vault level means Balancer pools can hold yield-bearing tokens (stETH, aTokens, etc.) and the Vault's share math uses the external exchange rates of those tokens. Any divergence between the external vault's reported price and market price creates a sandwichable window. Flash accounting means the Vault doesn't settle until callback end — protocols can borrow pool reserves without collateral within the callback, similar to a flashloan but spanning any pool operation.
- **Categories**: dex-amm, gauge-ve (via Balancer/Aura veBAL system)

---

### dex-clmm

#### 1. Uniswap V4
- **TVL**: $501.44M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/Uniswap/v4-core
- **Docs**: https://docs.uniswap.org/contracts/v4/overview (primary), https://app.uniswap.org/whitepaper-v4.pdf (whitepaper)
- **Audits**: Trail of Bits (2024), OpenZeppelin (2024), Spearbit (2024), community contest on Code4rena (2024) — extensive pre-launch audit campaign
- **Recent incidents**: None publicly disclosed as of 2026-05-25 (launched late 2024).
- **Special mechanism (C3)**: Uniswap V4 is a singleton architecture (all pools in one contract) with lifecycle hooks: before/afterSwap, before/afterAddLiquidity, before/afterRemoveLiquidity, before/afterInitialize — arbitrary external code executed at each pool action. Flash accounting using EIP-1153 transient storage: balances are only checked at the end of a "lock" scope, meaning mid-execution the protocol can owe tokens without collateral. Pools support native ETH (no WETH wrapper). Dynamic fees: hook contracts can set swap fees per-transaction.
- **Combination potential (C3')**: The highest-potential Ethereum CLMM for PRISM. Hook contracts execute arbitrary logic at swap lifecycle points — a hook can read Aave's current borrow rate, re-price the pool dynamically, or trigger a lending action mid-swap. The flash accounting via transient storage creates a window where tokens can be "borrowed" from any pool mid-transaction without collateral as long as they are returned by lock-end. This is structurally more powerful than a standard flashloan because it spans pool operations. Freshly deployed (late 2024), composability assumptions have not been fully stress-tested in production.
- **Categories**: dex-clmm, dex-amm

#### 2. Uniswap V3
- **TVL**: $1.001B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/Uniswap/v3-core
- **Docs**: https://docs.uniswap.org/contracts/v3/overview (primary), https://uniswap.org/whitepaper-v3.pdf (whitepaper)
- **Audits**: Trail of Bits (2021), ABDK (2021), samczsun (informal review 2021)
- **Recent incidents**: None publicly disclosed (protocol has been live since May 2021 without major exploits; well-audited).
- **Special mechanism (C3)**: Concentrated liquidity (capital allocated within user-defined price ticks). Tick-level liquidity accounting: global accumulators updated per-tick-cross. Fee growth tracked per liquidity unit using feeGrowthGlobal0X128 and feeGrowthGlobal1X128. TWAP oracle is maintained in-slot-0 using cumulative price (not spot), making it manipulation-resistant but readable by other protocols.
- **Combination potential (C3')**: The TWAP oracle is consumed by Aave, Compound, and many others as a secondary price feed — any manipulation of the spot price over a sufficiently long TWAP window can affect oracle-dependent liquidation thresholds. The fee-growth accounting uses separate per-position checkpoints, creating conditions where fee amounts can be read by external contracts and used to construct positions with predictable future fee accruals (targeted by MEV). Substantial liquidity means realistic flash-loan amounts; largest source of on-chain flashloan liquidity for ETH/stablecoin pairs.
- **Categories**: dex-clmm, dex-amm

---

### lending

#### 1. Aave V3
- **TVL**: $11.182B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/aave/aave-v3-core
- **Docs**: https://aave.com/docs (primary), https://github.com/aave/aave-v3-core/tree/master/techpaper (technical paper)
- **Audits**: ABDK (2022), Trail of Bits (2022), PeckShield (2022), SigmaPrime (2022), Certora formal verification (2022), Spearbit (2024 for V4 prep), OpenZeppelin (V4 2025–2026)
- **Recent incidents**: November 2023 — critical vulnerability in v2 periphery disclosed via bug bounty; some markets temporarily paused; $56K periphery tip-jar hack (minimal). No exploit of core v3 lending logic. Ongoing monitoring for CRV liquidation cascade (2023) — Aave's governance approved bad-debt coverage from treasury.
- **Special mechanism (C3)**: Variable-rate interest model with utilization-based kink. Health factor accounting uses LTV and liquidation threshold (two separate parameters). Aave v3 adds E-Mode (efficiency mode) that allows correlated assets to borrow at near-100% LTV, effectively collapsing the collateral margin. Flashloan module integrated at protocol level: any amount up to pool reserves can be borrowed within one transaction for a fee. Price isolation modes per asset. Portal (cross-chain collateral supply).
- **Combination potential (C3')**: As the largest Ethereum lending protocol, Aave's reserve state (available liquidity per token) is read by every routing protocol and many liquidation bots. E-Mode creates near-zero margin windows where the same transaction that borrows can also trigger a liquidation on an adjacent position, enabling self-liquidation paths. The oracle price used for liquidations (Chainlink + fallback) has a two-block staleness window, during which price changes from block N-1 may not yet be reflected. Flashloan premium (currently 0.05%) is charged but leaves no collateral requirement mid-transaction — the entire pool is borrowable without collateral.
- **Categories**: lending

#### 2. Morpho Blue
- **TVL**: $3.843B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/morpho-org/morpho-blue
- **Docs**: https://docs.morpho.org (primary)
- **Audits**: OpenZeppelin (Oct 2023), Spearbit (2023), Cantina (2024), Pessimistic (2024 for vaults)
- **Recent incidents**: None publicly disclosed for Morpho Blue core. A Morpho vault (Morpho Steakhouse USDC) was impacted by downstream collateral issues in 2025 but no protocol-level exploit.
- **Special mechanism (C3)**: Morpho Blue is a singleton smart contract with isolated, immutable markets (five parameters fixed at creation: collateral, loan asset, oracle, IRM, LLTV). No governance can change market parameters post-creation. Market state is minimal (borrow shares, total borrow assets, total supply assets) — each market settles independently. Interest accrues as shares that appreciate relative to assets (like ERC-4626 vault shares). No protocol-level fee unless explicitly set per market.
- **Combination potential (C3')**: The immutable market parameters mean oracle manipulation is directly translatable to position manipulation — the oracle for each market is read at liquidation time with no TWAP delay. Borrow shares appreciate over time (auto-compounding interest accrual), meaning the total borrow assets grows per second — this timing-sensitive value can be read by other contracts to predict exact liquidation prices. Markets are fully permissionless to create, allowing anyone to set up a market with a custom oracle that Morpho will trust for liquidations. MetaMorpho vaults (allocators) can shift capital between Morpho markets — this reallocation changes utilization and rates instantaneously.
- **Categories**: lending

#### 3. Sky Lending (MakerDAO / Sky Protocol)
- **TVL**: $5.732B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/makerdao
- **Docs**: https://developers.sky.money (primary), https://docs.sky.money, https://makerdao.com/da/whitepaper/ (original MCD whitepaper)
- **Audits**: ChainSecurity (2023 Endgame), Trail of Bits (multiple rounds 2019–2024), Certora (formal verification ongoing), CertiK (2024 Sky rebrand)
- **Recent incidents**: None publicly disclosed for core CDP logic since MCD launch (2019). USDS has a freeze function — considered a centralization risk by some. The 2022 DAI/USDC depeg episode during USDC depegging showed PSM vulnerability (DAI could lose its peg via PSM drain).
- **Special mechanism (C3)**: Multi-collateral CDP with Peg Stability Module (PSM): allows 1:1 swap between USDS and approved stablecoins at near-zero fee. Direct Deposit Module (D3M): allows Sky to autonomously mint/burn DAI/USDS into external lending protocols (e.g., Aave) to control on-chain borrowing rates. Savings Rate (SSR/DSR) applied to deposited USDS. Stability fee adjusted by governance, with immediate effect on all CDPs.
- **Combination potential (C3')**: The D3M module makes Sky a direct rate-setter in Aave's money markets — if Sky adjusts D3M target rate, Aave's USDS supply changes instantly. The PSM is a zero-slippage swap path between USDS and USDC/USDT; any price discrepancy between on-chain DEX pricing and PSM rate creates arbitrage. Governance-controlled stability fee changes affect all open CDPs simultaneously — this is oracle-independent rate adjustment that can be anticipated if governance proposals are visible before execution.
- **Categories**: stablecoin-cdp, lending

---

### lst

#### 1. Lido
- **TVL**: $18.762B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/lidofinance
- **Docs**: https://docs.lido.fi (primary), https://hackmd.io/@lido/v3-whitepaper (V3 whitepaper draft)
- **Audits**: Sigma Prime (2020, 2021, 2022, 2024), Quantstamp (2020, 2021), MixBytes (multiple rounds 2021–2024), Ackee (CSM 2024), ChainSecurity (2024)
- **Recent incidents**: None publicly disclosed for core staking. May 2022 — a bug in oracle committee logic caused a minor reward reporting delay (no funds at risk). 2022 stETH depeg to ~0.94 ETH during Terra/3AC crisis (market pricing, not protocol failure). Lido V3 CSM (Community Staking Module) launched 2024 — no incidents.
- **Special mechanism (C3)**: stETH is a rebasing token: total supply increases daily as oracle committee reports validator rewards. The rebase adjusts all stETH holder balances proportionally — this means ERC-20 transfer events are emitted only for transfers, not for rebase increases, which breaks standard accounting assumptions. wstETH (wrapped stETH) maintains constant balance with increasing per-share exchange rate — the exchange rate `wstETH.stEthPerToken()` is the canonical Lido pricing function consumed by virtually every DeFi protocol.
- **Combination potential (C3')**: The stETH/wstETH exchange rate is consumed by Aave, Compound, MakerDAO, Pendle, and essentially every protocol that accepts wstETH as collateral or yield source. A manipulation of the Lido oracle committee report (even briefly) affects collateral ratios across the entire DeFi stack. The rebasing mechanism means stETH behaves differently than non-rebasing tokens in protocols that account for ERC-20 balance snapshots. The daily oracle report that triggers the rebase is a public event — positions that anticipate the rebase can front-run the price impact across downstream protocols.
- **Categories**: lst

#### 2. Rocket Pool
- **TVL**: $534.67M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/rocket-pool
- **Docs**: https://docs.rocketpool.net (primary)
- **Audits**: Sigma Prime (Saturn 2024, Houston 2024), Consensys Diligence (Atlas 2023, Houston 2023), Chainsafe (Houston 2024)
- **Recent incidents**: May 2022 — two oDAO nodes compromised; ETH and RPL stolen from node accounts (protocol-level funds unaffected). January 2023 Atlas audit found critical reentrancy in node distributor; patched before deployment.
- **Special mechanism (C3)**: rETH is a non-rebasing accumulating token: exchange rate `rETH.getExchangeRate()` increases over time as staking rewards accrue. Node operators must put up ETH + RPL collateral (RPL is a protocol-level collateral asset). Saturn upgrade (Feb 2026) introduces MEV smoothing and new validator lifecycle hooks. The rETH/ETH exchange rate is updated via oracle committee similar to Lido but with a different validator set and update cadence.
- **Combination potential (C3')**: rETH exchange rate updates are visible on-chain and updated less frequently than market prices — the window between updates creates predictable arbitrage if the on-chain rate diverges from market rate. rETH is used as collateral in Aave/MakerDAO with LTV based on this rate — rate-update timing affects liquidation thresholds. The RPL collateral requirement means node operators have RPL price exposure that affects their ability to maintain validators; RPL price manipulation could cause validator exits, affecting rETH supply.
- **Categories**: lst

---

### lrt

#### 1. ether.fi
- **TVL**: $3.751B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/etherfi-protocol
- **Docs**: https://docs.ether.fi (primary)
- **Audits**: Sigma Prime, Pashov Audit Group, Code4rena contest (2024) — full list at docs.ether.fi/security
- **Recent incidents**: April 2026 — Bridge Security Hardening event following industry exploit (Kelp/KernelDAO $292M bridge drain). ether.fi deprecated weETH bridging on several low-TVL chains (Scroll, Swell, Bera, zkSync, Mode, Blast, Morph, Sonic) effective June 2026. Cash product migrated from Scroll to OP Mainnet (April 2026, $220M TVL migration).
- **Special mechanism (C3)**: eETH is a rebasing LRT that tracks ETH staking + EigenLayer restaking rewards. weETH (wrapped eETH) has an accumulating exchange rate `weETH.getEETHByWeETH()`. The protocol issues validator keys non-custodially (node operators keep the validator withdrawal credentials). Revenue sources: ETH staking (3–4%), EigenLayer AVS rewards (variable), ether.fi Cash (DeFi vault products). Multi-layer wrapping: ETH → eETH (Lido-style LST) → weETH (accumulating wrapper) → potentially deposited into lending protocols.
- **Combination potential (C3')**: weETH exchange rate is consumed by Aave, Spark, and other lending protocols for collateral valuation. The AVS reward component is variable and not predictable in advance — protocols that price weETH using only the ETH staking rate component undervalue the token during high-AVS-reward periods. Multi-layer wrapping (ETH → eETH → weETH → Aave collateral) creates a deep composability chain where a change at any layer propagates. April 2026 Kelp exploit showed that bridge-level LRT attacks can cause mass withdrawals across the entire LRT sector — indicating restaking LRT protocols have correlated systemic risk.
- **Categories**: lrt, lst

#### 2. EigenCloud (EigenLayer)
- **TVL**: $6.618B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/Layr-Labs
- **Docs**: https://docs.eigenlayer.xyz (primary)
- **Audits**: Sigma Prime (2023), Trail of Bits (2023), Dedaub (2024), multiple community audits
- **Recent incidents**: April 2026 — KernelDAO's Kelp protocol (built on EigenLayer) suffered $292M bridge exploit. EigenLayer core contracts not directly exploited but triggered ~$5.4B in withdrawals across restaking sector. EigenLayer as base layer unaffected; Kelp bridge contract had a vulnerability.
- **Special mechanism (C3)**: EigenLayer enables "restaking" — ETH already staked on Ethereum's consensus layer (or LST tokens) can be pledged additionally to Actively Validated Services (AVSs). Operators opt into AVSs and can be slashed by the AVS slasher contract under conditions defined by that AVS. Slashing events cascade: the operator's restaked position is reduced, which reduces the security guarantee to all AVSs they serve. The restaking shares track a `podOwnerShares` value per operator.
- **Combination potential (C3')**: EigenLayer's slashing mechanism is external-state-reading by design — AVS contracts determine when to slash, meaning any protocol that misconfigures its slashing conditions can be triggered by an adversarial restaker. The delegation model allows any address to receive delegated restaking shares from users — an operator's share count changes based on delegations from many users, creating race conditions on share accounting. AVS rewards are distributed off-chain and claimed on-chain, creating timing windows between off-chain reward computation and on-chain claiming.
- **Categories**: lrt

---

### yield-vault

#### 1. Pendle Finance
- **TVL**: $1.124B on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/pendle-finance
- **Docs**: https://docs.pendle.finance (primary), https://pendle.gitbook.io/pendle-academy (academy)
- **Audits**: Ackee (V2 2022), ChainSecurity (V2 core 2023), Dedaub (multiple 2023–2024), Code4rena contests. Full list: https://docs.pendle.finance/Security
- **Recent incidents**: None publicly disclosed. Certified Integrity Score of 91/100 per DeFiSafety.
- **Special mechanism (C3)**: Pendle splits yield-bearing tokens into Principal Tokens (PT) and Yield Tokens (YT). PT is a zero-coupon bond redeemable 1:1 at maturity. YT streams all yield from underlying to holder until maturity. The AMM for PT uses a custom asymptotic curve that prices PT as a discount to par. The AMM's exchange rate between PT and underlying asset moves toward 1 as maturity approaches (time-value-of-money priced on-chain). PT/YT splitting is via a SY (Standardized Yield) wrapper that abstracts ERC-4626 + custom yield sources.
- **Combination potential (C3')**: The PT price is a time-sensitive discount to par — Pendle's AMM is the on-chain "interest rate oracle" for many yield assets. Protocols that consume Pendle's implied yield rate (e.g., to set borrow rates) rely on this AMM's spot price, which is manipulable via large swaps. YT streams yield to its holder — a flash-loan that acquires YT briefly can collect yield accrued during the loan window (though this is constrained by YT pricing). The SY wrapper reads external exchange rates (e.g., wstETH/ETH) to compute how much yield to stream — any divergence between the SY-reported yield rate and market rate creates an arbitrage between PT and its underlying. Post-maturity PT redeems at exactly 1:1 — this is a hard pricing anchor that can be used in multi-leg strategies combining pre/post-maturity states.
- **Categories**: yield-vault

#### 2. Yearn Finance V3
- **TVL**: $126.7M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/yearn/yearn-vaults-v3
- **Docs**: https://docs.yearn.fi (primary)
- **Audits**: Chainsecurity (V3 2023), Ackee (V3 2023), yAudit (internal, ongoing)
- **Recent incidents**: Yearn V1 had a 2021 DAI vault exploit ($11M). V2 and V3 have not had major incidents. 2023 V2 exploit on yvUSDT ($10M) — not V3 contracts.
- **Special mechanism (C3)**: Yearn V3 vaults are fully ERC-4626 compliant. Each vault is an allocator that delegates capital to multiple strategies (also ERC-4626). Strategies report their assets back via `report()`, triggering share-price updates. The idle float between strategy allocation and actual deployment creates windows where vault price-per-share can be stale. `totalAssets()` aggregates across all strategies, any of which may have unreported gains/losses.
- **Combination potential (C3')**: ERC-4626's `convertToShares(assets)` and `convertToAssets(shares)` functions use totalAssets() which can change between blocks based on underlying strategy performance. Protocols that take a snapshot of share price and use it in the same transaction as a deposit/withdraw may experience slippage in their favor or against. The allocator pattern means strategy rebalancing can temporarily inflate or deflate the vault's liquid assets, creating timing windows where large withdrawals can disproportionately draw from remaining liquid strategies. Direct donations to vault (sending underlying tokens to contract address) increase totalAssets() without minting shares, inflating existing share price.
- **Categories**: yield-vault

---

### stablecoin-cdp

#### 1. Sky Lending (already listed under lending — see above)
*(Sky satisfies both lending and stablecoin-cdp; listed here for cross-reference)*
- See Sky Lending entry under §lending above.
- **Categories**: stablecoin-cdp, lending

#### 2. Liquity V2
- **TVL**: $82.19M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/liquity/bold
- **Docs**: https://docs.liquity.org/v2 (primary), https://www.liquity.org/blog/liquity-v2-is-live
- **Audits**: Dedaub (2024), Trail of Bits (2024), Code4rena contest (2024)
- **Recent incidents**: None publicly disclosed for V2. V1 had a 2021 front-end phishing (not contract-level).
- **Special mechanism (C3)**: Liquity V2 introduces user-set interest rates on individual troves (CDPs), creating an on-chain interest rate market. BOLD is the immutable stablecoin (no admin keys). Redemption mechanism: any BOLD holder can redeem against the lowest-interest-rate trove (incentivizing users to set market-competitive rates). The redemption mechanism uses sorted linked lists of troves ordered by interest rate — any redemption walks this list.
- **Combination potential (C3')**: The sorted trove list by interest rate is publicly readable — a bot can front-run interest rate changes to position a trove for or against redemption. Redemptions are an arbitrage mechanism: if BOLD trades below $1, anyone can redeem BOLD for collateral at $1 value, profiting from the peg. This creates a direct link between Liquity's collateral ratios and BOLD's market price. Since BOLD is immutable (no admin), the only stability mechanism is this redemption arbitrage — protocols that depend on BOLD's peg stability are fully exposed to the arbitrage dynamics without any admin fallback. User-set interest rates are adjustable, creating a game-theoretic competition among trove owners to avoid being the lowest-rate redemption target.
- **Categories**: stablecoin-cdp

#### 3. Frax Finance
- **TVL**: $287.95M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/FraxFinance
- **Docs**: https://docs.frax.finance (primary)
- **Audits**: Trail of Bits (2021), Certora (formal verification, 2022), Code4rena contests
- **Recent incidents**: 2022 — depeg concerns during Terra crash; FRAX held its peg due to AMO mechanisms. No protocol-level exploit of core contracts.
- **Special mechanism (C3)**: FRAX uses Algorithmic Market Operations (AMO) controllers — separate contracts authorized to mint/burn FRAX and deploy it in external protocols. AMOs can supply FRAX to Curve pools, Aave, or Uniswap — creating FRAX liquidity without requiring collateral deposits for each unit. The collateral ratio (CR) is algorithmically adjusted based on FRAX market price. Fraxlend has its own time-weighted oracle mechanism with variable interest rates.
- **Combination potential (C3')**: AMOs mint FRAX autonomously — any external contract that reads FRAX supply as an indicator of system health will see AMO-driven expansions that do not correspond to user collateral. Fraxlend's oracle has a "time-weighted average" that is adjustable by governance — this oracle is read by the Fraxlend liquidation module, creating a governance-adjustable liquidation price anchor. The AMO architecture allows FRAX to be deployed across multiple protocols simultaneously, meaning a single AMO misconfiguration can drain multiple venues.
- **Categories**: stablecoin-cdp

---

### perp

#### 1. Synthetix V3
- **TVL**: $40.97M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/Synthetixio/synthetix-v3
- **Docs**: https://docs.synthetix.io (primary)
- **Audits**: Iosiro (V2, 2022), OpenZeppelin (V3 2024), multiple Code4rena contests
- **Recent incidents**: Synthetix founder Kain Warwick acknowledged in late 2025 that V3 represents a fresh rewrite with limited production battle-testing. Synthetix returned to Ethereum mainnet from OP Mainnet in early 2026. No major exploit of V3 on Ethereum disclosed.
- **Special mechanism (C3)**: Synthetix V3 uses a modular vault + pool + market architecture. Vaults hold collateral; pools combine vaults and connect to markets; markets handle position accounting. Perps V3 runs order matching off-chain (for speed) but settles on-chain via "async orders" — a user requests an order, it is filled by a keeper at the next available oracle price, then settled on-chain. Funding rate is computed as a velocity model (rate changes over time based on skew), not a simple skew-proportional model. This means a funding rate "momentum" accumulates.
- **Combination potential (C3')**: The async order model means there is a window between order submission and fill — during this window, the oracle price (Pyth off-chain price) can move, creating a known latency arbitrage. The velocity funding rate model creates predictable funding rate trajectories that can be exploited by protocols or bots that take offsetting positions across time. V3's Pool-Market-Vault architecture separates risk-bearing (vault) from position-taking (market), meaning vault depositors take aggregate market risk — any strategy that can create a skewed market also reduces vault collateral health.
- **Categories**: perp

#### 2. GMX V2 (Perps)
- **TVL**: $187.73M on Arbitrum (also on Avalanche; no Ethereum mainnet deployment — but Arbitrum is EVM-equivalent) (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/gmx-io/gmx-synthetics
- **Docs**: https://docs.gmx.io (primary)
- **Audits**: ABDK (2021 V1), SigmaPrime (2022 V2), Code4rena contests (2023, 2024)
- **Recent incidents**: None publicly disclosed for V2 core. V1 had 2022 "price keeper" manipulation attempt that was caught.
- **Special mechanism (C3)**: GMX V2 uses isolated GM pools (one per market, e.g., ETH/USDC). Each GM pool is a two-sided AMM that provides both spot swap liquidity and perpetual position liquidity. Funding rate is two-directional: when long OI exceeds short OI, longs pay shorts and vice versa. An "impact pool" is maintained to absorb price impact from large trades — this pool grows when users pay positive impact fees and shrinks when users receive negative impact fees. Positions are marked-to-market using Chainlink price feeds with 30-second staleness allowance.
- **Combination potential (C3')**: The GM pool share price is determined by PnL of open positions plus pool's spot balance — a large directional position that closes profitably extracts from the pool's LP assets. The 30-second oracle staleness window means a price move of >30s is settleable at an old price, creating a latency arbitrage for fast-moving assets. The impact pool is a public variable; protocols can read it and predict whether their next trade will pay or receive impact fee, and if positive, extract from the impact pool via staged trades.
- **Categories**: perp

---

### bridge

#### 1. Stargate Finance (V1+V2 combined)
- **TVL**: $93.39M total ($24.6M Ethereum + $21.94M BSC) (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/stargate-protocol
- **Docs**: https://stargateprotocol.gitbook.io/stargate/ (V1), https://stargate.finance/docs (V2)
- **Audits**: Quantstamp (V1 2022), Certora (V1 formal verification 2022), Dedaub (V2 2024)
- **Recent incidents**: 2023 — general class of LayerZero-dependent bridges under scrutiny. No direct Stargate exploit. August 2025 — Wormhole submitted $110M acquisition bid for Stargate, suggesting strategic vulnerability/transition phase. V1 had liquidity fragmentation issues.
- **Special mechanism (C3)**: Stargate V1 uses unified liquidity pools (Delta algorithm) — liquidity across chains is balanced via credit accounting without locking to specific pairs. V2 adds AIPM (AI-driven Planning Module) for routing and Hydra for batched transaction settlement. STG/veSTG governance controls pool parameters (fees, credits). V2 OFT (Omnichain Fungible Token) standard allows tokens to exist natively on any chain without wrapped representation.
- **Combination potential (C3')**: The Delta credit algorithm in V1 tracks "credits" per chain — a large deposit on one chain inflates credits and allows large withdrawals on another. This cross-chain credit asymmetry can be exploited by coordinating deposits and withdrawals across blocks. The veSTG gauge system (V1) allows stakers to direct pool rewards — any entity accumulating veSTG can shift liquidity incentives across chains, affecting which pools are most liquid. Stargate's pool contracts hold significant native stablecoin balances — any oracle failure in the liquidity accounting can allow draining the delta credit pool.
- **Categories**: bridge

#### 2. Across Protocol
- **TVL**: $27.81M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/across-protocol
- **Docs**: https://docs.across.to (primary)
- **Audits**: OpenZeppelin (V2 2022), multiple internal reviews; zero exploits since 2021 launch
- **Recent incidents**: None publicly disclosed. Clean security record across $30B+ cumulative volume since launch.
- **Special mechanism (C3)**: Across uses a hub-and-spoke architecture: one Hub Pool on Ethereum, Spoke Pools on each destination chain. Intent-based routing: users state intent (deposit on chain A, receive on chain B), relayers front the funds immediately, then claim reimbursement via the Hub Pool after UMA optimistic oracle verification. Single-sided liquidity: LPs only deposit on the Hub Pool (Ethereum mainnet), not per-chain pools. UMA optimistic oracle: disputes settle after a challenge window — invalid fills can be disputed and refunded to the pool.
- **Combination potential (C3')**: The optimistic oracle challenge window creates a timing attack surface: a relayer who can delay the challenge period can fill invalid orders. Hub Pool liquidity is single-sided Ethereum — any protocol that reads Hub Pool balance to estimate bridge capacity will see the full liquidity even if much of it is already committed to outstanding relayer fills not yet settled. Relayer competition means fills happen at current market rate — a protocol that manipulates the destination-chain token price during the fill can front-run the relayer's settlement at a predictable rate.
- **Categories**: bridge

---

### gauge-ve

#### 1. Curve Finance (gauge/veCRV system — see also §dex-amm above)
*(Curve Finance is listed under dex-amm; listing here as primary gauge-ve candidate)*
- **TVL**: $1.549B on Ethereum (all Curve pools, DefiLlama 2026-05-25)
- **Repo**: https://github.com/curvefi/curve-dao-contracts (gauge contracts)
- **Docs**: https://docs.curve.finance/dao/gauges/overview (gauge docs)
- **Audits**: See dex-amm entry above
- **Recent incidents**: See dex-amm entry above
- **Special mechanism (C3)**: Curve's gauge system distributes CRV emissions to liquidity pools via gauge weight votes. veCRV holders vote weekly on gauge weights; the weight determines what fraction of weekly CRV emission each gauge receives. Boost: LPs with veCRV get up to 2.5x emission boost — a user with zero veCRV earns 1x CRV, while a user with sufficient veCRV earns 2.5x. Gauge controller tracks accumulated weights over time, not just current-week votes.
- **Combination potential (C3')**: Convex Finance holds ~53% of all veCRV — this concentration means Convex (and CVX holders who vote on Convex's gauge allocation) effectively controls which Curve pools receive CRV. Any protocol that holds CVX can rent Curve gauge weight — this creates a bribery market (via Votium/Hidden Hand) where protocols pay CVX holders to direct emissions to their pools. The boost mechanism depends on the ratio of LP's veCRV to total veCRV locked at a gauge — this ratio changes per-block as veCRV decays, creating predictable moments where boost drops below threshold, which external bots can monitor and trade around.
- **Categories**: gauge-ve, dex-amm, stablecoin-cdp

#### 2. Convex Finance
- **TVL**: $568.87M on Ethereum (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/convex-eth/platform
- **Docs**: https://docs.convexfinance.com (primary)
- **Audits**: MixBytes (2021), multiple Code4rena contests, internal reviews
- **Recent incidents**: None publicly disclosed. 2022 — class of "governance takeover" concerns raised in the context of Curve wars but not exploited against Convex directly.
- **Special mechanism (C3)**: Convex wraps Curve LP positions to distribute boosted CRV without requiring individual LPs to lock veCRV. cvxCRV is a CRV wrapper that is locked in Convex forever (no unlock) in exchange for enhanced yield. vlCVX (vote-locked CVX) controls how Convex votes its veCRV stash. The vlCVX 16-week lock means vote allocation is committed for 16 weeks — any bribe paid now affects gauge weights for 16 weeks forward.
- **Combination potential (C3')**: cvxCRV is perpetually locked — the cvxCRV/CRV peg depends on secondary market demand. If cvxCRV depegs significantly below CRV, Convex's internal accounting is unaffected but all downstream protocols that accept cvxCRV at 1:1 parity face bad debt. The 16-week vlCVX lock creates predictable governance epochs — protocols building strategies around Curve gauge weights can model which pools will be over- or under-weighted for the next 16 weeks. The Votium/Hidden Hand bribery market prices gauge votes — this on-chain market can be read to infer protocol demand for specific pool liquidity, creating information asymmetry profitable for gauge-aware strategies.
- **Categories**: gauge-ve

---

## BSC

### dex-amm

#### 1. PancakeSwap AMM (V2/Legacy)
- **TVL**: $1.823B on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/pancakeswap/pancake-smart-contracts
- **Docs**: https://docs.pancakeswap.finance (primary)
- **Audits**: CertiK (2020, 2021, 2022), Peckshield (multiple rounds)
- **Recent incidents**: None publicly disclosed for core AMM contracts. PancakeSwap's tokenomics underwent major revamp (Tokenomics 3.0, April 2025) deprecating veCAKE/gauge system. 2021 — various flash loan attacks on BSC ecosystem (not PancakeSwap core; third-party forks using similar code were hit).
- **Special mechanism (C3)**: Standard xy=k AMM with fee distribution to LPs (0.17% base fee, 0.03% to treasury). StableSwap pools use Curve-style amplified bonding curve for stablecoin pairs. PancakeSwap has position manager hooks (Infinity system — see dex-clmm below). The large stablecoin pool liquidity on BSC makes PancakeSwap the primary flashloan source for BSC-native arbitrage.
- **Combination potential (C3')**: As BSC's largest AMM by TVL, PancakeSwap is the primary price reference for BNB/stablecoin pairs and is consumed by Venus, Lista, and other BSC lending protocols as a secondary oracle. Flashloan amounts available are proportional to pool reserves — with $1.8B TVL, realistic single-transaction borrows of $100M+ are available, enabling large-scale liquidation or arbitrage strategies on BSC. The 0.20% fee per hop creates predictable price impact curves that can be reverse-engineered to model optimal flashloan sizes.
- **Categories**: dex-amm

#### 2. Curve DEX on BSC
- **TVL**: ~$990M on BSC (DefiLlama, 2026-05-25 — "BSC: $990.5M" from API data)
- **Repo**: https://github.com/curvefi (same codebase deployed on BSC)
- **Docs**: https://docs.curve.finance (primary)
- **Audits**: See Ethereum Curve entry (same contracts deployed to BSC)
- **Recent incidents**: July 2023 — Ellipsis Finance (Curve fork on BSC) lost $78K in same Vyper reentrancy incident that hit Curve's factory pools on Ethereum. Curve's own BSC pools were affected in the same event.
- **Special mechanism (C3)**: Same StableSwap invariant as Ethereum Curve. The BSC deployment controls major stablecoin liquidity on BSC (USDT/BUSD/USDC). Curve's 3pool on BSC is the benchmark stablecoin pool.
- **Combination potential (C3')**: Curve BSC pools are the primary stablecoin liquidity source, meaning manipulation of Curve's BSC pool pricing affects all downstream stablecoin pricing on BSC. Same LLAMMA/donation attack vectors as on Ethereum apply here. Cross-chain: Curve's BSC liquidity can be used in conjunction with Ethereum via bridges, creating multi-chain arbitrage windows in the Curve/Stargate stack.
- **Categories**: dex-amm

---

### dex-clmm

#### 1. PancakeSwap AMM V3
- **TVL**: $260.34M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/pancakeswap/pancake-v3-contracts
- **Docs**: https://docs.pancakeswap.finance/v3 (primary)
- **Audits**: CertiK (V3 2023), Peckshield (V3 2023)
- **Recent incidents**: None publicly disclosed for V3.
- **Special mechanism (C3)**: Concentrated liquidity (Uniswap V3 fork with modifications). Custom fee tiers (0.01%, 0.05%, 0.25%, 1%). Position Manager tracks per-position liquidity. BSC block time (3s) means TWAP manipulation is cheaper than Ethereum (shorter blocks = cheaper to sustain price deviation). BSC's lower gas cost enables more complex position management strategies.
- **Combination potential (C3')**: BSC's 3-second block time means TWAP oracle update frequency is higher but also means flashloan attack windows are smaller. TWAP price consumed by Venus Protocol (BSC's largest lending protocol) — any sustained price deviation for 1–2 minutes on PancakeSwap V3 can influence Venus oracle prices. LP positions have non-linear fee accrual near current tick — protocols providing liquidity "just-in-time" (JIT liquidity) can front-run large swaps and capture essentially all fees, a pattern well-known on Ethereum Uniswap V3 but also applicable here.
- **Categories**: dex-clmm

#### 2. PancakeSwap Infinity (Hook-based AMM)
- **TVL**: $79.85M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/pancakeswap/pancake-smart-contracts (infinity subdirectory)
- **Docs**: https://docs.pancakeswap.finance/infinity (primary)
- **Audits**: CertiK (2024), ongoing security reviews
- **Recent incidents**: None publicly disclosed (recently launched).
- **Special mechanism (C3)**: PancakeSwap Infinity is a hook-based AMM (modeled on Uniswap V4's hook system) deployed on BSC. Pools can have hook contracts that modify swap behavior, fee logic, or liquidity operations. Singleton architecture. Flash accounting within lock scopes. Multiple pool types: V2-style, V3-style, and custom hook-defined curves within the same contract.
- **Combination potential (C3')**: Freshly deployed (2024) with limited production battle-testing — composability assumptions not yet stress-tested. Hook contracts are external code that executes during swap; any BSC protocol that integrates Infinity pools may be exposed to hook-defined behavior that changes without notice. Flash accounting creates the same within-lock borrowing surface as Uniswap V4 but on BSC with lower gas costs, making attack strategies cheaper to execute.
- **Categories**: dex-clmm, dex-amm

---

### lending

#### 1. Venus Protocol (Core Pool + Isolated Pools)
- **TVL**: $1.188B on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/VenusProtocol
- **Docs**: https://docs-v4.venus.io (primary)
- **Audits**: CertiK (2020, 2021, 2022, 2024), Peckshield (multiple), OpenZeppelin (V4 2023), Fairyproof (2022)
- **Recent incidents**: 2023 — XVS oracle manipulation incident; attacker manipulated XVS price on PancakeSwap TWAP to borrow against inflated XVS collateral. ~$6M drained. Venus responded by implementing stricter oracle requirements and Chainlink integration. 2021 — multiple incidents with BSC ecosystem flash loan attacks, some affecting Venus.
- **Special mechanism (C3)**: Venus combines Compound-style money markets with its own stablecoin VAI minting. vTokens (vBNB, vBTC, etc.) are the interest-bearing wrappers. VAI is minted against vToken collateral with a custom stability fee. Venus Prime is a yield-boost program (non-transferable NFT + staked XVS = boosted APY on selected markets). Peg Stability Module (PSM) allows 1:1 VAI ↔ USDT/USDC swaps.
- **Combination potential (C3')**: Venus is the dominant lending protocol on BSC — liquidation bots monitor Venus health factors against PancakeSwap/Chainlink prices. The XVS oracle incident demonstrates that BSC's TWAP-based oracle is manipulable with sufficient capital and short timeframe. Venus Prime's boosted APY is assigned to staked XVS — a protocol that can stake XVS in Venus Prime while also taking the opposite position on XVS in a perp DEX creates a basis trade. The PSM creates a 1:1 swap anchor that can be drained if VAI's market price diverges — similar to the MakerDAO PSM attack vector.
- **Categories**: lending, stablecoin-cdp

#### 2. Aave V3 on BSC
- **TVL**: $170.12M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/aave/aave-v3-core (same codebase as Ethereum)
- **Docs**: https://aave.com/docs (primary)
- **Audits**: Same audit reports as Ethereum Aave V3; no BSC-specific audit issues disclosed
- **Recent incidents**: None publicly disclosed for BSC deployment specifically.
- **Special mechanism (C3)**: Same as Ethereum Aave V3 (see above). On BSC: uses Chainlink oracles with BSC-specific feeds. Supports BNB, BTCB, ETH, USDT, USDC as major markets. E-Mode applies for correlated BSC assets (e.g., stablecoin E-Mode).
- **Combination potential (C3')**: Aave V3 on BSC creates a cross-protocol arbitrage surface with Venus — if Venus and Aave offer different borrow rates for the same asset, a recursive borrowing strategy (borrow from one, supply to other, repeat) is rate-arbitrageable. Aave's flashloan on BSC uses the same mechanism as Ethereum — unlimited same-block borrowing — and can be composed with PancakeSwap liquidity for large-scale BSC DEX arbitrage.
- **Categories**: lending

---

### lst

#### 1. Lista Liquid Staking (slisBNB)
- **TVL**: $603.2M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/lista-dao/lista-dao (inferred from lista.org GitHub organization)
- **Docs**: https://docs.bsc.lista.org (primary)
- **Audits**: Peckshield (2023), Slowmist (2023), Fairyproof (2024) — audit list at docs.bsc.lista.org/security
- **Recent incidents**: None publicly disclosed for slisBNB core contracts.
- **Special mechanism (C3)**: slisBNB is the yield-bearing liquid staking token for BNB, appreciating against BNB in line with staking APR. BNB is distributed to multiple BNB Chain validators; rewards are aggregated and reflected via an increasing slisBNB/BNB exchange rate. Revenue split: 5% of staking yield goes to Lista DAO; 50% of DAO revenue goes to veLISTA holders. The ListaStakeManager contract handles the BNB validator delegation, unbonding (7-day period), and slisBNB minting/burning.
- **Combination potential (C3')**: slisBNB is consumed by Lista's own CDP system (lisUSD minting uses slisBNB as collateral) and by Venus as collateral — so slisBNB exchange rate errors propagate to both lending and CDP protocols. The 7-day BNB unbonding period creates a structural liquidity premium for slisBNB sellers who need immediate BNB, exploitable via secondary market arbitrage. veLISTA holders earn 50% of protocol revenue — a flash-acquisition of veLISTA combined with a large slisBNB stake could capture a disproportionate revenue share for a single epoch.
- **Categories**: lst

#### 2. Ankr (ankrBNB on BSC)
- **TVL**: $731K on BSC per DefiLlama (main page); note: Ankr's staking page shows higher staked BNB value — DefiLlama may be undercounting ⚠️ sub-threshold by DefiLlama measure
- **Repo**: https://github.com/Ankr-network
- **Docs**: https://www.ankr.com/docs/staking-for-developers/smart-contract-api/bnb-api/ (BSC staking API docs)
- **Audits**: Beosin (2022), PeckShield (2022)
- **Recent incidents**: October 2022 — Ankr's aBNBc token (now ankrBNB) was exploited via a private key compromise of a deployer, allowing infinite minting of aBNBc tokens; ~$5M drained on BSC. Attacker also drained Helio Protocol (now Lista DAO predecessor) which used aBNBc as collateral. Ankr has since migrated to ankrBNB with enhanced key management.
- **Special mechanism (C3)**: ankrBNB uses an accumulating exchange rate model (non-rebasing). ankrBNB can be minted by staking BNB, with validators across multiple node operators.
- **Combination potential (C3')**: The 2022 exploit demonstrated that ankrBNB's exchange rate can be manipulated via unauthorized minting — protocols that used ankrBNB as collateral (like the then-Helio Protocol) were immediately affected. Sub-threshold TVL by DefiLlama; listed as ⚠️ candidate.
- **Categories**: lst

---

### lrt

> **Coverage gap for BSC LRT**: As of 2026-05-25, there is no BSC-native protocol that qualifies as a true LRT (liquid restaking token) with TVL ≥ $20M on BSC and a mechanism comparable to EigenLayer LRTs on Ethereum. BNB Chain does not have a native restaking layer equivalent to EigenLayer. KernelDAO's "Kernel" product (shared security on BNB Chain, $660M TVL per their blog) is conceptually similar, but their DefiLlama entry (`kerneldao`) shows $1.73M on BSC — the stated $660M is likely their Ethereum (Kelp/rsETH) TVL aggregated. This cell is a **gap** — see Coverage Gaps section.

---

### yield-vault

#### 1. Alpaca Finance
- **TVL**: $45.23M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/alpaca-finance
- **Docs**: https://docs.alpacafinance.org (primary)
- **Audits**: PeckShield (2021), CertiK (2021), Inspex (2022)
- **Recent incidents**: 2022 — Alpaca Finance suffered a $4.5M exploit via a governance attack on a BSC vault. The exploit used flash loans to manipulate voting power in a proposal that allowed unauthorized withdrawals. Core lending was unaffected.
- **Special mechanism (C3)**: Alpaca Finance offers leveraged yield farming — users borrow from Alpaca's lending vaults (ibTokens: ibBNB, ibBUSD, etc.) and use the borrowed funds to open leveraged LP positions on PancakeSwap. ibTokens accumulate interest (ERC-4626-style exchange rate appreciation). The Automated Vault product (Alpaca 2.0) manages these leveraged positions with auto-rebalancing. Liquidation of leveraged positions is handled by Alpaca's own liquidation engine.
- **Combination potential (C3')**: The undercollateralized loan for leveraged farming creates a recursive capital structure: one borrow enables 3–6x leveraged LP, and each LP position accrues fees that partially service the debt. The liquidation engine triggers when the equity value of the LP position falls below threshold — monitoring ibToken exchange rates and PancakeSwap LP prices creates a predictable liquidation cascade trigger. ibToken exchange rates (read from Alpaca lending vaults) can be read by external protocols — a flash loan that temporarily reduces ibToken exchange rate could trigger mass liquidations of leveraged positions.
- **Categories**: yield-vault, lending

#### 2. Pendle Finance on BSC
- **TVL**: $13.34M on BSC (DefiLlama, 2026-05-25) ⚠️ sub-threshold ($20M BSC threshold); listed as candidate
- **Repo**: https://github.com/pendle-finance (same codebase as Ethereum)
- **Docs**: https://docs.pendle.finance (primary)
- **Audits**: See Ethereum Pendle entry
- **Recent incidents**: None publicly disclosed on BSC
- **Special mechanism (C3)**: Same PT/YT mechanism as Ethereum. On BSC, Pendle wraps slisBNB and other BSC yield-bearing assets for fixed/variable yield trading.
- **Combination potential (C3')**: Same as Ethereum Pendle. On BSC, slisBNB PT/YT markets create a direct link to Lista's liquid staking rate — any manipulation of slisBNB exchange rate affects Pendle's AMM pricing and therefore PT/YT valuations on BSC. Sub-threshold TVL — listed as ⚠️ candidate pending TVL growth.
- **Categories**: yield-vault

#### 3. Beefy Finance on BSC
- **TVL**: $6.68M on BSC (DefiLlama, 2026-05-25) ⚠️ sub-threshold; listed as candidate
- **Repo**: https://github.com/beefyfinance
- **Docs**: https://docs.beefy.finance (primary)
- **Audits**: Defisec (2021), multiple strategy audits ongoing; vault contracts are standardized
- **Recent incidents**: None on core Beefy contracts. 2022 — Beefy had several exploited strategies (third-party protocol integrations, not Beefy core).
- **Special mechanism (C3)**: Beefy is an auto-compounding yield aggregator. Each "vault" is an ERC-4626 wrapper around a specific liquidity mining strategy. Compounding happens via a public `harvest()` function — anyone can call it and gets a small gas rebate. The harvest interval is market-driven (anyone can trigger it when the gas cost is covered by pending rewards). Strategies earn from PancakeSwap LP fees + CAKE rewards, then sell CAKE for underlying and re-add liquidity.
- **Combination potential (C3')**: The public `harvest()` call creates a front-running opportunity — MEV bots can monitor pending reward accumulation and time harvest calls to extract maximum CAKE rewards before the compound. ERC-4626 share price inflates continuously between harvests — protocols that snapshot share price at harvest time get maximum value, while those snapshotting just before harvest underestimate vault value. Sub-threshold TVL — listed as ⚠️ candidate.
- **Categories**: yield-vault

---

### stablecoin-cdp

#### 1. Lista CDP (lisUSD)
- **TVL**: $403.35M on BSC (DefiLlama, 2026-05-25)
- **Repo**: https://github.com/lista-dao (inferred; Lista DAO GitHub)
- **Docs**: https://docs.bsc.lista.org/introduction/collateral-debt-position-lisusd (primary)
- **Audits**: Peckshield (2023), Slowmist (2023), Fairyproof (2024)
- **Recent incidents**: October 2022 — predecessor "Helio Protocol" was impacted by the Ankr aBNBc exploit: attackers minted unlimited aBNBc, used it to borrow HAY (now lisUSD predecessor) from Helio at oracle price, then sold HAY. ~$15M drained. Lista DAO redesigned after this incident with stricter oracle and collateral requirements.
- **Special mechanism (C3)**: lisUSD is a CDP stablecoin backed by slisBNB (and other collateral). The PSM module allows 1:1 swap between lisUSD and USDT/USDC. D3M module (Direct Minting Integration, inspired by MakerDAO) allows lisUSD to be minted directly into lending protocols. The oracle for slisBNB uses an on-chain exchange rate from ListaStakeManager — not an external oracle.
- **Combination potential (C3')**: The collateral oracle for slisBNB uses the on-chain exchange rate directly from ListaStakeManager — this is an internal rate that can only change slowly (validator rewards). However, this also means liquidation triggers are driven by BNB market price (via ListaStakeManager's underlying BNB) rather than a fast-updating Chainlink feed, creating a potential price oracle lag. The PSM's direct swap path between lisUSD and USDC creates an arbitrage: if lisUSD depegs, the PSM drains until rebalanced by DAO governance. The October 2022 exploit history demonstrates that any protocol accepting slisBNB derivatives as collateral is vulnerable to underlying LST manipulation.
- **Categories**: stablecoin-cdp, lending

#### 2. Venus Protocol (VAI minting — see also lending above)
*(Venus is listed under lending; listing here for stablecoin-CDP cross-reference)*
- See Venus Protocol entry under §lending above.
- **Categories**: stablecoin-cdp, lending

---

### perp

#### 1. ApeX Protocol (BSC deployment)
- **TVL**: $4.07M on BSC (DefiLlama, 2026-05-25) ⚠️ sub-threshold; listed as candidate
- **Repo**: https://github.com/ApeX-Protocol
- **Docs**: https://apex-protocol.gitbook.io/apex-protocol-docs (primary)
- **Audits**: Secure3 (2022), Dedaub (2023)
- **Recent incidents**: None publicly disclosed.
- **Special mechanism (C3)**: ApeX uses a CLOB-style perpetuals architecture with off-chain order matching and on-chain settlement. Trades settle on StarkEx (zkRollup) or BSC directly. 50% of trading fees are used for APEX token buybacks. The protocol runs an "omni" model accepting multiple collaterals.
- **Combination potential (C3')**: The 50% fee buyback creates a direct link between trading volume and APEX token price — a protocol that generates high volume (even via wash trading) also causes APEX buybacks, which could be exploited in conjunction with APEX options or perps on another platform. Off-chain order matching + on-chain settlement creates the standard async order gap (submission vs. fill window). Sub-threshold TVL — listed as ⚠️ candidate; BSC perp ecosystem lacks a high-TVL protocol meeting C1.
- **Categories**: perp

> **Coverage note for BSC Perp**: No BSC-native perp DEX currently has TVL ≥ $20M as of 2026-05-25. Level Finance ($2.7K TVL), MYX Finance (~$200K TVL), ApeX ($4M) all fall below threshold. The BSC perp ecosystem has largely migrated to Hyperliquid, dYdX, and Arbitrum/GMX. See Coverage Gaps section.

---

### bridge

#### 1. Stargate Finance on BSC
- **TVL**: $21.94M on BSC (DefiLlama, 2026-05-25) — just above $20M threshold
- **Repo**: https://github.com/stargate-protocol (same codebase)
- **Docs**: https://stargate.finance/docs (primary)
- **Audits**: See Ethereum Stargate entry
- **Recent incidents**: See Ethereum Stargate entry
- **Special mechanism (C3)**: Same as Ethereum deployment. BSC Stargate pools hold USDT/USDC/BUSD liquidity for cross-chain transfers. The Delta algorithm balances credits across all connected chains — BSC credits affect Ethereum and vice versa.
- **Combination potential (C3')**: Same as Ethereum. BSC's higher transaction volume and lower cost make cross-chain credit attacks via Stargate cheaper to execute from BSC side. The veSTG gauge weight voting (V1) also applies to BSC pool rewards — veSTG accumulated on Ethereum affects BSC pool fee splits.
- **Categories**: bridge

#### 2. cBridge (Celer Network) on BSC
- **TVL**: $3.13M on BSC (DefiLlama, 2026-05-25) ⚠️ sub-threshold
- **Repo**: https://github.com/celer-network
- **Docs**: https://cbridge-docs.celer.network (primary)
- **Audits**: CertiK (2022), Peckshield (2022)
- **Recent incidents**: 2023 — Celer DNS hijacking incident (front-end attack, not contract); $128K drained from users who approved malicious transactions. Core contracts unaffected.
- **Special mechanism (C3)**: cBridge uses two models: pool-based liquidity (LP pools on each chain, with state guardian network validating transfers) and mint/burn (for native project tokens). State Guardian Network (SGN) is a Cosmos-based side chain that validates bridge transfers — this introduces an off-chain trust assumption.
- **Combination potential (C3')**: The SGN's off-chain validation window creates a timing gap between lock on source chain and mint on destination chain — large fund movements during this window can affect destination chain market prices before the bridged funds arrive. Pool-based model means the per-chain pool balance directly determines bridge capacity — monitoring pool balances can predict when bridge routes will be unavailable, enabling front-running of large bridgees on destination chain DEXs. Sub-threshold TVL — listed as ⚠️ candidate.
- **Categories**: bridge

---

### gauge-ve

#### 1. PancakeSwap (veCAKE Gauge System — now Tokenomics 3.0)
- **TVL**: $2.83B aggregate PancakeSwap TVL on BSC (all versions combined, per search data; individual AMM TVL: PancakeSwap AMM $1.823B)
- **Repo**: https://github.com/pancakeswap/pancake-smart-contracts (veCAKE contracts in subdirectory)
- **Docs**: https://docs.pancakeswap.finance/products/vecake (veCAKE docs)
- **Audits**: CertiK (2023 veCAKE), Peckshield (2023)
- **Recent incidents**: April 2025 — Tokenomics 3.0 upgrade deprecated veCAKE/gauge voting system. Migration required users to transition locked CAKE positions. No security incident; architectural change.
- **Special mechanism (C3)**: veCAKE was PancakeSwap's vote-escrowed CAKE mechanism: lock CAKE for up to 4 years to receive veCAKE (non-transferable), which granted governance voting power and emission direction over 2-week gauge epochs. Gauge Boost multiplied votes for specific pools (1x to 2.5x range). Post-Tokenomics 3.0 (2025), the gauge/veCAKE system was replaced with a simplified staking model — veCAKE is no longer active. However, the historical gauge architecture and its contracts are relevant to PRISM's analysis of BSC gauge mechanisms.
- **Combination potential (C3')**: Tokenomics 3.0 deprecated veCAKE — the current PancakeSwap system no longer has active gauge voting as of 2026. For the active BSC gauge-ve category, Thena (ve(3,3)) or Ellipsis Finance (vested EPX) may be more relevant, but both have sub-threshold TVL. This cell is partially a gap — see Coverage Gaps section.
- **Categories**: gauge-ve, dex-amm, dex-clmm

#### 2. THENA (BSC native ve(3,3) DEX)
- **TVL**: $4.36M on BSC (DefiLlama, 2026-05-25) ⚠️ sub-threshold
- **Repo**: https://github.com/ThenafiBNB
- **Docs**: https://thena.fi/docs (primary)
- **Audits**: Peckshield (2023), Code4rena contest (2023)
- **Recent incidents**: THENA price ~97% down from ATH; significant TVL decline from peak. No protocol-level exploit disclosed.
- **Special mechanism (C3)**: THENA implements Solidly-derived ve(3,3) on BSC: veTHE is a vote-escrowed NFT (non-fungible, represents locked THE + time). veTHE holders vote weekly on gauge weights to direct THE emissions to liquidity pools. Emissions are proportional to votes received. 80% of protocol fees go to veTHE voters, 20% to theNFT stakers. Gauge emission cap at 5% per pool by default.
- **Combination potential (C3')**: ve(3,3) protocols have a well-documented bribery equilibrium: protocols pay veTHE voters to direct emissions to their pools. The fee distribution (80% to voters) means vote-buying is economically rational for protocols that can extract more than 80% of fees from a pool. theNFT staker fees (20%) create a separate revenue stream that can be isolated from gauge voting dynamics. Sub-threshold TVL — listed as ⚠️ candidate.
- **Categories**: gauge-ve, dex-amm

---

## Coverage Gaps (intentional)

### BSC — lrt
No qualifying LRT (liquid restaking token) protocol exists on BSC with TVL ≥ $20M as of 2026-05-25. Reasoning: EigenLayer restaking is Ethereum-specific. BNB Chain's restaking ecosystem is nascent — KernelDAO claims $660M "BNB Chain shared security" but their DefiLlama BSC TVL shows $1.73M (the bulk is Ethereum Kelp/rsETH). Ankr's BNB LST (ankrBNB) exists but is not a restaking protocol. Stader's BNBx is a BSC LST but also not LRT. Restaking on BNB Chain is primarily a 2026 emerging category with no mature protocol meeting C1.

### BSC — perp
No BSC-native perpetual DEX has TVL ≥ $20M as of 2026-05-25. Level Finance ($2.7K), MYX Finance (~$200K), ApeX BSC ($4.07M) all fall significantly below the $20M BSC threshold. BSC perp trading volume has largely migrated to Hyperliquid (its own L1), dYdX v4 (its own chain), and GMX on Arbitrum. The BSC perp ecosystem is under TVL threshold by a significant margin. ApeX is listed as a ⚠️ sub-threshold candidate for awareness.

### BSC — gauge-ve (active)
PancakeSwap deprecated its veCAKE/gauge voting system in April 2025 (Tokenomics 3.0). THENA (ve(3,3)) has $4.36M TVL — sub-threshold. Ellipsis Finance has $990K TVL — far sub-threshold. No qualifying active gauge-ve protocol on BSC meets C1 as of 2026-05-25. PancakeSwap is listed as the cell representative based on historical gauge architecture and its massive overall TVL; the active gauge component is deprecated.

### Ethereum — perp (mainnet-native above threshold)
Synthetix V3 on Ethereum mainnet has $40.97M TVL — above the $50M Ethereum threshold? Actually $40.97M is below the $50M Ethereum C1 threshold ⚠️. GMX V2 is on Arbitrum (not Ethereum mainnet). dYdX v4 is on its own chain. Synthetix V3 is listed as sub-threshold candidate at $40.97M. The Ethereum mainnet perp category has limited TVL because most perp trading moved to dedicated L2s/chains. Synthetix V3 is listed as the representative candidate with ⚠️ notation; it satisfies C2 and C3 criteria.

---

## Summary

- **Total candidates**: 36 (including sub-threshold ⚠️ candidates)
- **Ethereum candidates**: 19 entries across 10 categories
- **BSC candidates**: 17 entries across 8 categories (2 gaps: LRT fully, Perp/gauge-ve partially)
- **Coverage — Ethereum**: 10/10 priority categories covered (perp covered by Synthetix V3 at $40.97M ⚠️ sub-threshold)
- **Coverage — BSC**: 8/10 priority categories with qualifying protocols (LRT = full gap; Perp = sub-threshold only; gauge-ve = deprecated+sub-threshold only)

### Sub-threshold candidates (⚠️)
| Protocol | Chain | Category | TVL | Gap reason |
|---|---|---|---|---|
| Ankr (ankrBNB) | BSC | lst | $731K | DefiLlama undercounts; total staked BNB higher |
| Pendle Finance | BSC | yield-vault | $13.34M | Below $20M BSC threshold |
| Beefy Finance | BSC | yield-vault | $6.68M | Below $20M BSC threshold |
| ApeX Protocol | BSC | perp | $4.07M | Below $20M BSC threshold; BSC perp ecosystem gap |
| cBridge (Celer) | BSC | bridge | $3.13M | Below $20M BSC threshold |
| THENA | BSC | gauge-ve | $4.36M | Below $20M BSC threshold |
| Synthetix V3 | Ethereum | perp | $40.97M | Below $50M Ethereum threshold |

### Known judgment calls for user review
1. **EigenCloud vs. EigenLayer naming**: DefiLlama lists the restaking protocol as "EigenCloud" (the AVS ecosystem product) rather than "EigenLayer" — TVL of $6.618B appears correct for the core restaking contracts.
2. **Sky Lending counted under both lending and stablecoin-cdp**: Sky's $5.732B TVL is primarily CDP collateral; the Spark/Aave-fork component is the lending portion. The TVL figure is for the combined CDP system.
3. **Curve counted under multiple categories**: Curve DEX TVL ($1.549B) is distinct from Curve LlamaLend TVL ($64.65M) and crvUSD supply. The gauge-ve section uses the same TVL figure as dex-amm.
4. **BSC Curve TVL**: The ~$990M figure came from the DefiLlama API call; this should be verified against the dedicated Curve BSC page as this is unusually high relative to other data.
5. **PancakeSwap Infinity freshness**: PancakeSwap Infinity (hook-based AMM) launched recently with $79.85M BSC TVL — mechanism is novel but production battle-testing is minimal. High C3' potential but also high uncertainty about undiscovered attack surfaces.
