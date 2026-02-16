#!/usr/bin/env bash
set -euo pipefail

# Snapshot script for LLM project analysis.
# - Creates a cleaned copy of repo (no venv/cache/build artifacts)
# - Adds diagnostics report (git/env/tooling/make outputs)
# - Produces artifacts/snapshots/<name>_snapshot_<timestamp>.tar.gz + .sha256

# ---------- config ----------
EXCLUDES=(
  ".git/"
  ".venv/"
  "venv/"
  "__pycache__/"
  ".mypy_cache/"
  ".pytest_cache/"
  ".ruff_cache/"
  ".cache/"
  ".idea/"
  ".vscode/"
  "dist/"
  "build/"
  "*.egg-info/"
  ".tox/"
  ".coverage"
  "htmlcov/"
  "node_modules/"
  "artifacts/"   # avoid recursion
  ".DS_Store"
)

# Grep patterns for "quick secret smoke" (report only; doesn't block)
SECRET_PATTERNS=(
  "OPENAI_API_KEY"
  "api[_-]?key"
  "secret"
  "token"
  "password"
  "-----BEGIN .*PRIVATE KEY-----"
)

# ---------- helpers ----------
die() { echo "ERROR: $*" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

ts_utc() { date -u +"%Y%m%d_%H%M%SZ"; }

tmp_root=""

cleanup() {
  # avoid set -u trap crash
  if [ -n "${tmp_root:-}" ] && [ -d "${tmp_root:-}" ]; then
    rm -rf "$tmp_root"
  fi
}

project_name() {
  # best-effort: folder name
  basename "$(pwd)"
}

safe_run() {
  # usage: safe_run "title" cmd...
  local title="$1"; shift
  echo
  echo "== $title =="
  set +e
  "$@"
  local rc=$?
  set -e
  echo "rc=$rc"
  return 0
}

rsync_copy() {
  local src="$1"
  local dst="$2"

  have rsync || die "rsync not found. Install: sudo apt-get update && sudo apt-get install -y rsync"
  local args=(-a --delete)
  for e in "${EXCLUDES[@]}"; do
    args+=(--exclude "$e")
  done
  rsync "${args[@]}" "$src/" "$dst/"
}

make_report() {
  local repo_dir="$1"
  local out_dir="$2"

  mkdir -p "$out_dir/meta" "$out_dir/cmd"

  # Basic meta
  {
    echo "timestamp_utc=$(date -u -Is)"
    echo "cwd=$repo_dir"
    echo "uname=$(uname -a)"
    echo "user=$(id -un 2>/dev/null || true)"
    echo "uid=$(id -u 2>/dev/null || true)"
    echo "gid=$(id -g 2>/dev/null || true)"
    echo "shell=${SHELL:-}"
  } > "$out_dir/meta/system.txt"

  # Git info (if available)
  if have git && [ -d "$repo_dir/.git" ]; then
    (
      cd "$repo_dir"
      {
        echo "== git rev-parse HEAD =="
        git rev-parse HEAD || true
        echo
        echo "== git status =="
        git status --porcelain=v1 || true
        echo
        echo "== git branch =="
        git branch -vv || true
        echo
        echo "== git log -n 30 =="
        git log -n 30 --oneline --decorate || true
        echo
        echo "== git remote -v =="
        git remote -v || true
      } > "$out_dir/meta/git.txt"
    )
  else
    echo "git not available or .git missing" > "$out_dir/meta/git.txt"
  fi

  # Python/tooling versions
  {
    safe_run "python --version" python --version
    safe_run "python -m pip --version" python -m pip --version
    safe_run "python -m pip list" python -m pip list
    safe_run "ruff --version" python -m ruff --version
    safe_run "mypy --version" python -m mypy --version
    safe_run "pytest --version" python -m pytest --version
  } > "$out_dir/meta/python_tools.txt" 2>&1

  # Tree (limited)
  if have find; then
    (
      cd "$repo_dir"
      echo "== top-level files =="
      ls -la
      echo
      echo "== tree (depth<=4, excluding common noise) =="
      find . -maxdepth 4 \
        -not -path "./.git/*" \
        -not -path "./.venv/*" \
        -not -path "./artifacts/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/.mypy_cache/*" \
        -not -path "*/.pytest_cache/*" \
        -not -path "*/.ruff_cache/*" \
        -print
    ) > "$out_dir/meta/tree.txt" 2>&1
  fi

  # Secret smoke (non-blocking report)
  (
    cd "$repo_dir"
    echo "== secret smoke (report only) =="
    for pat in "${SECRET_PATTERNS[@]}"; do
      echo
      echo "-- pattern: $pat --"
      # ripgrep if available, else grep
      if have rg; then
        rg -n --hidden --no-ignore-vcs "$pat" . || true
      else
        grep -RIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=artifacts "$pat" . || true
      fi
    done
  ) > "$out_dir/meta/secret_smoke.txt" 2>&1

  # Make targets if present
  if [ -f "$repo_dir/Makefile" ]; then
    (
      cd "$repo_dir"
      safe_run "make -n lint (dry)" make -n lint
      safe_run "make -n typecheck (dry)" make -n typecheck
      safe_run "make -n mypy-smoke (dry)" make -n mypy-smoke
      safe_run "make -n test (dry)" make -n test

      safe_run "make lint" make lint
      safe_run "make typecheck" make typecheck
      safe_run "make mypy-smoke" make mypy-smoke
      safe_run "make test" make test
    ) > "$out_dir/cmd/make.txt" 2>&1
  else
    echo "No Makefile" > "$out_dir/cmd/make.txt"
  fi

  # Snapshot README with "how to run"
  cat > "$out_dir/README_SNAPSHOT.txt" <<'TXT'
This snapshot contains a cleaned copy of the repository + diagnostics reports.

Key files:
- repo/                 : sanitized repo copy (no .git, no venv, no caches)
- report/meta/*.txt     : system/git/python/tool versions, tree listing, secret smoke (report-only)
- report/cmd/make.txt   : outputs of make lint/typecheck/mypy-smoke/test (if Makefile exists)

To reproduce checks locally:
  python -m pip install -e ".[dev]"
  make format
  make lint
  make typecheck
  make mypy-smoke
  make test
TXT
}

pack() {
  local snap_name="$1"
  local tmp_root="$2"
  local out_dir="$3"

  mkdir -p "$out_dir"
  local out_abs
  out_abs="$(cd "$out_dir" && pwd -P)"
  local archive="$out_abs/${snap_name}.tar.gz"

  tar -C "$tmp_root" -czf "$archive" .
  sha256sum "$archive" > "${archive}.sha256"

  echo "OK"
  echo "Archive: $archive"
  echo "SHA256 : ${archive}.sha256"
}

main() {
  local root
  root="$(pwd)"

  # quick pre-flight
  have tar || die "tar not found"
  have sha256sum || die "sha256sum not found"

  local name
  name="$(project_name)"
  local stamp
  stamp="$(ts_utc)"
  local snap_name="${name}_snapshot_${stamp}"

  tmp_root="$(mktemp -d)"
  trap cleanup EXIT

  mkdir -p "$tmp_root/repo" "$tmp_root/report"

  echo "Copying repo (sanitized)..."
  rsync_copy "$root" "$tmp_root/repo"

  echo "Generating report..."
  make_report "$root" "$tmp_root/report"

  pack "$snap_name" "$tmp_root" "artifacts/snapshots"
}

main "$@"
