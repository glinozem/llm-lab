from __future__ import annotations

from typing import Literal, TypedDict

Role = Literal["system", "developer", "user", "assistant"]
Provider = Literal["ollama", "openai"]


class Message(TypedDict):
    role: Role
    content: str
