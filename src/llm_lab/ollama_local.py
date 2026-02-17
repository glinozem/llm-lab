from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Literal

OllamaMode = Literal["generate", "chat"]


def _get(obj: Any, key: str) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(key)
    return getattr(obj, key, None)


def _raise_if_error(resp: Any) -> None:
    err = _get(resp, "error")
    if isinstance(err, str) and err:
        raise RuntimeError(err)


def extract_generate_text(resp: Any) -> str:
    _raise_if_error(resp)
    text = _get(resp, "response")
    if isinstance(text, str):
        return text
    raise KeyError("response")


def extract_chat_text(resp: Any) -> str:
    _raise_if_error(resp)

    msg = _get(resp, "message")
    content = _get(msg, "content")
    if isinstance(content, str):
        return content

    # fallback
    text = _get(resp, "response")
    if isinstance(text, str):
        return text

    raise KeyError("message.content")


def extract_stream_piece(chunk: Any, mode: OllamaMode) -> str:
    _raise_if_error(chunk)

    if mode == "generate":
        piece = _get(chunk, "response")
        return piece if isinstance(piece, str) else ""

    msg = _get(chunk, "message")
    piece = _get(msg, "content")
    return piece if isinstance(piece, str) else ""


def join_stream(chunks: Iterable[Any], mode: OllamaMode) -> str:
    return "".join(extract_stream_piece(c, mode) for c in chunks)
