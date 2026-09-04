# -*- coding: utf-8 -*-
"""
PRISM agent prompt 3c — Cross-validation Econ -> Audit (audit validates an econ fragment)
Stage 3 (Strategy Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['ECON_FRAGMENT', 'SPECS']
"""

PROMPT = """
[ROLE] You are an audit expert, acting as the realizability validator of an economic fragment.

[INPUT]
- One Econ-Fragment: {{ECON_FRAGMENT}}
- The MPG and Effect-specs of the relevant mechanisms: {{SPECS}}

[TASK] Decide whether a concrete function-call path exists that realizes the value flow / valuation-mismatch exploitation described by this economic combination. If yes -> produce the path and mark validated; if no -> mark rejected and explain (which step has no callable entry / is blocked by some guard, etc.).

[CONSTRAINTS] The path must be concrete and executable; do not fabricate nonexistent functions or bypass guards just to make it pass.

[OUTPUT FORMAT] Strict JSON:
{ "validated": true,
  "realizing_path": [ {"step": 1, "contract": "", "function": "", "symbolic_params": []} ],
  "reason": "" }   // if validated=false, leave realizing_path empty and explain in reason
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['ECON_FRAGMENT', 'SPECS']


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
