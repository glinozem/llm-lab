.PHONY: help format format-check lint typecheck mypy-smoke test check run

PY ?= python

help:
	@echo "Targets:"
	@echo "  format        - ruff format ."
	@echo "  format-check  - ruff format --check ."
	@echo "  lint          - ruff check ."
	@echo "  typecheck     - mypy (src/llm_lab)"
	@echo "  mypy-smoke    - mypy reveal_type smoke check"
	@echo "  test          - pytest"
	@echo "  check         - format-check + lint + typecheck + mypy-smoke + test"
	@echo "  run           - run CLI with ARGS='...'"

format:
	$(PY) -m ruff format .

format-check:
	$(PY) -m ruff format --check .

lint:
	$(PY) -m ruff check .

typecheck:
	$(PY) -m mypy

mypy-smoke:
	bash scripts/mypy_smoke.sh

test:
	$(PY) -m pytest -q -m "not integration"

check: format-check lint typecheck mypy-smoke test

run:
	$(PY) -m llm_lab.cli $(ARGS)

integration:
	@WIN_HOST=$$(ip -4 route show default | awk '{print $$3; exit}'); \
	OLLAMA_HOST=$${OLLAMA_HOST:-http://$$WIN_HOST:11434}; \
	echo "OLLAMA_HOST=$$OLLAMA_HOST"; \
	OLLAMA_HOST=$$OLLAMA_HOST $(PY) -m pytest -q -rs -m integration

ollama-ping:
	@WIN_HOST=$$(ip -4 route show default | awk '{print $$3; exit}'); \
	OLLAMA_HOST=$${OLLAMA_HOST:-http://$$WIN_HOST:11434}; \
	echo "OLLAMA_HOST=$$OLLAMA_HOST"; \
	llm-lab --provider ollama --ollama-host "$$OLLAMA_HOST" --model mistral:latest --prompt "ping"
