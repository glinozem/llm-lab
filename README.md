# llm-lab

Учебно-практический “лаб” для инженерии LLM на Python: **строго типизированные клиенты** для **OpenAI** и **Ollama**, небольшой CLI, аккуратные проверки качества и CI.

## Что внутри

- **Строгая типизация**
  - `TypedDict Message` (сообщения)
  - `Protocol`-контракт `LLMClient.generate(list[Message]) -> str`
- **LLMFactory** с `@overload + Literal` — type checker выводит конкретные типы клиентов
- **CLI**
  - консольная команда `llm-lab`
  - entrypoint: `python -m llm_lab`
- **Настройки** из окружения / `.env` (через `pydantic-settings`)
- **Ollama для WSL2 ↔ Windows**
  - Windows: `ollama serve` слушает `0.0.0.0:11434`
  - WSL: доступ через default gateway (fallback)
- **Quality gates / CI**
  - `ruff` (format + lint)
  - `mypy` (строго)
  - `mypy-smoke` (проверка `reveal_type` для overload’ов)
  - `pytest` unit
  - `pytest` integration (для Ollama)

---

## Требования

- Python **3.12+** (CI: 3.12/3.13)
- Для Ollama:
  - Windows: установлен Ollama
  - WSL2: доступ к Ollama, запущенному на Windows

---

## Установка

```bash
python -m venv .venv
. .venv/bin/activate

python -m pip install -U pip
pip install -e ".[dev]"
```

---

## Конфигурация

```bash
cp .env.example .env
```

Типовые переменные окружения:

- `LLM_PROVIDER=ollama|openai`
- `OLLAMA_HOST=http://<host>:11434`
- `OLLAMA_MODEL=<model>`
- `OPENAI_API_KEY=<key>`
- `OPENAI_BASE_URL=https://api.openai.com`
- `OPENAI_MODEL=<model>`

> Примечание: если `OLLAMA_HOST` не задан в WSL, проект может брать host как default gateway из таблицы маршрутизации.

---

## Использование

### 1) Один prompt

**Ollama:**
```bash
python -m llm_lab --provider ollama --model mistral --prompt "ping"
```

**OpenAI:**
```bash
export OPENAI_API_KEY="..."
python -m llm_lab --provider openai --model gpt-5 --prompt "Скажи привет"
```

### 2) Режим сообщений

`role:content`, где `role` ∈ `system|developer|user|assistant`:

```bash
python -m llm_lab   --provider ollama   --model mistral   --message "system:Ты полезный ассистент."   --message "developer:Отвечай точно и кратко."   --message "user:Объясни, что такое Protocol в typing."
```

---

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

---

## Снимки проекта (sanitized snapshot)

```bash
./scripts/snapshot_project.sh
(cd artifacts/snapshots && sha256sum -c *.sha256)
```

В архиве:
- `repo/` — санитизированная копия репозитория
- `report/` — метаданные окружения/команды/secret-smoke

---

## Следующий шаг (RAG → агенты)

- v0.2: **Embeddings contract + providers** → минимальный **RAG** → CLI `rag ingest/ask`
- v0.3: **tool interface + agent loop** + минимальный eval harness
