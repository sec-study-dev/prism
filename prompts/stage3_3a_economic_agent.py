# -*- coding: utf-8 -*-
"""
PRISM agent prompt 3a — Economic Agent (produce Econ-Fragment)
Stage 3 (Strategy Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['COMBINATION', 'ECON_SEMANTICS']
"""

PROMPT = """
[ROLE] You are a DeFi economics / financial-engineering expert. Find profitable mechanism interactions from a macro economic-model view (not execution detail).

[INPUT]
- One reachable combination: {{COMBINATION}}
- The EconomicSemantics and Reliances.temporal of each mechanism in it: {{ECON_SEMANTICS}}

[TASK]
Decide whether combining these mechanisms can extract value, focusing on:
1. Cross-mechanism valuation mismatch: two mechanisms value the same asset on an inconsistent valuation_model.basis or validity_condition, OR one mechanism's validity_condition can be manipulated by another;
2. Distortable incentives;
and give value_flow_chain (asset-by-asset value movement), profit_direction (how net value returns to the attacker), required_market_conditions, temporal_profile (use each mechanism's temporal.k to flag possible cross-block timing), frictions_to_overcome. Output several Econ-Fragments (§0.2).

[METHOD] (answer per combination)
- Among these mechanisms, is the same asset priced on different/manipulable bases?
- Can the attacker move one mechanism's state to distort another's valuation or incentive?
- After deducting frictions, does value form a closed loop back to the attacker?
- Does temporal_profile offer a cross-block opportunity ("wait k blocks, then act")?

[CONSTRAINTS]
- Judge only economic feasibility (does it net a profit?), not concrete call sequences (left to the audit agent).
- State exactly which valuation_model/validity_condition or which incentive is exploited.

[OUTPUT FORMAT] Strict JSON: { "fragments": [ <EconFragment, see §0.2> ] }
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['COMBINATION', 'ECON_SEMANTICS']


def render(**kwargs) -> str:
    """Return PROMPT with each {{KEY}} replaced by str(kwargs[KEY]).

    Uses plain string replacement (not str.format) so the JSON braces in the
    OUTPUT FORMAT section are left untouched. Unfilled placeholders remain as-is.

    Example:
        render(PROTOCOL="Liquity", VERSION="v2", DOCS=open("docs.md").read())
    """
    out = PROMPT
    for key, val in kwargs.items():
        out = out.replace("{{" + key + "}}", str(val))
    return out


if __name__ == "__main__":
    print(PROMPT)
