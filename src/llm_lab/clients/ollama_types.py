from __future__ import annotations

from typing import NotRequired, TypedDict


class OllamaMessage(TypedDict):
    role: str
    content: str


class OllamaChatResponse(TypedDict):
    message: OllamaMessage

    # остальное нам не важно, но реальный ответ содержит много полей
    model: NotRequired[str]
    created_at: NotRequired[str]
    done: NotRequired[bool]
