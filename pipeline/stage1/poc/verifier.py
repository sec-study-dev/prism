"""PoC verifier: forge build + forge test + sanity check."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from .sanity import SanityChecker, SanityFailure

log = logging.getLogger(__name__)


class VerifierResult:
    def __init__(self, passed: bool, reason: str = "", stdout: str = "", stderr: str = ""):
        self.passed = passed
        self.reason = reason
        self.stdout = stdout
        self.stderr = stderr


def verify_poc(
    *,
    source: str,
    test_name: str,
    mechanism_tags: list[str],
    state_writes: list[str],
    foundry_root: Path,
    poc_subdir: Path,
) -> VerifierResult:
    """Write the source to disk, run forge build + test, then sanity check."""
    poc_subdir.mkdir(parents=True, exist_ok=True)
    test_path = poc_subdir / f"{test_name}.t.sol"
    test_path.write_text(source)

    build = subprocess.run(
        ["forge", "build"],
        cwd=foundry_root, capture_output=True, text=True, timeout=300,
    )
    if build.returncode != 0:
        return VerifierResult(False, "build-failed", build.stdout, build.stderr)

    test = subprocess.run(
        ["forge", "test", "--match-test", f"test_{test_name}", "-vv"],
        cwd=foundry_root, capture_output=True, text=True, timeout=600,
    )
    if test.returncode != 0:
        return VerifierResult(False, "test-failed", test.stdout, test.stderr)

    checker = SanityChecker()
    try:
        checker.check(source, mechanism_tags=mechanism_tags, state_writes=state_writes)
    except SanityFailure as e:
        return VerifierResult(False, f"sanity-failed: {e}", test.stdout, "")

    return VerifierResult(True, "all-checks-pass", test.stdout, "")
