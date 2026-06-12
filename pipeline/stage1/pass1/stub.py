"""Pass 1 stub data structure (lightweight mechanism candidate)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict


VALID_CHAINS = {"ethereum", "bsc"}
VALID_TRIGGER_KINDS = {"function-call", "hook-callback", "state-change", "lifecycle-point"}
STUB_ID_PATTERN = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_-]+$")
TAG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


class StubValidationError(ValueError):
    pass


@dataclass
class Stub:
    stub_id: str
    chain: str
    trigger_kind: str
    entry_point: str
    state_reads_coarse: list[str]
    state_writes_coarse: list[str]
    candidate_tags: list[str]

    def __post_init__(self):
        if not STUB_ID_PATTERN.match(self.stub_id):
            raise StubValidationError(f"stub_id invalid: {self.stub_id}")
        if self.chain not in VALID_CHAINS:
            raise StubValidationError(f"chain invalid: {self.chain}")
        if self.trigger_kind not in VALID_TRIGGER_KINDS:
            raise StubValidationError(f"trigger_kind invalid: {self.trigger_kind}")
        if not self.candidate_tags:
            raise StubValidationError("candidate_tags must be non-empty")
        for tag in self.candidate_tags:
            if not TAG_PATTERN.match(tag):
                raise StubValidationError(f"tag pattern invalid: {tag}")

    def to_json(self) -> dict:
        return asdict(self)


def parse_stub_json(s: str) -> Stub:
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise StubValidationError(f"JSON decode error: {e}")
    required = {"stub_id", "chain", "trigger_kind", "entry_point",
                "state_reads_coarse", "state_writes_coarse", "candidate_tags"}
    missing = required - set(data.keys())
    if missing:
        raise StubValidationError(f"missing fields: {missing}")
    return Stub(**{k: data[k] for k in required})
