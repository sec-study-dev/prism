"""PoC sanity checks (spec §8)."""
from __future__ import annotations

import re


ATTACKABLE_TAGS = {
    "validation-gap", "share-asset-pricing", "emergency-bypass",
    "oracle-coupling", "accounting-window",
}

PROFIT_PATTERNS = [
    r"assertGt\s*\(\s*\w*[aA]ttacker\w*\w*[aA]fter[^,]*,\s*\w*[aA]ttacker\w*\w*[bB]efore",
    r"assertGt\s*\(\s*\w*[aA]fter[^,]*[aA]ttacker[^,]*,\s*\w*[bB]efore[^,]*[aA]ttacker",
    r"assertGt\s*\(\s*\w*[aA]fter_[^,]*,\s*\w*[bB]efore[^,]*\)",
    r"assertGt\s*\(\s*\w*[bB]al[aA]fter\w*,\s*\w*[bB]al[bB]efore\w*\)",
]
HARM_PATTERNS = [
    r"assertLt\s*\(\s*\w*[vV]ictim\w*\w*[aA]fter[^,]*,\s*\w*[vV]ictim\w*\w*[bB]efore",
    r"assertLt\s*\(\s*\w*[aA]fter_[^,]*,\s*\w*[bB]efore[^,]*\)",
]

TRIVIAL_PATTERNS = [
    r"assertTrue\s*\(\s*true\s*\)",
    r"assertEq\s*\(\s*(\w+)\s*,\s*\1\s*\)",
    r"assertFalse\s*\(\s*false\s*\)",
]


class SanityFailure(Exception):
    pass


class SanityChecker:
    def check(self, source: str, *, mechanism_tags: list[str], state_writes: list[str]) -> None:
        non_trivial = self._has_non_trivial_assertion(source)
        if not non_trivial:
            raise SanityFailure("trivial-only assertions: all asserts match trivial patterns")

        has_state_change = self._has_state_change_assertion(source, state_writes)
        if not has_state_change:
            raise SanityFailure("no state-change assertion on a state_writes variable")

        if any(t in ATTACKABLE_TAGS for t in mechanism_tags):
            has_profit_or_harm = (
                any(re.search(p, source) for p in PROFIT_PATTERNS) or
                any(re.search(p, source) for p in HARM_PATTERNS)
            )
            if not has_profit_or_harm:
                raise SanityFailure("attackable-class mechanism requires profit or harm assertion")

    def _has_non_trivial_assertion(self, source: str) -> bool:
        any_assert = re.search(r"assert\w*\s*\(", source)
        if not any_assert:
            return False
        stripped = source
        for pat in TRIVIAL_PATTERNS:
            stripped = re.sub(pat, "", stripped)
        return bool(re.search(r"assert\w*\s*\(", stripped))

    def _has_state_change_assertion(self, source: str, state_writes: list[str]) -> bool:
        # Always accept if there are before/after temporal markers alongside an assertion
        if re.search(r"(before|after)", source, re.I) and re.search(r"assert\w*\s*\(", source):
            return True
        if not state_writes:
            return False
        for var in state_writes:
            short = var.split(".")[-1].split("[")[0]
            if short and short.lower() in source.lower():
                # Any assert that references the variable counts as state-change check
                if re.search(r"assert\w*\s*\([^)]*" + re.escape(short), source, re.I):
                    return True
        return False
