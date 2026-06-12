"""Claude API wrapper with budget tracking and retry."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .budget import BudgetTracker


@dataclass
class LLMMessage:
    role: Literal["user", "assistant"]
    content: str


class LLMClient:
    def __init__(
        self,
        model: str,
        budget: BudgetTracker,
        api_key: str | None = None,
        max_tokens: int = 4096,
    ):
        self.model = model
        self.budget = budget
        self.max_tokens = max_tokens
        self._client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=30),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def complete(self, system: str, messages: list[LLMMessage]) -> str:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        self.budget.record(resp.usage.input_tokens, resp.usage.output_tokens, self.model)
        text_blocks = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        return "".join(text_blocks)
