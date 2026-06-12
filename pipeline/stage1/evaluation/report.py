"""Aggregate Stage 1 evaluation report."""
from __future__ import annotations

import json
from pathlib import Path

from .criterion_a import compute_coverage, CoverageResult
from .criterion_b import compare_against_gold, PRResult


def _load_db(db_root: Path) -> dict[str, list[dict]]:
    if not db_root.exists():
        return {}
    db: dict[str, list[dict]] = {}
    for ir_path in db_root.rglob("*.json"):
        if ir_path.name.endswith(".metrics.json"):
            continue
        if not (ir_path.parent / f"{ir_path.parent.name}.t.sol").exists():
            continue
        slug = ir_path.parent.parent.name
        try:
            ir = json.loads(ir_path.read_text())
        except Exception:
            continue
        db.setdefault(slug, []).append(ir)
    return db


def build_report(
    *,
    db_root: Path,
    benchmark_events: list[dict],
    tier_a_protocol_names: list[str],
    gold_paths: dict[str, Path],
    audit_form_pass_rate: float | None,
    output_path: Path,
) -> dict:
    db = _load_db(db_root)
    a = compute_coverage(benchmark_events, db, tier_a_protocol_names)
    b_results: dict[str, PRResult] = {}
    for slug, gp in gold_paths.items():
        gold = json.loads(gp.read_text())
        pred = db.get(slug, [])
        b_results[slug] = compare_against_gold(predicted=pred, gold=gold)

    lines = [
        "# Stage 1 Extraction Report",
        "",
        f"**Date:** {__import__('datetime').datetime.now().date()}",
        f"**Pipeline version:** stage1-v1.0",
        "",
        "## Criterion A — Benchmark Coverage",
        f"- Relevant M/mixed events (touching Tier-A): **{a.total_relevant}**",
        f"- Covered by DB: **{a.covered}**",
        f"- **Coverage ratio: {a.coverage_ratio:.2%}** (target ≥95%)",
        f"- Uncovered event IDs: `{a.uncovered_event_ids[:20]}`" if a.uncovered_event_ids else "- (all covered)",
        "",
        "## Criterion B — Gold Standard P/R",
    ]
    for slug, pr in b_results.items():
        lines += [
            f"### {slug}",
            f"- Predicted: {len(pr.matched) + len(pr.predicted_only)}",
            f"- Gold standard: {len(pr.matched) + len(pr.gold_only)}",
            f"- **Precision: {pr.precision:.2%}** (target ≥90%)",
            f"- **Recall: {pr.recall:.2%}** (target ≥80%)",
            f"- Predicted-only: {pr.predicted_only[:10]}",
            f"- Gold-only (missed): {pr.gold_only[:10]}",
            "",
        ]

    lines += [
        "## Criterion C — User Audit",
        f"- **Pass rate: {audit_form_pass_rate:.2%}** (target ≥95%)" if audit_form_pass_rate is not None
            else "- (not yet filled in; run audit form first)",
        "",
        "## DB Summary",
        f"- Total mechanisms: {sum(len(v) for v in db.values())}",
        f"- Per-protocol counts:",
    ]
    for slug, mechs in sorted(db.items()):
        lines.append(f"  - `{slug}`: {len(mechs)}")

    md = "\n".join(lines)
    output_path.write_text(md)
    return {
        "criterion_a": {
            "ratio": a.coverage_ratio,
            "passes": a.coverage_ratio >= 0.95,
            "total": a.total_relevant,
            "covered": a.covered,
        },
        "criterion_b": {
            slug: {"precision": pr.precision, "recall": pr.recall,
                   "passes": pr.precision >= 0.90 and pr.recall >= 0.80}
            for slug, pr in b_results.items()
        },
        "criterion_c": {
            "rate": audit_form_pass_rate,
            "passes": (audit_form_pass_rate or 0.0) >= 0.95,
        },
    }
