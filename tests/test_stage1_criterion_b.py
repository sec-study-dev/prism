"""Tests for Criterion B: gold-standard P/R comparison."""
import pytest
from pipeline.stage1.evaluation.criterion_b import compare_against_gold, PRResult


def _ir(mid: str, tags: list[str]) -> dict:
    return {"id": mid, "tags": tags, "trigger": {"entry_point": mid.split(".")[-1]}}


def test_perfect_match():
    gold = [_ir("v.a", ["lifecycle-hook"]), _ir("v.b", ["share-asset-pricing"])]
    pred = [_ir("v.a", ["lifecycle-hook"]), _ir("v.b", ["share-asset-pricing"])]
    r = compare_against_gold(predicted=pred, gold=gold)
    assert r.precision == 1.0
    assert r.recall == 1.0


def test_extra_predictions_lower_precision():
    gold = [_ir("v.a", ["lifecycle-hook"])]
    pred = [_ir("v.a", ["lifecycle-hook"]), _ir("v.b", ["function-callable"])]
    r = compare_against_gold(predicted=pred, gold=gold)
    assert r.precision == 0.5
    assert r.recall == 1.0


def test_missing_predictions_lower_recall():
    gold = [_ir("v.a", ["lifecycle-hook"]), _ir("v.b", ["share-asset-pricing"])]
    pred = [_ir("v.a", ["lifecycle-hook"])]
    r = compare_against_gold(predicted=pred, gold=gold)
    assert r.precision == 1.0
    assert r.recall == 0.5


def test_match_by_id_case_insensitive():
    gold = [_ir("V.A", ["function-callable"])]
    pred = [_ir("v.a", ["function-callable"])]
    r = compare_against_gold(predicted=pred, gold=gold)
    assert r.precision == 1.0
