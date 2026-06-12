"""Criterion B: P/R against gold standard (spec §3.B)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PRResult:
    precision: float
    recall: float
    matched: list[str]
    predicted_only: list[str]
    gold_only: list[str]


def _key(ir: dict) -> str:
    return ir["id"].lower()


def compare_against_gold(*, predicted: list[dict], gold: list[dict]) -> PRResult:
    pred_keys = {_key(ir) for ir in predicted}
    gold_keys = {_key(ir) for ir in gold}
    matched = sorted(pred_keys & gold_keys)
    pred_only = sorted(pred_keys - gold_keys)
    gold_only = sorted(gold_keys - pred_keys)
    p = len(matched) / len(pred_keys) if pred_keys else 0.0
    r = len(matched) / len(gold_keys) if gold_keys else 0.0
    return PRResult(precision=p, recall=r, matched=matched,
                    predicted_only=pred_only, gold_only=gold_only)
