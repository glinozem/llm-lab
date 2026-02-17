#!/usr/bin/env bash
set -euo pipefail

# Must be sourced to affect the current shell.
# If executed directly, exports will not persist outside this process.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "WARN: scripts/ollama_env.sh is meant to be sourced (not executed)." >&2
  echo "      Run: source ${BASH_SOURCE[0]}" >&2
  echo >&2
fi

# WSL helper: derive Ollama endpoint from the default gateway (Windows host) if not set.
# Usage:
#   source scripts/ollama_env.sh

if [[ -z "${OLLAMA_HOST:-}" ]]; then
  WIN_HOST="$(ip -4 route show default 2>/dev/null | awk '{print $3; exit}')"
  if [[ -n "${WIN_HOST}" ]]; then
    export OLLAMA_HOST="http://${WIN_HOST}:11434"
  else
    echo "WARN: could not detect default gateway via 'ip route'; leaving OLLAMA_HOST unset" >&2
  fi
fi

# Normalize if user exported OLLAMA_HOST without a scheme.
if [[ -n "${OLLAMA_HOST:-}" && "${OLLAMA_HOST}" != *"://"* ]]; then
  export OLLAMA_HOST="http://${OLLAMA_HOST}"
fi

if [[ -z "${OLLAMA_MODEL:-}" ]]; then
  export OLLAMA_MODEL="mistral"
fi

echo "Exported:"
echo "  OLLAMA_HOST=${OLLAMA_HOST:-<unset>}"
echo "  OLLAMA_MODEL=${OLLAMA_MODEL:-<unset>}"

echo
cat <<'EOF'
Tips:
  make ollama-ping
  make local-llm ARGS='chat --prompt "Hi!" --stream'
  python scripts/local_llm.py chat --prompt "Hi!" --stream
EOF
