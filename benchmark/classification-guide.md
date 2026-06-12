# M / B / Mixed Classification Guide

Every benchmark event must be classified as **M**, **B**, or **mixed** to
distinguish events involving mechanism-level interactions (which PRISM
targets) from events involving only basic-action compositions (which prior
synthesis tools target).

## Decision tree

For each event:

1. **Read the post-mortem.** Identify every distinct mechanism the attacker
   used. If unclear, mark `classification_rationale: "ambiguous post-mortem;
   classified as <X> based on available evidence"` and pick the closest
   class.

2. **For each mechanism used by the attacker**, ask: is this mechanism
   describable purely as a `function-callable` operation from FlashSyn's or
   DeFiPoser's action library (swap, transfer, deposit, withdraw, borrow,
   repay, liquidate, addLiquidity, removeLiquidity, mint, burn, redeem)?

3. **Classify**:

   - **B (Basic)**: Every mechanism used is in the basic-action set above.
     The exploit/arb is a composition of basic actions, possibly with
     unusual parameter values or ordering, but no protocol-specific
     mechanism that requires deeper IR than function-level.

   - **M (Mechanism-interaction)**: At least one mechanism used carries a
     tag beyond `function-callable` — i.e., one of `lifecycle-hook`,
     `accounting-window`, `numerical-invariant` (when the invariant is
     specifically what's exploited, not just used incidentally),
     `structural-layering`, `validation-gap`, `oracle-coupling`,
     `share-asset-pricing`, `emergency-bypass`, or a new tag.

   - **mixed**: Some mechanisms in the chain are basic-only; others require
     mechanism-level descriptions. **Prefer mixed over M whenever the
     exploit visibly composes basic-action steps (flashloan + swap +
     borrow + …) with a mechanism-level step (share-asset-pricing,
     accounting-window, …)** — even if the mechanism-level step is the
     "key" lever. Reserve M for chains that are essentially pure
     mechanism exploitation, where any basic-action wrapper is just a
     flash-loan delivery vehicle for a single mechanism-level operation.

   - **Tier-A scope rule**: classify based on what mechanism in a
     **corpus protocol** was exploited. If the victim is a non-corpus
     contract (e.g., another MEV bot, an off-corpus aggregator) and the
     corpus protocol only acts as a venue for basic actions, classify as
     B from the PRISM perspective even if the off-corpus victim has
     mechanism-level structure.

4. **Always record `classification_rationale`** — at least one sentence
   pointing to the specific mechanism that pushes the event into M or
   mixed. Without rationale a classification is not auditable.

## Examples

### Example B classification

> Event: a flash-loan-funded oracle manipulation where attacker
> swaps a large amount on a thin pool to move TWAP, then borrows
> against the inflated collateral price, then dumps.

→ Mechanisms used: swap, flashloan, borrow. All function-callable.
→ The oracle is used but not exploited at the mechanism level (no
   validation-gap, no accounting-window). The vulnerability is in the
   *parameters* (pool thinness), not the *mechanism semantics*.
→ Class: **B**.

### Example M classification

> Event: an ERC-4626 first-depositor inflation attack where attacker
> deposits 1 wei, donates a large amount of the underlying asset
> directly to the vault, then a subsequent depositor loses funds to
> rounding.

→ Mechanisms used: deposit (function-callable), direct asset donation
   (not in basic action library; it relies on the ERC-4626
   `share-asset-pricing` invariant), and subsequent depositor's deposit.
→ The exploit specifically targets the share-to-asset ratio mechanism.
→ Class: **M**.

### Example mixed classification

> Event: a v4 hook exploit that involves a normal swap (basic) followed
> by reading intra-lock currencyDelta from inside the hook (mechanism-
> level), followed by a transfer that drains.

→ Mechanisms used: swap (basic), hook callback reading
   `accounting-window` state (mechanism-level), transfer (basic).
→ Class: **mixed**.

## Audit invariants

- Every event with `subset_class: M` or `mixed` must have
  `classification_rationale` non-empty.
- The rationale must reference at least one specific
  non-`function-callable` tag (or a new tag if one was introduced).
- During Stage 0 closeout, an audit script will spot-check 10 random
  events and re-classify them; agreement must be ≥ 80% with the
  original classification. Disagreements get a re-review.
