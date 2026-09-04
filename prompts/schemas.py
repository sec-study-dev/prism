# -*- coding: utf-8 -*-
"""
PRISM shared output schemas (Section 0 of PRISM_agent_prompts.md).
Referenced by the Stage 1 / Stage 3 prompts. Auto-generated; edit the source .md.
"""

# Effect-based Specification — Stage 1 pipeline final output format
EFFECT_SPEC_SCHEMA = """
{
  "Identity": { "protocol": "", "version": "", "name": "", "category": "" },
  "Interface": { "functions": [], "events": [] },
  "Preconditions": [ "<first-order-logic predicate>" ],
  "Postconditions": [ "<first-order-logic predicate>" ],
  "StateModel": {
    "storage_reads": [], "storage_writes": [],
    "external_deps": [ {"kind": "ORACLE|TOKEN|CONTRACT", "ref": ""} ]
  },
  "CompositionPoints": [
    { "location": {"function": "", "offset": ""}, "call_type": "CALL|DELEGATECALL|STATICCALL",
      "semantic_tag": "PRICE_QUERY|TOKEN_TRANSFER|CALLBACK|FLASH_LOAN|MINT|...",
      "committed_writes": [], "pending_writes": [], "reads_before": [], "guard_context": [] }
  ],
  "Reliances": {
    "trust":     [ "<what/whom the mechanism relies on>" ],
    "atomicity": [ "<which operations it relies on not being interrupted>" ],
    "liquidity": [ "<which liquidity sources it relies on being available>" ],
    "temporal":  [ { "var": "", "k": 0, "b": "INF|<integer>", "closes_by": ["<mechanisms that authoritatively rewrite this var>"] } ]
  },
  "Invariants": [ { "expr": "", "scope": "PER_CALL|PER_BLOCK|PER_EPOCH|GLOBAL",
                    "dimension": "economic|state_consistency|access_control|price_rate|conservation|temporal" } ],
  "EconomicSemantics": {
    "value_flow": [ {"asset": "", "from": "", "to": ""} ],
    "incentive_structure": [ "" ],
    "failure_modes": [ "" ],
    "valuation_model": { "basis": "SPOT_ORACLE|TWAP|SHARE=assets/supply|BONDING_CURVE|FIXED_PEG|FACE_VALUE|...",
                         "converts": "<which asset it converts to which, on this basis>",
                         "validity_condition": "<condition under which this valuation is economically sound>" },
    "frictions": [ { "type": "SWAP_FEE|INTEREST|REDEEM_FEE|EXIT_PENALTY|PERF_FEE|SLIPPAGE|SPREAD|ROUNDING", "rule": "" } ]
  }
}
"""

# Strategy Fragment — Stage 3 economic/audit agent output
STRATEGY_FRAGMENT_SCHEMA = """
// EconFragment (Economic Agent)
{ "kind": "ECON", "involved_mechanisms": [],
  "value_flow_chain": [ {"step": 1, "asset": "", "from": "", "to": "", "via_mechanism": ""} ],
  "profit_direction": "<how net value ultimately returns to the attacker>",
  "exploited_mismatch": { "type": "VALUATION_MISMATCH|INCENTIVE_DISTORTION",
                          "detail": "<which two mechanisms value the same asset on inconsistent/manipulable basis or validity_condition / which incentive is distortable>" },
  "required_market_conditions": [ "" ],
  "temporal_profile": [ {"mechanism": "", "k": 0} ],
  "frictions_to_overcome": [ "" ],
  "rationale": "" }

// AuditFragment (Code Audit Agent)
{ "kind": "AUDIT", "method": "RELIANCE_VIOLATION|COUNTERFACTUAL", "involved_mechanisms": [],
  "call_path": [ {"step": 1, "contract": "", "function": "", "symbolic_params": [{"name":"","type":""}],
                  "touches": "<the reliance/invariant or composition point touched>"} ],
  "violated_target": { "kind": "RELIANCE|INVARIANT", "ref": "<the specific reliance/invariant violated>", "how": "" },
  "attacker_control": [ "<attacker-controlled: funds / call order / params / callback>" ],
  "temporal_breakpoints": [ {"after_step": 1, "mechanism": "", "k": 0} ],
  "rationale": "" }
"""

# Strategy Sketch — Synthesizer output (input to Stage 4)
STRATEGY_SKETCH_SCHEMA = """
{
  "id": "", "goal": "<natural-language description of the net-profit goal>", "involved_mechanisms": [],
  "steps": [
    { "step_no": 1, "contract": "", "function": "",
      "symbolic_params": [ {"name": "x1", "type": "uint256", "role": "<amountIn / borrow amount / slippage tolerance / ...>"} ],
      "mechanism_id": "", "temporal_scope_k": 0,        // 0=instant; k>=1=this step's mechanism must wait k blocks (breakpoint)
      "state_effect": "", "value_effect": "" }
  ],
  "value_loop": { "attacker_inflow": [], "attacker_outflow": [],
                  "flashloan": {"asset": "", "amount_symbol": "", "repay_at_step": null},
                  "net_profit_expr": "<gross-profit expression in symbolic params>" },
  "preconditions": { "contract_state": [ "" ], "market_conditions": [ "" ] },
  "segmentation_hint": [ {"break_after_step": 1, "k": 0} ],   // §3.2.5: split where k>=1; place the second segment at +k blocks
  "stage4_target": { "class": "single_block|cross_block",
                     "objective": "maximize net_profit_expr",
                     "constraints": [ "no_revert", "slippage_bounds", "health_factor", "flashloan_repay" ] },
  "validation_status": { "econ_validated": true, "audit_validated": true }
}
"""

