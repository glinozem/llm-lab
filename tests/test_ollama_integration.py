from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.integration


def _norm(host: str) -> str:
    host = host.strip()
    if not host:
        return host
    if "://" not in host:
        host = "http://" + host
    return host.rstrip("/")


def test_ollama_tags_reachable() -> None:
    host = _norm(os.environ.get("OLLAMA_HOST", ""))
    if not host:
        pytest.skip("OLLAMA_HOST is not set")

    try:
        r = httpx.get(f"{host}/api/tags", timeout=2.0)
    except Exception as e:
        pytest.skip(f"Ollama not reachable at {host}: {e}")

    r.raise_for_status()
    data = r.json()
    assert "models" in data
