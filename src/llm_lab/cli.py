from __future__ import annotations

import argparse
import sys
from typing import cast

import httpx

from llm_lab.factory import LLMFactory
from llm_lab.settings import Settings
from llm_lab.types import Message, Provider, Role

DEFAULT_SYSTEM = "You are a helpful assistant."
DEFAULT_DEVELOPER = "Follow the developer instructions and be precise."
ALLOWED_ROLES: tuple[Role, ...] = ("system", "developer", "user", "assistant")


def _parse_message(raw: str) -> Message:
    # Format: role:content (split only on the first ':')
    if ":" not in raw:
        raise ValueError("expected ROLE:CONTENT")
    role_s, content = raw.split(":", 1)
    role = role_s.strip()
    content = content.lstrip()
    if not content:
        raise ValueError("empty content")

    if role not in ALLOWED_ROLES:
        raise ValueError(f"unknown role {role!r}; allowed: {', '.join(ALLOWED_ROLES)}")

    return {"role": cast(Role, role), "content": content}


def _ensure_defaults(
    messages: list[Message],
    *,
    system_text: str,
    developer_text: str,
) -> list[Message]:
    roles = {m["role"] for m in messages}
    out = list(messages)

    if "system" not in roles:
        out.insert(0, {"role": "system", "content": system_text})

    roles = {m["role"] for m in out}
    if "developer" not in roles:
        insert_at = 1 if out and out[0]["role"] == "system" else 0
        out.insert(insert_at, {"role": "developer", "content": developer_text})

    return out


def _friendly_httpx_error(e: httpx.HTTPError) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        r = e.response
        req = r.request
        try:
            detail = str(r.json())
        except Exception:
            detail = (r.text or "").strip()
        detail = detail[:800]
        return f"HTTP {r.status_code} calling {req.method} {req.url}\n{detail}".strip()
    if isinstance(e, httpx.RequestError):
        req = e.request
        return f"Network error calling {req.method} {req.url}: {e}"
    return f"HTTP client error: {e}"


def main() -> None:
    p = argparse.ArgumentParser(prog="llm-lab")
    p.add_argument("--provider", choices=["ollama", "openai"])
    p.add_argument("--model")
    p.add_argument("--ollama-host")
    p.add_argument("--openai-base-url")
    p.add_argument("--openai-api-key")

    # Defaults for headers (used if messages do not contain system/developer)
    p.add_argument("--system", default=DEFAULT_SYSTEM)
    p.add_argument("--developer", default=DEFAULT_DEVELOPER)

    # Old single-prompt mode (optional now)
    p.add_argument("--prompt")

    # New multi-message mode
    p.add_argument(
        "--message",
        action="append",
        default=[],
        help="Repeatable. Format: role:content (system|developer|user|assistant)",
    )

    args = p.parse_args()

    s = Settings()
    provider: Provider = args.provider or s.llm_provider

    if args.model:
        if provider == "ollama":
            s.ollama_model = args.model
        else:
            s.openai_model = args.model

    if args.ollama_host:
        s.ollama_host = args.ollama_host
    if args.openai_base_url:
        s.openai_base_url = args.openai_base_url
    if args.openai_api_key:
        s.openai_api_key = args.openai_api_key

    client = LLMFactory.create(provider, settings=s)

    messages: list[Message] = []

    if args.message:
        try:
            messages.extend(_parse_message(m) for m in args.message)
        except ValueError as e:
            print(f"Invalid --message: {e}", file=sys.stderr)
            raise SystemExit(2) from e

    if args.prompt:
        messages.append({"role": "user", "content": args.prompt})

    if not messages:
        print("Provide --prompt or at least one --message", file=sys.stderr)
        raise SystemExit(2)

    messages = _ensure_defaults(
        messages,
        system_text=args.system,
        developer_text=args.developer,
    )

    try:
        print(client.generate(messages))
    except httpx.HTTPError as e:
        print(_friendly_httpx_error(e), file=sys.stderr)
        raise SystemExit(2) from e
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(2) from e


if __name__ == "__main__":
    main()
