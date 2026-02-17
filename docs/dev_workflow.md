# Dev workflow

Этот документ — короткая шпаргалка по ежедневной разработке в `llm-lab`.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
```

## Quality gates

Запуск всего набора проверок:
```bash
make check
```

Проверка, что в Makefile рецепты начинаются с TAB (защита от `missing separator`):
```bash
make makefile-smoke
```

## Ollama: WSL2 ↔ Windows

Windows (PowerShell):
```powershell
.\scripts\ollama_serve.ps1
```

WSL2:
```bash
source scripts/ollama_env.sh
make ollama-ping
```

Интеграционные тесты:
```bash
make integration
```

## Локальные запросы к Ollama

Через Makefile (автодетект Windows host по default gateway, если `OLLAMA_HOST` не задан):
```bash
make local-llm ARGS='chat --prompt "Hi!" --stream'
```

Напрямую через скрипт:
```bash
python scripts/local_llm.py chat --prompt "ping" --stream
python scripts/local_llm.py generate --prompt "Что такое FastAPI?"
```

## Создание snapshot (sanitized)

```bash
./scripts/snapshot_project.sh
(cd artifacts/snapshots && sha256sum -c *.sha256)
```
