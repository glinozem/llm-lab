from __future__ import annotations

import os
import subprocess


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
