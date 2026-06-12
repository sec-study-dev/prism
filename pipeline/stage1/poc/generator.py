"""PoC generator: tag-class template + LLM fill."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from pipeline.stage1.config import POC_MAX_ATTEMPTS
from pipeline.stage1.llm.client import LLMMessage

log = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"

SYSTEM_PROMPT = """You are filling in a Foundry test template for a PRISM PoC.

You receive: the mechanism IR JSON; a template with {{PLACEHOLDER}} variables;
the protocol source context.

Task: produce the fully-filled .t.sol source. Replace every {{PLACEHOLDER}}
with appropriate Solidity code. The test must:

1. Compile (forge build)
2. Run (forge test --match-test test_<id>) to pass
3. Have NON-TRIVIAL assertions (no assertTrue(true), no x==x)
4. Reference at least one state_writes variable from the IR
5. For attackable-class mechanisms (validation-gap, share-asset-pricing,
   emergency-bypass, oracle-coupling, accounting-window): include an attacker
   profit assertion (assertGt(attackerAfter, attackerBefore)) OR a victim
   harm assertion (assertLt(victimAfter, victimBefore))

Output ONLY the filled .t.sol source (no markdown wrapper, no commentary)."""


def _pick_template(mechanism_tags: list[str]) -> Path:
    """Pick the template matching the highest-priority tag in the mechanism."""
    priority = [
        "validation-gap", "share-asset-pricing", "emergency-bypass",
        "oracle-coupling", "accounting-window", "lifecycle-hook",
        "structural-layering", "numerical-invariant", "function-callable",
    ]
    for tag in priority:
        if tag in mechanism_tags:
            p = TEMPLATES_DIR / f"{tag}.t.sol.template"
            if p.exists():
                return p
    raise ValueError(f"no template matches tags: {mechanism_tags}")


def generate_poc(
    *,
    llm_client,
    ir: dict,
    template_path: Path | None = None,
    source_blob: str,
    feedback: str = "",
) -> str:
    """Generate PoC .t.sol source for a mechanism IR. Returns the filled source."""
    if template_path is None:
        template_path = _pick_template(ir["tags"])
    template = template_path.read_text()

    user_msg = f"""=== MECHANISM IR ===
{__import__('json').dumps(ir, indent=2)}

=== TEMPLATE ===
{template}

=== PROTOCOL SOURCE CONTEXT ===
{source_blob}

{feedback}

Output the fully-filled .t.sol Solidity source."""

    response = llm_client.complete(
        system=SYSTEM_PROMPT,
        messages=[LLMMessage(role="user", content=user_msg)],
    )
    response = re.sub(r"^```(?:solidity|sol)?\s*", "", response.strip())
    response = re.sub(r"\s*```$", "", response)
    return response
