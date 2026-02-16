from __future__ import annotations

import pytest

from llm_lab.clients.ollama_client import OllamaClient
from llm_lab.clients.openai_client import OpenAIClient
from llm_lab.config import Settings
from llm_lab.factory import LLMFactory


def test_factory_ollama() -> None:
    s = Settings(ollama_host="http://example:11434", ollama_model="mistral")
    c = LLMFactory.create("ollama", settings=s)
    assert isinstance(c, OllamaClient)


def test_factory_openai_requires_key() -> None:
    s = Settings(openai_api_key=None)
    with pytest.raises(ValueError):
        LLMFactory.create("openai", settings=s)


def test_factory_openai() -> None:
    s = Settings(openai_api_key="test", openai_model="gpt-5", openai_base_url="https://api.openai.com")
    c = LLMFactory.create("openai", settings=s)
    assert isinstance(c, OpenAIClient)
