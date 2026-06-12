"""Test M0 composite gate."""
import subprocess
import sys
from pathlib import Path


def test_m0_gate_passes(repo_root: Path):
    """M0 gate must pass at the end of Stage 0."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.m0_gate"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"M0 gate failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
