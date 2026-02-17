#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from ollama import Client

from llm_lab.ollama_local import extract_chat_text, extract_generate_text, extract_stream_piece
from llm_lab.settings import Settings
from llm_lab.types import Message, Role

_ALLOWED_ROLES: set[Role] = {"system", "developer", "user", "assistant"}


def _parse_message(s: str) -> Message:
    if ":" not in s:
        raise ValueError('Message must be "role:content"')
    role_raw, content = s.split(":", 1)
    role = role_raw.strip()
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"Invalid role: {role!r}. Allowed: {sorted(_ALLOWED_ROLES)}")
    content = content.strip()
    if not content:
        raise ValueError("Message content must be non-empty")
    return {"role": role, "content": content}  # type: ignore[return-value]


def _env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None:
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def build_parser() -> argparse.ArgumentParser:
    p = (
        argparse.ArgumentParser(
            prog="local_llm",
            description="Local Ollama runner (generate/chat/stream) "
            "using env OLLAMA_HOST/OLLAMA_MODEL.",
        ),
    )

    sub = p.add_subparsers(dest="mode", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--prompt", type=str, help="Prompt text (if --message not provided).")
        sp.add_argument(
            "--message",
            action="append",
            default=[],
            help='Chat message in "role:content" form (repeatable).',
        )
        sp.add_argument("--stream", action="store_true", help="Stream tokens to stdout.")
        sp.add_argument(
            "--host", type=str, default=None, help="Override Ollama host (env by default)."
        )
        sp.add_argument("--model", type=str, default=None, help="Override model (env by default).")
        sp.add_argument(
            "--temperature", type=float, default=None, help="Override temperature (env by default)."
        )
        sp.add_argument(
            "--num-ctx", type=int, default=None, help="Override context size (env by default)."
        )

    sp_gen = sub.add_parser("generate", help="Use Ollama generate endpoint.")
    common(sp_gen)

    sp_chat = sub.add_parser("chat", help="Use Ollama chat endpoint.")
    common(sp_chat)

    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)

    settings = Settings()  # .env optional; env vars work even if file absent
    host = args.host or settings.ollama_host
    model = args.model or settings.ollama_model

    temperature = (
        args.temperature if args.temperature is not None else _env_float("OLLAMA_TEMPERATURE", 0.2)
    )
    num_ctx = args.num_ctx if args.num_ctx is not None else _env_int("OLLAMA_NUM_CTX", 2048)

    options: dict[str, Any] = {"temperature": temperature, "num_ctx": num_ctx}

    client = Client(host=host)

    # Build messages for chat; for generate we only need prompt.
    messages: list[Message] = []
    if args.message:
        messages = [_parse_message(m) for m in args.message]
    elif args.prompt:
        messages = [{"role": "user", "content": args.prompt}]
    else:
        print("Error: provide --prompt or at least one --message", file=sys.stderr)
        return 2

    try:
        if args.mode == "generate":
            # For generate: use prompt (prefer explicit --prompt, else use last user message)
            prompt = args.prompt
            if prompt is None:
                # derive from last user message if possible
                user_msgs = [m["content"] for m in messages if m["role"] == "user"]
                prompt = user_msgs[-1] if user_msgs else messages[-1]["content"]

            if args.stream:
                for chunk in client.generate(
                    model=model, prompt=prompt, options=options, stream=True
                ):
                    sys.stdout.write(extract_stream_piece(chunk, "generate"))
                    sys.stdout.flush()
                sys.stdout.write("\n")
                return 0

            resp = client.generate(model=model, prompt=prompt, options=options, stream=False)
            print(extract_generate_text(resp))
            return 0

        # chat
        if args.stream:
            for chunk in client.chat(model=model, messages=messages, options=options, stream=True):
                sys.stdout.write(extract_stream_piece(chunk, "chat"))
                sys.stdout.flush()
            sys.stdout.write("\n")
            return 0

        resp = client.chat(model=model, messages=messages, options=options, stream=False)
        print(extract_chat_text(resp))
        return 0

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
