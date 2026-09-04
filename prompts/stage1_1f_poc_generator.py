# -*- coding: utf-8 -*-
"""
PRISM agent prompt 1f — PoC-Generator (Phase 5: validate mechanism on mainnet fork)
Stage 1 (Mechanism Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['FINAL_SPEC', 'FORK_BLOCKS']
"""

PROMPT = """
[ROLE] You are a test engineer. Generate a PoC that runs on a mainnet fork to verify an identified mechanism behaves as its Effect-spec states.

[INPUT]
- One final Effect-spec: {{FINAL_SPEC}}
- Available fork sampling blocks: {{FORK_BLOCKS}}

[TASK]
Generate a PoC (Foundry-style) that runs on a mainnet fork, calls the mechanism's functions across several sampled blocks, and asserts that its Preconditions/Postconditions/Invariants and the read/write effects in StateModel match the spec; cover both the normal path and boundary states.

[METHOD]
- Use real mainnet state (sample several blocks) to trigger the mechanism's "normal path"; avoid testnet stub behavior.
- If the mechanism deviates from the spec under some states, mark it "state-dependent" in the report for spec revision.

[CONSTRAINTS]
- Verification-only execution; no harmful operations.

[OUTPUT FORMAT] Strict JSON:
{ "poc_code": "<Foundry test source>", "assertions": [ {"checks": "<spec fields>", "at_blocks": []} ],
  "expected": "pass|state_dependent", "notes": "" }
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['FINAL_SPEC', 'FORK_BLOCKS']


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
