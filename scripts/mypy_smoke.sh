#!/usr/bin/env bash
set -euo pipefail

FILE="tests/typecheck/reveal_types.py"

OUT="$(python -m mypy --show-error-codes --pretty "$FILE")"
echo "$OUT"

must_any() {
  local ok=1
  local pat
  for pat in "$@"; do
    if echo "$OUT" | grep -F "$pat" >/dev/null; then
      ok=0
      break
    fi
  done
  return "$ok"
}

# ensure overload visibility (module path may differ depending on where the class is defined)
must_any \
  'Revealed type is "llm_lab.clients.openai_client.OpenAIClient"' \
  'Revealed type is "llm_lab.clients.openai.OpenAIClient"'

must_any \
  'Revealed type is "llm_lab.clients.ollama_client.OllamaClient"' \
  'Revealed type is "llm_lab.clients.ollama.OllamaClient"'

# union order can vary, and module path can vary
must_any \
  'Revealed type is "llm_lab.clients.openai_client.OpenAIClient | llm_lab.clients.ollama_client.OllamaClient"' \
  'Revealed type is "llm_lab.clients.ollama_client.OllamaClient | llm_lab.clients.openai_client.OpenAIClient"' \
  'Revealed type is "llm_lab.clients.openai.OpenAIClient | llm_lab.clients.ollama.OllamaClient"' \
  'Revealed type is "llm_lab.clients.ollama.OllamaClient | llm_lab.clients.openai.OpenAIClient"'

echo "mypy-smoke: OK"
