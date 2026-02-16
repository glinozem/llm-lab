from __future__ import annotations

from typing import Literal, overload

from llm_lab.clients.ollama_client import OllamaClient
from llm_lab.clients.openai_client import OpenAIClient
from llm_lab.config import Settings
from llm_lab.types import LLMClient, Provider


class LLMFactory:
    @overload
    @staticmethod
    def create(provider: Literal["ollama"], /, *, settings: Settings | None = None) -> OllamaClient: ...

    @overload
    @staticmethod
    def create(provider: Literal["openai"], /, *, settings: Settings | None = None) -> OpenAIClient: ...

    @overload
    @staticmethod
    def create(provider: Provider, /, *, settings: Settings | None = None) -> OpenAIClient | OllamaClient: ...

    @overload
    @staticmethod
    def create(provider: str, /, *, settings: Settings | None = None) -> LLMClient: ...

    @staticmethod
    def create(provider: str, /, *, settings: Settings | None = None) -> LLMClient:
        s = settings or Settings()

        if provider == "ollama":
            return OllamaClient(model=s.ollama_model, host=s.ollama_host)

        if provider == "openai":
            if not s.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for provider='openai'")
            return OpenAIClient(
                api_key=s.openai_api_key,
                model=s.openai_model,
                base_url=s.openai_base_url,
            )

        raise ValueError(f"Unsupported provider: {provider!r}")
