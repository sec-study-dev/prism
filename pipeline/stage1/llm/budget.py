"""Token / USD budget tracking with per-scope isolation."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field


# Sonnet 4.6 pricing per 1M tokens (rough); update if model/pricing changes
MODEL_PRICING_PER_MTOKEN = {
    "claude-sonnet-4-6": (3.0, 15.0),  # (input, output)
    "claude-opus-4-7": (15.0, 75.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
}


@dataclass
class _ScopeAccum:
    input_tokens: int = 0
    output_tokens: int = 0


class BudgetTracker:
    def __init__(self, usd_hard_cap: float | None = None):
        self.input_tokens = 0
        self.output_tokens = 0
        self._scopes: dict[str, _ScopeAccum] = {}
        self._current_scope: str | None = None
        self.usd_hard_cap = usd_hard_cap

    @property
    def usd_estimate(self) -> float:
        return self._compute_usd(self.input_tokens, self.output_tokens, "claude-sonnet-4-6")

    def _compute_usd(self, in_tok: int, out_tok: int, model: str) -> float:
        in_price, out_price = MODEL_PRICING_PER_MTOKEN.get(model, (3.0, 15.0))
        return in_tok / 1_000_000 * in_price + out_tok / 1_000_000 * out_price

    @contextmanager
    def scope(self, name: str):
        prev = self._current_scope
        self._current_scope = name
        self._scopes.setdefault(name, _ScopeAccum())
        try:
            yield
        finally:
            self._current_scope = prev

    def record(self, input_tokens: int, output_tokens: int, model: str) -> None:
        if self.usd_hard_cap is not None:
            projected = self._compute_usd(
                self.input_tokens + input_tokens,
                self.output_tokens + output_tokens,
                model,
            )
            if projected > self.usd_hard_cap:
                raise RuntimeError(f"budget exceeded: ${projected:.2f} > cap ${self.usd_hard_cap:.2f}")
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        if self._current_scope is not None:
            s = self._scopes[self._current_scope]
            s.input_tokens += input_tokens
            s.output_tokens += output_tokens

    def per_scope(self) -> dict:
        return {
            name: {"input_tokens": s.input_tokens, "output_tokens": s.output_tokens}
            for name, s in self._scopes.items()
        }
