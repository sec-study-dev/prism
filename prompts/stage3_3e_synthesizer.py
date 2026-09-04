# -*- coding: utf-8 -*-
"""
PRISM agent prompt 3e — Synthesizer (splice validated fragments into a Strategy Sketch)
Stage 3 (Strategy Identification)

Auto-generated from PRISM_agent_prompts.md. Edit the source .md, not this file.
Runtime placeholders (fill via render()): ['VALIDATED_FRAGMENTS', 'SPECS']
"""

PROMPT = """
[ROLE] You are the strategy integrator. Splice cross-validated fragments into one complete, executable strategy.

[INPUT]
- The validated Econ-Fragments (with realizing_path) and Audit-Fragments (with profitability verdicts): {{VALIDATED_FRAGMENTS}}
- The Effect-specs of the relevant mechanisms (especially each mechanism's Reliances.temporal.k): {{SPECS}}

[TASK]
1. Splice fragments that share mechanisms, or that can be chained via pre/post, into one complete strategy whose value flow forms a closed loop (net profit > 0);
2. Produce ordered steps, each tagged with its mechanism's temporal_scope_k (from Reliances.temporal);
3. Generate segmentation_hint: any step with temporal_scope_k>=1 is a cross-block breakpoint (for §3.2.5 splitting; place the second segment at +k blocks);
4. Decide stage4_target.class (single_block / cross_block) and give objective and constraints;
5. Keep params symbolic; give value_loop (incl. flash loan and repay step, net_profit_expr) and preconditions.

[METHOD]
- single_block: all steps have k=0 and are executable within one block; cross_block: there is a k>=1 breakpoint.
- Include only steps backed by validated fragments; ensure value_loop closes.

[CONSTRAINTS]
- Output must be schema-valid (§0.3), self-contained enough for §3.2.5 to split directly and for Stage 4 to generate transactions directly.

[OUTPUT FORMAT] Strict JSON: { <StrategySketch, see §0.3> }
"""

# The {{PLACEHOLDER}} slots this prompt expects at runtime.
PLACEHOLDERS = ['VALIDATED_FRAGMENTS', 'SPECS']


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
