"""Run Stage 1 A/B/C evaluation, emit report + audit form."""
from __future__ import annotations

import sys
from pathlib import Path as _Path

# Ensure the project root is on sys.path when run as `python scripts/run_evaluation.py`
# (editable-install finders may not be active before site-packages is imported)
_PROJECT_ROOT = str(_Path(__file__).parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import argparse
import json
from pathlib import Path

from pipeline.stage1.evaluation.report import build_report
from pipeline.stage1.evaluation.criterion_c import (
    sample_audit_items, render_audit_form, compute_audit_pass_rate
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("mechanism-db"))
    parser.add_argument("--benchmark", type=Path, default=Path("benchmark/events"))
    parser.add_argument("--gold-dir", type=Path, default=Path("evaluation/gold"))
    parser.add_argument("--audit-form", type=Path, default=Path("audit-form.md"))
    parser.add_argument("--audit-form-tallied", type=Path, default=None,
                        help="If set, read pre-filled audit form and tally pass rate")
    parser.add_argument("--out", type=Path, default=Path("stage1-extraction-report.md"))
    args = parser.parse_args()

    benchmark = [json.loads(p.read_text()) for p in args.benchmark.rglob("*.json")]

    tier_a_names = []
    for mp in Path("corpus/tier-a/protocols").rglob("metadata.json"):
        tier_a_names.append(json.loads(mp.read_text())["name"])

    gold_paths: dict[str, Path] = {}
    if args.gold_dir.exists():
        for gp in args.gold_dir.glob("*.json"):
            gold_paths[gp.stem] = gp

    audit_rate: float | None = None
    if args.audit_form_tallied and args.audit_form_tallied.exists():
        text = args.audit_form_tallied.read_text()
        real = text.lower().count("| real |")
        fp = text.lower().count("| false-positive |")
        total = real + fp
        audit_rate = (real / total) if total else None
    else:
        if args.db.exists():
            items = sample_audit_items(
                db_root=args.db,
                exclude_protocols={"uniswap-v4", "curve-finance"},
                k_per_protocol=3, seed=2026,
            )
            render_audit_form(items, args.audit_form)
            print(f"Audit form written to {args.audit_form}. Fill it in, then re-run with --audit-form-tallied")
        else:
            print(f"DB root {args.db} does not exist yet (run the pipeline first); skipping audit form generation.")

    summary = build_report(
        db_root=args.db,
        benchmark_events=benchmark,
        tier_a_protocol_names=tier_a_names, gold_paths=gold_paths,
        audit_form_pass_rate=audit_rate, output_path=args.out,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
