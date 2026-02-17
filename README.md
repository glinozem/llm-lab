# llm-lab

Учебно‑практический “лаб” для инженерии LLM на Python: **строго типизированные клиенты** для **OpenAI** и **Ollama**, небольшой CLI, аккуратные проверки качества и CI.

## Что внутри

- **Строгая типизация**
  - `TypedDict Message` (сообщения)
  - `Protocol`‑контракт `LLMClient.generate(list[Message]) -> str`
- **LLMFactory** с `@overload + Literal` — type checker выводит конкретные типы клиентов
- **CLI**
  - команда `llm-lab`
  - entrypoint: `python -m llm_lab`
- **Ollama для WSL2 ↔ Windows**
  - Windows: `ollama serve` слушает `0.0.0.0:11434`
  - WSL: доступ через default gateway (fallback)
- **Quality gates / CI**
  - `ruff` (format + lint)
  - `mypy` (строго)
  - `mypy-smoke` (`reveal_type` для overload’ов)
  - `pytest` unit
  - `pytest` integration (для Ollama)

## Требования

- Python **3.12+** (CI: 3.12/3.13)
- Для Ollama:
  - Windows: установлен Ollama
  - WSL2: доступ к Ollama, запущенному на Windows

## Установка

```bash
python -m venv .venv
. .venv/bin/activate

python -m pip install -U pip
pip install -e ".[dev]"
```

> `.env` пока не обязателен: настройки читаются из переменных окружения; `.env` — опционален.

## Конфигурация (env vars)

- `LLM_PROVIDER=ollama|openai`
- `OLLAMA_HOST=http://<host>:11434`
- `OLLAMA_MODEL=<model>`
- `OPENAI_API_KEY=<key>`
- `OPENAI_BASE_URL=https://api.openai.com`
- `OPENAI_MODEL=<model>`

## Ollama: Windows + WSL2

### 1) Запуск Ollama на Windows

PowerShell:

```powershell
.\scripts\ollama_serve.ps1
```

Скрипт выставляет `OLLAMA_HOST=0.0.0.0:11434` и запускает `ollama serve`.

### 2) Проверка из WSL2

```bash
make ollama-ping
make integration
```

`make integration` печатает итоговый `OLLAMA_HOST=...` и запускает `pytest` с маркером `integration`.

---

## Быстрый старт “как в курсе” (без .env)

### 1) Windows: поднять Ollama сервер

PowerShell:

```powershell
.\scripts\ollama_serve.ps1
```

### 2) WSL2: настроить доступ к Ollama на Windows

```bash
export OLLAMA_HOST="http://$(ip -4 route show default | awk '{print $3; exit}'):11434"
export OLLAMA_MODEL="mistral"
```

Проверка:

```bash
make ollama-ping
```

### 3) Запросы из Python (наш “взрослый” скрипт)

generate:

```bash
python scripts/local_llm.py generate --prompt "ping"
```

chat:

```bash
python scripts/local_llm.py chat --prompt "Что такое FastAPI?"
```

stream:

```bash
python scripts/local_llm.py chat --prompt "Расскажи про миграции в БД" --stream
```

---

## Мини-скрипт “по‑взрослому”: `scripts/local_llm.py`

Скрипт поддерживает:

- `generate` / `chat`
- `--stream`
- берёт `OLLAMA_HOST` / `OLLAMA_MODEL` из окружения (или использует дефолты проекта)
- аккуратный “dry parsing” ответов Ollama (поддерживаются и dict-ответы, и объектные ответы `ollama-python`)

Примеры:

```bash
python scripts/local_llm.py generate --prompt "Что такое Alembic?"
python scripts/local_llm.py chat --prompt "Что такое FastAPI?"
python scripts/local_llm.py chat --prompt "Расскажи про миграции в БД" --stream
```

## Разработка и проверки

Главная команда:

```bash
make check
```

Полезные таргеты:

- `make format` / `make format-check`
- `make lint`
- `make typecheck`
- `make mypy-smoke`
- `make test` (unit)
- `make integration` (требует Ollama)
- `make makefile-smoke` (защита от “missing separator”: рецепты Makefile должны начинаться с TAB)

## Снимки проекта (sanitized snapshot)

```bash
./scripts/snapshot_project.sh
(cd artifacts/snapshots && sha256sum -c *.sha256)
```

В архиве:

- `repo/` — санитизированная копия репозитория
- `report/` — метаданные окружения/команды/secret-smoke
