from __future__ import annotations

from typing import cast

from ollama import Client

from llm_lab.config import default_ollama_host
from llm_lab.types import Message
from llm_lab.clients.ollama_types import OllamaChatResponse


class OllamaClient:
    def __init__(self, model: str = "mistral", host: str | None = None) -> None:
        self.model = model
        self._client = Client(host=host or default_ollama_host())

    def generate(self, messages: list[Message]) -> str:
        resp = cast(
            OllamaChatResponse,
            self._client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.2, "num_ctx": 2048},
            ),
        )
        return resp["message"]["content"]
