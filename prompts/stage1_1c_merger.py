# -*- coding: utf-8 -*-
"""
PRISM agent prompt 1c — Merger
Stage 1 (Mechanism Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['PROPOSALS']
"""

PROMPT = """
[ROLE] You are the integrator of mechanism proposals.

[INPUT]
- Proposals from the Doc-Proposer and the MPG-Proposers (multiple partial_spec sets): {{PROPOSALS}}

[TASK]
1. Align candidates that refer to the same mechanism (match by function set / touched storage / name);
2. Merge field-by-field into a unified Effect-spec draft per mechanism: adopt directly where doc and MPG agree; include fields only one source has, annotating the source;
3. Record every conflict or gap in disagreements.

[METHOD]
- Prefer the MPG's code evidence to correct the Doc's wording (docs may be stale/over-claiming); when doc and code conflict, do NOT adjudicate yourself — record it as a conflict for the Critic/Aggregator.

[CONSTRAINTS]
- Add nothing that no Proposer proposed; merge, do not create.

[OUTPUT FORMAT] Strict JSON:
{ "merged_mechanisms": [ { "Identity": {...}, "spec_draft": { <§0.1 fields; values include sources> } } ],
  "disagreements": [ { "mechanism": "", "field": "", "doc_value": null, "mpg_value": null,
                       "type": "conflict|gap", "note": "" } ] }
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['PROPOSALS']


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
