from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from llm_lab.types import Message


@dataclass(frozen=True, slots=True)
class OpenAIClient:
    api_key: str
    model: str
    base_url: str = "https://api.openai.com"
    timeout_s: float = 60.0
    _http: httpx.Client | None = None  # DI for tests

    def generate(self, messages: list[Message]) -> str:
        url = f"{self.base_url.rstrip('/')}/v1/responses"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        client = self._http or httpx.Client(timeout=self.timeout_s)
        try:
            resp = client.post(url, headers=headers, json={"model": self.model, "input": messages})
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        finally:
            if self._http is None:
                client.close()

        return _extract_output_text(data)


def _extract_output_text(data: dict[str, Any]) -> str:
    out = data.get("output")
    if not isinstance(out, list):
        raise ValueError("OpenAI response: missing 'output' array")

    chunks: list[str] = []
    for item in out:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message" or item.get("role") != "assistant":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if isinstance(c, dict) and c.get("type") == "output_text":
                text = c.get("text")
                if isinstance(text, str):
                    chunks.append(text)

    text = "".join(chunks).strip()
    if not text:
        raise ValueError("OpenAI response: empty output_text")
    return text
