.PHONY: help format format-check lint typecheck mypy-smoke test check run makefile-smoke integration ollama-ping local-llm

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
	@echo "  ollama-ping   - ping Ollama from WSL (uses default gateway if OLLAMA_HOST is unset)"
	@echo "  local-llm     - run scripts/local_llm.py with ARGS='...' (uses default gateway if OLLAMA_HOST is unset)"
	@echo "  integration   - run integration tests (uses default gateway if OLLAMA_HOST is unset)"

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

makefile-smoke:
	@# fail if recipe lines start with spaces (common "missing separator" trap)
	@awk 'BEGIN{bad=0;in_recipe=0} \
in_recipe && $$0 ~ /^ +[^#[:space:]]/ {printf "Makefile: recipe must start with TAB (line %d): %s\n", NR, $$0 > "/dev/stderr"; bad=1} \
in_recipe && $$0 ~ /^[^[:space:]]/ {in_recipe=0} \
END{exit bad}' Makefile

check: makefile-smoke format-check lint typecheck mypy-smoke test

run:
	$(PY) -m llm_lab $(ARGS)

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

local-llm:
	@OLLAMA_HOST_ENV=$${OLLAMA_HOST:-}; \
	if [ -z "$$OLLAMA_HOST_ENV" ]; then \
		WIN_HOST=$$(ip -4 route show default | awk '{print $$3; exit}'); \
		OLLAMA_HOST_ENV="http://$$WIN_HOST:11434"; \
	fi; \
	case "$$OLLAMA_HOST_ENV" in \
		*://*) ;; \
		*) OLLAMA_HOST_ENV="http://$$OLLAMA_HOST_ENV" ;; \
	esac; \
	echo "OLLAMA_HOST=$$OLLAMA_HOST_ENV"; \
	OLLAMA_HOST=$$OLLAMA_HOST_ENV $(PY) scripts/local_llm.py $(ARGS)
