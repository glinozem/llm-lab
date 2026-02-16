.PHONY: lint test run

lint:
	ruff check .
	mypy .

test:
	pytest -q

run:
	python -m llm_lab.cli --prompt "What is FastAPI? (1-2 sentences)"
