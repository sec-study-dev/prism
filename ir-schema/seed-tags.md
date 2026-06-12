# Seed Tags for PRISM Meta-IR

Tags are an **open set**. This document defines the **seed** tags: the initial
vocabulary used during Tier-A iteration. New tags may be introduced during
Stage 1 extraction; when introduced, they must be added here with the same
structure as below before being committed to the mechanism DB.

Tag naming rule (enforced by schema): `^[a-z][a-z0-9-]*$`.

---

#### `function-callable`

**Definition.** The mechanism is triggered by an explicit external/public
function call. The simplest and most common kind. Most mechanisms with this
tag also carry one or more other tags that say what makes the function
interesting.

**When to apply.** Always, when the trigger.kind is `function-call`.

**When NOT to apply.** When the mechanism is purely a hook callback, a
state-change-triggered side effect, or a constraint that is never directly
invoked.

---

#### `lifecycle-hook`

**Definition.** The mechanism is a callback inserted into another protocol's
or contract's execution lifecycle (Uniswap v4 hooks, ERC-777 hooks, OZ
proxy upgrade hooks, etc.).

**When to apply.** When trigger.kind is `hook-callback` or when the
mechanism is registered as a callback that fires automatically during
another contract's flow.

**When NOT to apply.** When the function is callable in its own right
without being invoked by an outer lifecycle.

---

#### `accounting-window`

**Definition.** The mechanism operates within a window where some accounting
state is transient (running net, pending settlement, in-flight balance).
Reading or writing during this window can be misleading because the
"final" state is only known at window close.

**When to apply.** Flash accounting deltas, JIT liquidity windows, batch
operation buffers, multicall intermediate balances.

**When NOT to apply.** When all state read/written is final at call time.

---

#### `numerical-invariant`

**Definition.** The mechanism maintains or breaks a numerical relation
between protocol state variables (share-to-asset ratio, LTV, collateral
factor, total-supply-vs-balance, exchange rate).

**When to apply.** Any time invariants_held or invariants_at_risk contains a
numerical relation.

**When NOT to apply.** When the invariants are categorical (e.g., "only
admin can call X") rather than numerical.

---

#### `structural-layering`

**Definition.** The mechanism depends on or is composed with another
protocol's mechanism as a layer (LRT wrapping LST; vault wrapping vault;
restaking layering).

**When to apply.** When deps contains another `mechanism` or `protocol`
reference that represents a layered relationship (output of one becomes
input of the other).

**When NOT to apply.** When dependencies are peer (e.g., a DEX swap
involving two tokens) rather than layered (LST → LRT → CDP collateral).

---

#### `validation-gap`

**Definition.** The mechanism has a `missing-require` precondition — a
check that a reader would expect but the code lacks. Examples: aggregate
balance check missing in batchTransfer, zero-share check missing in
ERC-4626, totalSupply cap missing in mint.

**When to apply.** Whenever preconditions has at least one entry with
`kind: missing-require` (or `is_present: false`).

**When NOT to apply.** When all expected checks are present in the code.

---

#### `oracle-coupling`

**Definition.** The mechanism reads or trusts a price/rate from an oracle
or an external state source whose update timing it does not control.

**When to apply.** When deps contains `oracle` or the trigger conditions
reference oracle data.

**When NOT to apply.** When the mechanism uses only on-chain state it
itself manages.

---

#### `share-asset-pricing`

**Definition.** The mechanism computes the conversion between an
accounting share unit and an underlying asset unit using a ratio formula
(`shares * totalAssets / totalSupply` or similar).

**When to apply.** Whenever the postcondition includes a
shares↔assets formula. Frequently combined with `numerical-invariant`.

**When NOT to apply.** When the conversion is a flat 1:1 mapping with no
ratio.

---

#### `emergency-bypass`

**Definition.** The mechanism is an emergency / fallback / admin-rescue
path that bypasses normal flow constraints (skip waiting period, ignore
liquidity check, force-withdraw, etc.).

**When to apply.** When the function name or documentation marks the
mechanism as emergency, rescue, force, sweep, or recovery; or when the
mechanism deliberately weakens preconditions present in the normal path.

**When NOT to apply.** When the mechanism is just paused-state aware but
has no rescue semantics.

---

## Adding a new tag

If Stage 1 extraction encounters a mechanism not covered by these tags:

1. Propose the new tag name (must match `^[a-z][a-z0-9-]*$`)
2. Add a section to this file with definition, when-to-apply, when-NOT-to-apply
3. Add at least one reference example (an existing mechanism JSON file)
4. Have at least one other reviewer (human or another Stage 1 pass) confirm
   the tag is not a duplicate of an existing one
5. Commit the file change before committing any mechanism JSON that uses
   the new tag.
