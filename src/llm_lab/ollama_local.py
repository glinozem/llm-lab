from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Literal

OllamaMode = Literal["generate", "chat"]


def extract_generate_text(resp: Mapping[str, Any]) -> str:
    """
    Ollama generate response (non-stream):
      {"response": "...", "done": true, ...}
    """
    text = resp.get("response")
    if isinstance(text, str):
        return text
    raise KeyError("response")


def extract_chat_text(resp: Mapping[str, Any]) -> str:
    """
    Ollama chat response (non-stream):
      {"message": {"role": "...", "content": "..."}, ...}
    """
    msg = resp.get("message")
    if isinstance(msg, Mapping):
        content = msg.get("content")
        if isinstance(content, str):
            return content

    # fallback for some shapes
    text = resp.get("response")
    if isinstance(text, str):
        return text

    raise KeyError("message.content")


def extract_stream_piece(chunk: Mapping[str, Any], mode: OllamaMode) -> str:
    """
    Stream chunks are JSON dicts. We extract the incremental text piece.
    """
    if mode == "generate":
        piece = chunk.get("response")
        return piece if isinstance(piece, str) else ""
    # chat
    msg = chunk.get("message")
    if isinstance(msg, Mapping):
        piece = msg.get("content")
        return piece if isinstance(piece, str) else ""
    return ""


def join_stream(chunks: Iterable[Mapping[str, Any]], mode: OllamaMode) -> str:
    return "".join(extract_stream_piece(c, mode) for c in chunks)
