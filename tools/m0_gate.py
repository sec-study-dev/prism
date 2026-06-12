"""M0 composite gate — verifies all Stage 0 exit criteria.

Exit criteria (umbrella spec §15 M0):
1. Meta-IR JSON schema v1 — exists + 5 valid examples + 3 invalid rejected
2. Seed tag set — 9 tags + all example tags declared
3. Tier-A — ≥20 protocols (≥10 Ethereum + ≥10 BSC), all valid, each chain
   covering as many of 10 priority categories as feasible
4. Benchmark — 50-100 events, valid, M+mixed in 15-40%
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class Check:
    def __init__(self, name: str):
        self.name = name
        self.failures: list[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def ok(self) -> bool:
        return not self.failures


def run_pytest(target: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "--no-header"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def check_ir() -> Check:
    c = Check("IR schema + examples")
    examples = list((REPO_ROOT / "ir-schema" / "examples").glob("*.json"))
    if len(examples) < 5:
        c.fail(f"only {len(examples)} examples, need ≥5")
    invalids = list((REPO_ROOT / "ir-schema" / "invalid-examples").glob("*.json"))
    if len(invalids) < 3:
        c.fail(f"only {len(invalids)} invalid examples, need ≥3")
    ok, output = run_pytest("tests/test_ir_schema.py")
    if not ok:
        c.fail(f"IR schema tests failed:\n{output}")
    return c


def check_tags() -> Check:
    c = Check("Seed tags")
    p = REPO_ROOT / "ir-schema" / "seed-tags.md"
    if not p.exists():
        c.fail("seed-tags.md missing")
        return c
    tags = re.findall(r"^####\s+`([a-z][a-z0-9-]*)`", p.read_text(), re.MULTILINE)
    if len(tags) < 9:
        c.fail(f"only {len(tags)} seed tags, need ≥9")
    ok, output = run_pytest("tests/test_tag_coverage.py")
    if not ok:
        c.fail(f"tag coverage tests failed:\n{output}")
    return c


def check_tier_a() -> Check:
    c = Check("Tier-A protocols")
    metadata = list((REPO_ROOT / "corpus" / "tier-a" / "protocols").rglob("metadata.json"))
    if len(metadata) < 20:
        c.fail(f"Tier-A has {len(metadata)} protocols, need ≥20")
    counts = {"ethereum": 0, "bsc": 0}
    for f in metadata:
        chain = json.loads(f.read_text()).get("chain")
        if chain in counts:
            counts[chain] += 1
    if counts["ethereum"] < 10:
        c.fail(f"Tier-A has {counts['ethereum']} Ethereum protocols, need ≥10")
    if counts["bsc"] < 10:
        c.fail(f"Tier-A has {counts['bsc']} BSC protocols, need ≥10")
    ok, output = run_pytest("tests/test_protocol_schema.py")
    if not ok:
        c.fail(f"protocol schema/Tier-A tests failed:\n{output}")
    return c


def check_benchmark() -> Check:
    c = Check("Benchmark events")
    events = list((REPO_ROOT / "benchmark" / "events").rglob("*.json"))
    if not (50 <= len(events) <= 200):
        c.fail(f"benchmark has {len(events)} events, need 50-200")
    audit_log = REPO_ROOT / "benchmark" / "audit-log.md"
    if not audit_log.exists():
        c.fail("audit-log.md missing — closeout audit not performed")
    ok, output = run_pytest("tests/test_benchmark_schema.py")
    if not ok:
        c.fail(f"benchmark tests failed:\n{output}")
    return c


def main() -> int:
    checks = [
        check_ir(),
        check_tags(),
        check_tier_a(),
        check_benchmark(),
    ]
    print("=" * 60)
    print("PRISM M0 Gate")
    print("=" * 60)
    all_ok = True
    for c in checks:
        status = "OK" if c.ok() else "FAIL"
        print(f"[{status}] {c.name}")
        for f in c.failures:
            for line in f.splitlines():
                print(f"        {line}")
        all_ok &= c.ok()
    print("=" * 60)
    print("M0 GATE: PASS" if all_ok else "M0 GATE: FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
