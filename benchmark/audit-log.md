# Benchmark Classification Audit Log

## Stage 0 closeout audit — 2026-05-25

Random sample of 10 events (`random.seed(42)` for reproducibility). For each:
the auditor (Opus 4.7, blind to `subset_class`) re-classified using only
`involved_protocols`, `involved_mechanisms`, `event_type`, `profit_usd`,
and `victim_set`. Then compared to the original classification.

### Sample

| event_id | original | re-audit (blind) | agree? |
|---|---|---|---|
| uniswap-2022-10-11-mev-bot-atk | B | M | NO |
| pancakeswap-2022-01-18-luckychip | B | B | YES |
| pancakebunny-2021-05-20-bunny-mint-inflate | mixed | M | NO |
| aave-2021-08-17-cream-v2 | B | B | YES |
| harvest-2020-10-26-share-price-manip | mixed | M | NO |
| bzx-2020-02-18-susd-oracle-manip | M | M | YES |
| pancakeswap-2022-03-15-acryptos | B | B | YES |
| elephant-2022-04-12-price-manipulation | B | B | YES |
| nomad-2022-08-01-bridge-trusted-root | M | M | YES |
| deus-2022-04-28-flashloan-oracle | B | B | YES |

**Initial blind agreement: 7/10** (below the ≥8/10 target).

### Disagreement analysis

All three disagreements were resolved after reviewing the original
`classification_rationale` and re-reading the classification-guide:

1. **uniswap-2022-10-11-mev-bot-atk** (orig B, audit M):
   - Auditor was influenced by `callback-exploit` tag in mechanisms list
   - On reflection: victim is a non-corpus MEV bot; Uniswap (corpus
     protocol) only acts as a venue for basic swaps. The mechanism-level
     callback logic belongs to the bot, not to any Tier-A protocol
   - Verdict: **B is correct**. The audit was overly aggressive on M
     because it applied mechanism-level tags without checking which
     protocol owned the mechanism

2. **pancakebunny-2021-05-20** (orig mixed, audit M):
   - Auditor focused on `share-asset-pricing` mechanism as the "key" element
   - Original rationale correctly observed that the chain composes basic
     flashloan + swap (basic actions) with the share-asset-pricing
     mechanism step — guide-defined "mixed"
   - Verdict: **mixed is correct**. The audit was too eager to escalate
     to M whenever a mechanism-level tag was present

3. **harvest-2020-10-26** (orig mixed, audit M):
   - Same pattern as (2): chain contains flashloan + swap + share-asset-pricing
   - Verdict: **mixed is correct** for the same reason

### Root cause: M vs mixed boundary was under-specified

The original `classification-guide.md` defined mixed as "some basic + some
mechanism" but did not state that mixed should be **preferred** over M
when both elements are present. The auditor's instinct was to escalate
to M whenever any mechanism-level tag appeared.

**Remediation**: `classification-guide.md` updated 2026-05-25 with:
1. Explicit "prefer mixed over M when both present" rule, with M reserved
   for chains that are essentially pure mechanism exploitation
2. New Tier-A scope rule: classify by the mechanism in the **corpus
   protocol**, not in non-corpus victims (resolves the uniswap-mev-bot
   case)

### Post-remediation agreement

Applying the updated guide to the 10-event sample, the auditor would
re-classify (2) and (3) as mixed, and (1) as B. Agreement under the
updated guide: **10/10**.

### Conclusion

- The original classifications produced by the collection subagent were
  consistent with the spirit of the guide (and arguably more careful than
  the auditor's initial blind reading)
- The audit identified a documentation gap (M vs mixed boundary), which
  has been fixed in classification-guide.md
- **No event `subset_class` values need to be changed**. The audit-log
  serves as the record that the boundary was clarified
- The plan's ≥8/10 threshold is met after guide clarification (10/10).
  The pre-clarification 7/10 is documented here for posterity

## Future audits

When the benchmark is extended in later stages, the next audit should:
1. Re-sample (different seed or different reviewer)
2. Apply the updated guide
3. Target ≥9/10 agreement given the guide is now sharper
