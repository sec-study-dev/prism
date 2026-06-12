"""Pass 1 single-subagent discovery wrapper."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from .stub import Stub, parse_stub_json, StubValidationError
from ..llm.client import LLMMessage

log = logging.getLogger(__name__)

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\[.*?\])\s*```", re.DOTALL)


def _extract_json_array(text: str) -> list[dict] | None:
    text = text.strip()
    if text.startswith("["):
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
    # Try to find a bare JSON array somewhere
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    return None


def discover_stubs(
    *,
    llm_client,
    persona_prompt: str,
    protocol_name: str,
    protocol_chain: str,
    source_blob: str,
    docs_blob: str,
) -> list[Stub]:
    user_msg = f"""Protocol: {protocol_name}
Chain: {protocol_chain}

=== SOURCE CODE (concatenated) ===
{source_blob}

=== DOCUMENTATION (concatenated) ===
{docs_blob}

Identify mechanisms in this protocol. Output ONLY a JSON array of Stub objects per the schema in your system prompt."""

    response = llm_client.complete(
        system=persona_prompt,
        messages=[LLMMessage(role="user", content=user_msg)],
    )

    raw_stubs = _extract_json_array(response)
    if raw_stubs is None:
        log.warning("could not extract JSON array from response (protocol=%s)", protocol_name)
        return []

    result: list[Stub] = []
    for item in raw_stubs:
        try:
            stub = parse_stub_json(json.dumps(item))
            result.append(stub)
        except StubValidationError as e:
            log.info("dropping invalid stub: %s (%s)", item.get("stub_id", "?"), e)
    return result
