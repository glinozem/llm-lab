from __future__ import annotations

import socket
import struct
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from llm_lab.types import Provider


def _is_wsl() -> bool:
    # Works for WSL1/WSL2
    return bool(
        (
            Path("/proc/version").exists()
            and "microsoft" in Path("/proc/version").read_text().lower()
        )
        or ("WSL_DISTRO_NAME" in __import__("os").environ)
    )


def _wsl_default_gateway() -> str | None:
    # Parse /proc/net/route (more reliable than /etc/resolv.conf in your setup)
    try:
        txt = Path("/proc/net/route").read_text().splitlines()
    except OSError:
        return None

    for line in txt[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        dest, gateway = parts[1], parts[2]
        if dest != "00000000":
            continue
        try:
            gw = int(gateway, 16)
            return socket.inet_ntoa(struct.pack("<L", gw))
        except ValueError:
            return None
    return None


def _default_ollama_host() -> str:
    # If env is set, pydantic will use it anyway; this is the fallback default.
    if _is_wsl():
        gw = _wsl_default_gateway()
        if gw:
            return f"http://{gw}:11434"
    return "http://127.0.0.1:11434"


def default_ollama_host() -> str:
    """Backward-compatible public helper."""
    return _default_ollama_host()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Provider = "ollama"

    ollama_host: str = Field(default_factory=_default_ollama_host)
    ollama_model: str = "mistral"

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com"
    openai_model: str = "gpt-5"

    @field_validator("ollama_host")
    @classmethod
    def _normalize_ollama_host(cls, v: str) -> str:
        v = v.strip()
        if "://" not in v:
            v = "http://" + v
        return v.rstrip("/")
