from __future__ import annotations

from typing import Literal, Protocol, TypedDict


Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


class LLMClient(Protocol):
    def generate(self, messages: list[Message]) -> str: ...
