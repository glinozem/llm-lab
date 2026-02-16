from __future__ import annotations

from typing import Literal

from llm_lab.clients.ollama_client import OllamaClient

Provider = Literal["ollama"]


class LLMFactory:
    @staticmethod
    def create(provider: Provider, /) -> OllamaClient:
        if provider == "ollama":
            return OllamaClient()
        raise ValueError(f"Unsupported provider: {provider}")
