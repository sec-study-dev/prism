"""Criterion C: random audit sampling (spec §3.C).

3 mechanisms per non-gold-standard Tier-A protocol = 72 judgments.
User fills in 'real' / 'false-positive' per item; pass rate computed.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AuditItem:
    protocol_slug: str
    chain: str
    mechanism_id: str
    ir_path: Path | None
    sol_path: Path | None
    metrics_path: Path | None
    judgment: str | None  # 'real' | 'false-positive' | None (unfilled)


def sample_audit_items(
    *,
    db_root: Path,
    exclude_protocols: set[str],
    k_per_protocol: int = 3,
    seed: int = 0,
) -> list[AuditItem]:
    rng = random.Random(seed)
    items: list[AuditItem] = []
    for chain_dir in sorted(db_root.iterdir()):
        if not chain_dir.is_dir():
            continue
        chain = chain_dir.name
        for proto_dir in sorted(chain_dir.iterdir()):
            if not proto_dir.is_dir():
                continue
            slug = proto_dir.name
            if slug in exclude_protocols:
                continue
            mech_dirs = [d for d in proto_dir.iterdir() if d.is_dir()]
            if not mech_dirs:
                continue
            sampled = rng.sample(mech_dirs, min(k_per_protocol, len(mech_dirs)))
            for md in sampled:
                mid = md.name
                items.append(AuditItem(
                    protocol_slug=slug, chain=chain, mechanism_id=mid,
                    ir_path=md / f"{mid}.json",
                    sol_path=md / f"{mid}.t.sol",
                    metrics_path=md / f"{mid}.metrics.json",
                    judgment=None,
                ))
    return items


def render_audit_form(items: list[AuditItem], output_path: Path) -> str:
    lines = [
        "# Stage 1 Criterion C — User Audit Form",
        "",
        "For each mechanism below, set `judgment` to `real` or `false-positive`",
        "(in the table). Real = the IR truthfully captures an interactable mechanism;",
        "False-positive = LLM hallucinated, PoC passes trivially, or mechanism not useful.",
        "",
        "| # | Protocol | Mechanism ID | IR | PoC | Metrics | Judgment |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, it in enumerate(items, 1):
        lines.append(
            f"| {i} | {it.protocol_slug} | `{it.mechanism_id}` | "
            f"[ir]({it.ir_path}) | [sol]({it.sol_path}) | [metrics]({it.metrics_path}) | "
            f"_real / false-positive_ |"
        )
    lines.append("")
    lines.append("After judging all, save and run `python -m pipeline.stage1.evaluation.criterion_c --tally <this-file>` to compute pass rate.")
    md = "\n".join(lines)
    output_path.write_text(md)
    return md


def compute_audit_pass_rate(items: list[AuditItem]) -> float:
    filled = [it for it in items if it.judgment in {"real", "false-positive"}]
    if not filled:
        return 0.0
    return sum(1 for it in filled if it.judgment == "real") / len(filled)
