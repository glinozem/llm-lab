from __future__ import annotations

from typing import Literal, reveal_type

from llm_lab.factory import LLMFactory

# Dedicated mypy-only file: asserts overload precision for LLMFactory.create().

oai = LLMFactory.create("openai")
reveal_type(oai)  # N: Revealed type is "llm_lab.clients.openai_client.OpenAIClient"

olm = LLMFactory.create("ollama")
reveal_type(olm)  # N: Revealed type is "llm_lab.clients.ollama_client.OllamaClient"

provider: Literal["openai", "ollama"] = "openai"
any_client = LLMFactory.create(provider)
reveal_type(any_client)  # N: Revealed type is "OpenAIClient | OllamaClient"
