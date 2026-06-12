"""Gold-standard generator: 3-subagent consensus on a protocol's full mechanism list.

Used for spec §3.B Criterion B: golden truth comparison on Uniswap V4 + Curve Finance.
"""
from __future__ import annotations

import logging

from pipeline.stage1.pass1.consensus import run_consensus

log = logging.getLogger(__name__)


def generate_gold_standard(
    *,
    llm_client,
    protocol_name: str,
    protocol_chain: str,
    source_blob: str,
    docs_blob: str,
    max_rounds: int = 5,
) -> list[dict]:
    """Run consensus to convergence, return mechanism stubs as gold standard.

    For gold standard purposes, we accept only unanimous-3of3 or resolved
    consensus (not majority-2of3 fallback). Reject events that didn't converge.
    """
    result = run_consensus(
        llm_client=llm_client,
        protocol_name=protocol_name,
        protocol_chain=protocol_chain,
        source_blob=source_blob,
        docs_blob=docs_blob,
        max_rounds=max_rounds,
    )
    gold = []
    for stub in result.stubs:
        k = stub.stub_id.lower()
        level = result.consensus_levels.get(k)
        if level in {"unanimous-3of3", "resolved-after-rounds"}:
            gold.append({
                "id": stub.stub_id,
                "tags": stub.candidate_tags,
                "trigger": {"entry_point": stub.entry_point},
                "consensus_level": level,
            })
    return gold
