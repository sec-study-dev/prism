"""Flagger: select Pass 1 stubs that proceed to Pass 2 deep extraction."""
from __future__ import annotations

from dataclasses import dataclass

from .pass1.stub import Stub


@dataclass
class FlagDecision:
    flagged: bool
    reasons: list[str]


class Flagger:
    """OR-composition of 4 rules per spec §6.

    1. candidate_tags contains a non-`function-callable` tag
    2. The stub function is called by other Tier-A protocol contracts
    3. The protocol is referenced in a benchmark M/mixed event
    4. The protocol has a public historical incident
    """

    def __init__(
        self,
        benchmark_events: list[dict],
        cross_protocol_calls: set[str],
        incident_protocols: set[str],
    ):
        self.benchmark_events = benchmark_events
        self.cross_protocol_calls = cross_protocol_calls
        self.incident_protocols = incident_protocols

    def flag(self, stub: Stub, protocol_name: str | None = None) -> FlagDecision:
        reasons: list[str] = []

        non_basic_tags = [t for t in stub.candidate_tags if t != "function-callable"]
        if non_basic_tags:
            reasons.append("non-function-callable-tag")

        if stub.stub_id in self.cross_protocol_calls:
            reasons.append("cross-tier-a-called")

        if protocol_name:
            for ev in self.benchmark_events:
                if ev.get("subset_class") not in {"M", "mixed"}:
                    continue
                if protocol_name in ev.get("involved_protocols", []):
                    reasons.append("benchmark-related")
                    break

        if protocol_name and protocol_name in self.incident_protocols:
            reasons.append("historical-incident")

        return FlagDecision(flagged=bool(reasons), reasons=reasons)
