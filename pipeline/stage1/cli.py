"""Stage 1 orchestrator CLI: run pipeline for one protocol."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from pipeline.stage1.config import (
    PASS1_MODEL, PASS2_MODEL, POC_MODEL,
    HARD_USD_BUDGET, MECHANISM_DB, CORPUS_TIER_A,
    IR_SCHEMA_PATH, PIPELINE_VERSION,
)
from pipeline.stage1.db.writer import write_mechanism, DBWriteError
from pipeline.stage1.flagger import Flagger
from pipeline.stage1.llm.budget import BudgetTracker
from pipeline.stage1.llm.client import LLMClient
from pipeline.stage1.pass1.consensus import run_consensus
from pipeline.stage1.pass2.extractor import extract_ir
from pipeline.stage1.pass2.tool_registry import ToolRegistry
from pipeline.stage1.poc.generator import generate_poc
from pipeline.stage1.poc.verifier import verify_poc
from pipeline.stage1.prepare import prepare_protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("stage1.cli")


def run_protocol(
    metadata_path: Path,
    benchmark_events: list[dict],
    incident_protocols: set[str],
    cross_calls: set[str],
    db_root: Path,
    foundry_root: Path,
) -> dict:
    bundle = prepare_protocol(metadata_path)
    log.info("Starting protocol: %s on %s", bundle.name, bundle.chain)

    budget = BudgetTracker(usd_hard_cap=HARD_USD_BUDGET)
    with budget.scope(bundle.slug):
        pass1_client = LLMClient(model=PASS1_MODEL, budget=budget)
        consensus = run_consensus(
            llm_client=pass1_client,
            protocol_name=bundle.name,
            protocol_chain=bundle.chain,
            source_blob=bundle.source_blob,
            docs_blob=bundle.docs_blob,
        )
        log.info(
            "Pass 1 produced %d stubs (rounds=%d)",
            len(consensus.stubs),
            consensus.rounds,
        )

        flagger = Flagger(
            benchmark_events=benchmark_events,
            cross_protocol_calls=cross_calls,
            incident_protocols=incident_protocols,
        )
        flagged = []
        for s in consensus.stubs:
            d = flagger.flag(s, protocol_name=bundle.name)
            if d.flagged:
                flagged.append((s, d.reasons))
        log.info("Flagged %d stubs for Pass 2", len(flagged))

        ir_schema = json.loads(IR_SCHEMA_PATH.read_text())
        pass2_client = LLMClient(model=PASS2_MODEL, budget=budget)
        poc_client = LLMClient(model=POC_MODEL, budget=budget)
        tool_reg = ToolRegistry()

        written = 0
        dropped = 0
        for stub, reasons in flagged:
            ir, pass2_attempts = extract_ir(
                llm_client=pass2_client,
                stub=stub,
                tool_registry=tool_reg,
                source_blob=bundle.source_blob,
                docs_blob=bundle.docs_blob,
                ir_schema=ir_schema,
                source_path=bundle.source_path,
            )
            if ir is None:
                dropped += 1
                continue

            poc_source = None
            poc_attempts = 0
            poc_feedback = ""
            for attempt in range(1, 4):
                poc_attempts = attempt
                source = generate_poc(
                    llm_client=poc_client,
                    ir=ir,
                    source_blob=bundle.source_blob,
                    feedback=poc_feedback,
                )
                state_writes = [w.get("variable", "") for w in ir.get("state_writes", [])]
                test_name = ir["poc"]["test_name"]
                poc_subdir = db_root / bundle.chain / bundle.slug / ir["id"]
                result = verify_poc(
                    source=source,
                    test_name=test_name,
                    mechanism_tags=ir["tags"],
                    state_writes=state_writes,
                    foundry_root=foundry_root,
                    poc_subdir=poc_subdir,
                )
                if result.passed:
                    poc_source = source
                    break
                poc_feedback = (
                    f"Previous PoC attempt #{attempt} failed: {result.reason}\n"
                    f"Stderr:\n{result.stderr[:2000]}"
                )

            if poc_source is None:
                dropped += 1
                continue

            k = stub.stub_id.lower()
            metrics = {
                "mechanism_id": ir["id"],
                "consensus_level": consensus.consensus_levels.get(k, "majority-2of3"),
                "consensus_rounds": consensus.rounds,
                "subagent_proposals": consensus.subagent_proposals.get(
                    k, {"A": "", "B": "", "C": ""}
                ),
                "extraction_pass": 2,
                "pass2_attempts": pass2_attempts,
                "poc_attempts": poc_attempts,
                "flagged_reasons": reasons,
                "provenance_quality": "code-only",
                "extraction_pipeline_version": PIPELINE_VERSION,
                "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            ir["poc"]["status"] = "passing"
            try:
                write_mechanism(
                    ir=ir,
                    metrics=metrics,
                    poc_source=poc_source,
                    db_root=db_root,
                    protocol_slug=bundle.slug,
                )
                written += 1
            except DBWriteError as e:
                log.error("DB write failed for %s: %s", ir["id"], e)
                dropped += 1

    scope_data = budget.per_scope().get(bundle.slug, {"input_tokens": 0, "output_tokens": 0})
    usd_used = budget._compute_usd(
        scope_data["input_tokens"],
        scope_data["output_tokens"],
        PASS2_MODEL,
    )

    return {
        "protocol": bundle.slug,
        "stubs_total": len(consensus.stubs),
        "flagged": len(flagged),
        "written": written,
        "dropped": dropped,
        "usd_used": usd_used,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PRISM Stage 1 pipeline (per-protocol)"
    )
    parser.add_argument(
        "--metadata", required=True, type=Path, help="Path to protocol metadata.json"
    )
    parser.add_argument(
        "--db", type=Path, default=MECHANISM_DB, help="Mechanism DB root"
    )
    parser.add_argument(
        "--foundry-root",
        type=Path,
        default=Path.cwd(),
        help="Directory containing foundry.toml",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("benchmark/events"),
        help="Benchmark events dir",
    )
    args = parser.parse_args()

    benchmark_events = []
    for ev_file in args.benchmark.rglob("*.json"):
        benchmark_events.append(json.loads(ev_file.read_text()))

    cross_calls: set[str] = set()
    incident_protocols: set[str] = {
        ev["involved_protocols"][0]
        for ev in benchmark_events
        if ev.get("involved_protocols")
    }

    summary = run_protocol(
        metadata_path=args.metadata,
        benchmark_events=benchmark_events,
        incident_protocols=incident_protocols,
        cross_calls=cross_calls,
        db_root=args.db,
        foundry_root=args.foundry_root,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
