from __future__ import annotations

import os
import subprocess

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from llm_lab.types import Provider


def is_wsl() -> bool:
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def default_ollama_host() -> str:
    if os.getenv("OLLAMA_HOST"):
        return os.environ["OLLAMA_HOST"]

    if is_wsl():
        try:
            gw = subprocess.check_output(
                ["sh", "-lc", "ip -4 route show default | cut -d' ' -f3"],
                text=True,
            ).strip()
            if gw:
                return f"http://{gw}:11434"
        except Exception:
            pass

    return "http://localhost:11434"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Provider = "ollama"

    ollama_host: str = Field(default_factory=default_ollama_host)
    ollama_model: str = "mistral"

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com"
    openai_model: str = "gpt-5"

