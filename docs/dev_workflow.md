# Dev workflow

Этот документ — короткая шпаргалка по ежедневной разработке в `llm-lab`.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip

# Быстрый вариант (ставим из pyproject.toml)
pip install -e ".[dev]"

# Вариант “как в CI” (пинованные зависимости из requirements-dev.txt)
# make sync
```

## Lockfiles (uv)

В репозитории есть два “lockfile-подобных” файла, генерируемых из `pyproject.toml`:

- `requirements.txt` — runtime зависимости
- `requirements-dev.txt` — runtime + dev (`--extra dev`)

Генерация делается через `uv pip compile`.

### Команды

Сгенерировать/обновить оба файла:
```bash
make lock
```

Проверить, что локальные `requirements*.txt` соответствуют `pyproject.toml` (пересобирает и падает, если есть diff):
```bash
make lock-check
```

Синхронизировать окружение “как в CI” (нужны существующие `requirements-dev.txt`):
```bash
make sync
```

### Как обновлять после Dependabot PR

Dependabot может обновлять:

- `requirements*.txt` напрямую (чаще всего для `pip` ecosystem)
- `pyproject.toml` (если он соответствует PEP 621)

Рекомендованный порядок действий для PR с обновлениями зависимостей:

1) Смёрджить PR нельзя, пока CI зелёный.
2) Локально прогнать:
   ```bash
   make check
   make lock-check
   ```
3) Если `make lock-check` упал (появился diff), то:
   ```bash
   make lock
   git add requirements.txt requirements-dev.txt
   git commit -m "deps: regen requirements via uv"
   ```
   и допушить коммит в ветку PR.

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
