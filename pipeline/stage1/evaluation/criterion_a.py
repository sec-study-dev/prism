"""Criterion A: benchmark M/mixed coverage check (spec §3.A).

For each M/mixed event involving a Tier-A protocol, verify that the
mechanism DB contains at least one mechanism (in any of the involved
protocols) whose tags overlap with the event's involved_mechanisms.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CoverageResult:
    total_relevant: int
    covered: int
    uncovered_event_ids: list[str]
    coverage_ratio: float


def compute_coverage(
    events: list[dict],
    db_by_protocol: dict[str, list[dict]],
    tier_a_protocol_names: list[str],
) -> CoverageResult:
    """db_by_protocol: {protocol-slug: [IR dict, ...]} — pass already-loaded DB.

    Matching is by name (case-insensitive) and by tag overlap.
    """
    tier_a_lower = {p.lower() for p in tier_a_protocol_names}
    relevant = []
    for ev in events:
        if ev.get("subset_class") not in {"M", "mixed"}:
            continue
        protocols_lower = {p.lower() for p in ev.get("involved_protocols", [])}
        if not protocols_lower & tier_a_lower:
            continue
        relevant.append(ev)

    def _normalize(s: str) -> str:
        """Strip punctuation/spaces for fuzzy slug matching."""
        import re
        return re.sub(r"[^a-z0-9]", "", s.lower())

    covered = 0
    uncovered: list[str] = []
    for ev in relevant:
        ev_tags = set(ev.get("involved_mechanisms", []))
        ev_proto_names_lower = {p.lower() for p in ev.get("involved_protocols", [])}
        ev_proto_norms = {_normalize(p) for p in ev_proto_names_lower}
        found = False
        for slug, mechs in db_by_protocol.items():
            slug_norm = _normalize(slug)
            # Match if normalized slug contained in or contains any normalized protocol name
            if not any(
                slug_norm in p_norm or p_norm in slug_norm
                for p_norm in ev_proto_norms
            ):
                continue
            for m in mechs:
                if set(m.get("tags", [])) & ev_tags:
                    found = True
                    break
            if found:
                break
        if found:
            covered += 1
        else:
            uncovered.append(ev.get("event_id", "?"))

    if not relevant:
        return CoverageResult(0, 0, [], 1.0)
    return CoverageResult(
        total_relevant=len(relevant),
        covered=covered,
        uncovered_event_ids=uncovered,
        coverage_ratio=covered / len(relevant),
    )
