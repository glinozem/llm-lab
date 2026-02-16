from __future__ import annotations

from typing import Protocol

from .types import Message


class LLMClient(Protocol):
    """Единый контракт для клиентов (OpenAI/Ollama/и т.д.)."""

    def generate(self, messages: list[Message]) -> str:
        """Сгенерировать ответ модели на список сообщений."""
        ...
