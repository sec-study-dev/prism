"""Tests that examples use only seed tags or document new tags."""
import json
import re
from pathlib import Path

import pytest


SEED_TAGS_PATH_PARTS = ("ir-schema", "seed-tags.md")


def _extract_seed_tags(md_path: Path) -> set[str]:
    """Seed tags are h2 or h3 headings starting with `#### \`<tag>\``."""
    text = md_path.read_text()
    pattern = re.compile(r"^####\s+`([a-z][a-z0-9-]*)`", re.MULTILINE)
    return set(pattern.findall(text))


def test_seed_tags_file_exists(repo_root: Path):
    p = repo_root.joinpath(*SEED_TAGS_PATH_PARTS)
    assert p.exists()


def test_at_least_nine_seed_tags(repo_root: Path):
    p = repo_root.joinpath(*SEED_TAGS_PATH_PARTS)
    tags = _extract_seed_tags(p)
    assert len(tags) >= 9, f"expected ≥9 seed tags, found {len(tags)}: {tags}"


def test_example_tags_are_all_seed_or_declared(repo_root: Path):
    p = repo_root.joinpath(*SEED_TAGS_PATH_PARTS)
    seed = _extract_seed_tags(p)
    examples_dir = repo_root / "ir-schema" / "examples"
    used: set[str] = set()
    for f in examples_dir.glob("*.json"):
        used.update(json.loads(f.read_text()).get("tags", []))
    unknown = used - seed
    assert not unknown, (
        f"examples use tags not in seed set: {unknown}. "
        f"Either add them to {p} or fix the examples."
    )
