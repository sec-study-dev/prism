"""3-subagent consensus protocol with dispute resolution loop."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .discovery import discover_stubs
from .personas import PERSONAS
from .stub import Stub

log = logging.getLogger(__name__)


def _stub_key(stub: Stub) -> str:
    """Normalize a stub identity for cross-persona deduplication."""
    return stub.stub_id.lower()


@dataclass
class ConsensusResult:
    stubs: list[Stub]
    consensus_levels: dict[str, str]
    rounds: int
    subagent_proposals: dict[str, dict[str, str]]


def _run_one_persona(persona: str, llm_client, protocol_name, protocol_chain, source_blob, docs_blob) -> list[Stub]:
    return discover_stubs(
        llm_client=llm_client,
        persona_prompt=PERSONAS[persona],
        protocol_name=protocol_name,
        protocol_chain=protocol_chain,
        source_blob=source_blob,
        docs_blob=docs_blob,
    )


def run_consensus(
    *,
    llm_client,
    protocol_name: str,
    protocol_chain: str,
    source_blob: str,
    docs_blob: str,
    max_rounds: int = 5,
) -> ConsensusResult:
    """Run 3-subagent consensus discovery with up to max_rounds dispute resolution.

    Algorithm:
    1. Run each of 3 personas; collect their stub lists.
    2. For each unique stub_key, count which personas proposed it (1, 2, or 3).
    3. If unanimous (3/3): accept, level = unanimous-3of3.
    4. If disputed (1/3 or 2/3): re-run dispute resolution on personas that didn't propose,
       focused on the disputed stub. Up to max_rounds.
    5. After max_rounds, fallback: 2/3 = majority-2of3 (accept); 1/3 = dropped.
    """
    # Initial round
    proposals_per_persona: dict[str, list[Stub]] = {}
    for p in ("A", "B", "C"):
        proposals_per_persona[p] = _run_one_persona(
            p, llm_client, protocol_name, protocol_chain, source_blob, docs_blob
        )

    proposals_by_key: dict[str, dict[str, Stub]] = {}
    for persona, stubs in proposals_per_persona.items():
        for s in stubs:
            k = _stub_key(s)
            proposals_by_key.setdefault(k, {})[persona] = s

    consensus_levels: dict[str, str] = {}
    final_stubs: list[Stub] = []
    disputed_keys: set[str] = set()

    for k, by_persona in proposals_by_key.items():
        if len(by_persona) == 3:
            consensus_levels[k] = "unanimous-3of3"
            final_stubs.append(next(iter(by_persona.values())))
        else:
            disputed_keys.add(k)

    rounds_used = 0
    for round_idx in range(1, max_rounds + 1):
        if not disputed_keys:
            break
        rounds_used = round_idx
        for k in list(disputed_keys):
            missing = {"A", "B", "C"} - set(proposals_by_key[k].keys())
            for persona in missing:
                rerun_stubs = _run_one_persona(
                    persona, llm_client, protocol_name, protocol_chain, source_blob, docs_blob
                )
                for s in rerun_stubs:
                    proposals_by_key.setdefault(_stub_key(s), {})[persona] = s
            if len(proposals_by_key[k]) == 3:
                consensus_levels[k] = "resolved-after-rounds"
                final_stubs.append(next(iter(proposals_by_key[k].values())))
                disputed_keys.discard(k)

    for k in disputed_keys:
        by_persona = proposals_by_key[k]
        if len(by_persona) >= 2:
            consensus_levels[k] = "majority-2of3"
            final_stubs.append(next(iter(by_persona.values())))

    subagent_proposals: dict[str, dict[str, str]] = {}
    for k, by_persona in proposals_by_key.items():
        if k in consensus_levels:
            subagent_proposals[k] = {
                p: (by_persona[p].entry_point if p in by_persona else "(not proposed)")
                for p in ("A", "B", "C")
            }

    return ConsensusResult(
        stubs=final_stubs,
        consensus_levels=consensus_levels,
        rounds=rounds_used,
        subagent_proposals=subagent_proposals,
    )
