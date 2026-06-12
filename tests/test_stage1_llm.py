"""Tests for Stage 1 LLM client and budget tracker."""
from unittest.mock import MagicMock, patch
import pytest

from pipeline.stage1.llm.client import LLMClient, LLMMessage
from pipeline.stage1.llm.budget import BudgetTracker


def test_budget_starts_zero():
    b = BudgetTracker()
    assert b.input_tokens == 0
    assert b.output_tokens == 0
    assert b.usd_estimate == 0.0


def test_budget_records_usage():
    b = BudgetTracker()
    b.record(input_tokens=1000, output_tokens=200, model="claude-sonnet-4-6")
    assert b.input_tokens == 1000
    assert b.output_tokens == 200
    assert b.usd_estimate > 0


def test_budget_aggregates():
    b = BudgetTracker()
    b.record(1000, 200, "claude-sonnet-4-6")
    b.record(500, 100, "claude-sonnet-4-6")
    assert b.input_tokens == 1500
    assert b.output_tokens == 300


def test_budget_per_protocol_isolation():
    b = BudgetTracker()
    with b.scope("aave-v3"):
        b.record(1000, 200, "claude-sonnet-4-6")
    with b.scope("uniswap-v4"):
        b.record(500, 100, "claude-sonnet-4-6")
    per = b.per_scope()
    assert per["aave-v3"]["input_tokens"] == 1000
    assert per["uniswap-v4"]["input_tokens"] == 500


def test_budget_hard_cap_triggers():
    b = BudgetTracker(usd_hard_cap=0.01)
    with pytest.raises(RuntimeError, match="budget exceeded"):
        b.record(10_000_000, 100_000, "claude-sonnet-4-6")


def test_llm_client_records_to_budget(mocker):
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="hi", type="text")]
    fake_response.usage = MagicMock(input_tokens=100, output_tokens=10)
    fake_response.stop_reason = "end_turn"

    mock_anthropic = mocker.patch("pipeline.stage1.llm.client.Anthropic")
    mock_anthropic.return_value.messages.create.return_value = fake_response

    budget = BudgetTracker()
    client = LLMClient(model="claude-sonnet-4-6", budget=budget, api_key="test")
    out = client.complete(
        system="be helpful",
        messages=[LLMMessage(role="user", content="hi")],
    )
    assert out == "hi"
    assert budget.input_tokens == 100
    assert budget.output_tokens == 10
