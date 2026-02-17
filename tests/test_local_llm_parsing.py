from __future__ import annotations

from llm_lab.ollama_local import (
    extract_chat_text,
    extract_generate_text,
    join_stream,
)


def test_extract_generate_text() -> None:
    resp = {"response": "hello", "done": True}
    assert extract_generate_text(resp) == "hello"


def test_extract_chat_text() -> None:
    resp = {"message": {"role": "assistant", "content": "hi"}, "done": True}
    assert extract_chat_text(resp) == "hi"


def test_join_stream_generate() -> None:
    chunks = [
        {"response": "a", "done": False},
        {"response": "b", "done": False},
        {"response": "c", "done": True},
    ]
    assert join_stream(chunks, "generate") == "abc"


def test_join_stream_chat() -> None:
    chunks = [
        {"message": {"role": "assistant", "content": "x"}, "done": False},
        {"message": {"role": "assistant", "content": "y"}, "done": False},
        {"message": {"role": "assistant", "content": "z"}, "done": True},
    ]
    assert join_stream(chunks, "chat") == "xyz"
