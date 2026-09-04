# -*- coding: utf-8 -*-
"""
PRISM agent prompt 3d — Cross-validation Audit -> Econ (econ validates an audit fragment)
Stage 3 (Strategy Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['AUDIT_FRAGMENT', 'ECON_SEMANTICS']
"""

PROMPT = """
[ROLE] You are an economics expert, acting as the profitability validator of an audit fragment.

[INPUT]
- One Audit-Fragment (call path + violated reliance/invariant): {{AUDIT_FRAGMENT}}
- The EconomicSemantics of the relevant mechanisms: {{ECON_SEMANTICS}}

[TASK] Using each mechanism's EconomicSemantics, trace the value in/out along this path, deduct frictions, and decide whether it nets a profit and whether value returns to the attacker. Give the net-value reasoning, the profit sign, and the required conditions.

[CONSTRAINTS] Make only an economic judgment; state value conservation/source explicitly (is value created from nothing, or transferred from someone).

[OUTPUT FORMAT] Strict JSON:
{ "profitable": true, "net_value_reasoning": "", "est_profit_sign": "positive|zero|negative",
  "required_conditions": [ "" ] }
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['AUDIT_FRAGMENT', 'ECON_SEMANTICS']


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
