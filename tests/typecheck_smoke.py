from __future__ import annotations

from typing import TYPE_CHECKING, Literal, reveal_type

from llm_lab.factory import LLMFactory
from llm_lab.types import Provider

if TYPE_CHECKING:
    c1 = LLMFactory.create("ollama")
    reveal_type(c1)  # OllamaClient

    c2 = LLMFactory.create("openai")
    reveal_type(c2)  # OpenAIClient

    p: Provider = "ollama"
    c3 = LLMFactory.create(p)
    reveal_type(c3)  # OpenAIClient | OllamaClient

    p2: Literal["openai", "ollama"] = "openai"
    c4 = LLMFactory.create(p2)
    reveal_type(c4)  # OpenAIClient | OllamaClient
