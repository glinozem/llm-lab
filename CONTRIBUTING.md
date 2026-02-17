# Contributing

Спасибо за вклад в `llm-lab`! Это учебно-практический репозиторий с упором на инженерную дисциплину: типизация, проверяемость, reproducibility.

## Быстрый старт

Требования:
- Python 3.12+
- (опционально) Ollama для интеграционных тестов

Установка:
```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
```

Проверки:
```bash
make check
make makefile-smoke
```

## Ветвление и PR

Рекомендуемый процесс:
1) Создать ветку от `master`:
   ```bash
   git checkout -b feat/<short-name>
   ```
2) Коммиты небольшие и логичные.
3) Открыть PR и дождаться зелёного CI.

> В репозитории включена защита `master` с required checks.
> У владельца есть admin bypass — но по умолчанию лучше работать через PR.

## Интеграционные тесты (Ollama)

Если ты в WSL2 и Ollama запущен на Windows:
- Windows: `.\scripts\ollama_serve.ps1`
- WSL: можно подготовить env:
  ```bash
  source scripts/ollama_env.sh
  ```

Запуск:
```bash
make ollama-ping
make integration
```

## Стиль и качество

Обязательные “quality gates”:
- `ruff format` / `ruff check`
- `mypy`
- `pytest` unit

Локально всё это запускает:
```bash
make check
```

## Секреты

Никогда не коммить:
- API ключи, токены, пароли
- `.env` с реальными значениями
- логи/скриншоты, где видны секреты
