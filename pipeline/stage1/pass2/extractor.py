"""Pass 2: deep IR extraction for a single flagged stub."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import jsonschema

from pipeline.stage1.config import PASS2_MAX_ATTEMPTS
from pipeline.stage1.llm.client import LLMMessage
from pipeline.stage1.pass1.stub import Stub

log = logging.getLogger(__name__)

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


SYSTEM_PROMPT = """You are extracting a detailed mechanism IR JSON for a PRISM Stage 1 deep pass.

You receive a Stub (Pass 1 output) describing a candidate mechanism, plus
structured context: AST visitor outputs, source blob, docs blob.

Produce a single JSON object conforming to the meta-IR schema. ALL top-level
fields are required. additionalProperties: false. Tags must be open lowercase
kebab-case. Provenance must reference doc URL or code path with line ranges.

Set poc.status to "draft". The PoC file path should follow the convention
ir-schema/examples/poc/<mechanism-id>.t.sol or, for Tier-A protocols,
mechanism-db/<chain>/<protocol-slug>/<mechanism-id>/<mechanism-id>.t.sol
(the orchestrator will move it to the final location).

Output ONLY the JSON object (you may wrap in a ```json block)."""


def _extract_json_obj(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    m = JSON_BLOCK_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


def extract_ir(
    *,
    llm_client,
    stub: Stub,
    tool_registry,
    source_blob: str,
    docs_blob: str,
    ir_schema: dict,
    source_path: Path | None = None,
    max_attempts: int = PASS2_MAX_ATTEMPTS,
) -> tuple[dict | None, int]:
    """Returns (ir_dict_or_none, attempts_used)."""
    validator = jsonschema.Draft202012Validator(ir_schema)

    tool_block = ""
    if tool_registry is not None:
        try:
            tool_block = tool_registry.gather(source_path).to_prompt_block()
        except Exception as e:  # noqa: BLE001 — static analysis is best-effort
            log.warning("tool registry gather failed: %s", e)
    tool_section = f"\n=== STATIC ANALYSIS CONTEXT ===\n{tool_block}\n" if tool_block else ""

    feedback = ""
    for attempt in range(1, max_attempts + 1):
        user_msg = f"""Stub:
{json.dumps(stub.to_json(), indent=2)}
{tool_section}
=== SOURCE BLOB ===
{source_blob}

=== DOCS BLOB ===
{docs_blob}

{feedback}

Produce the meta-IR JSON object."""
        response = llm_client.complete(
            system=SYSTEM_PROMPT,
            messages=[LLMMessage(role="user", content=user_msg)],
        )
        ir = _extract_json_obj(response)
        if ir is None:
            feedback = f"PREVIOUS ATTEMPT (#{attempt}): could not extract JSON object. Output ONLY a JSON object."
            continue
        errors = list(validator.iter_errors(ir))
        if not errors:
            return ir, attempt
        err_summary = "; ".join(f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors[:5])
        feedback = f"PREVIOUS ATTEMPT (#{attempt}) FAILED schema validation:\n{err_summary}\nFix and re-output the full JSON."
    return None, max_attempts
