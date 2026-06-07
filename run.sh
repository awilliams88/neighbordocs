#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

TARGET="${1:-app}"
PYTHON=".venv/bin/python"

setup() {
  # Create or repair the local Python environment.
  if [ ! -x "$PYTHON" ]; then
    python3 -m venv .venv
  fi

  # Keep pip cache inside the repo to avoid global cache permission warnings.
  export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$ROOT_DIR/.pip-cache}"
  mkdir -p "$PIP_CACHE_DIR"

  # Update pip first so dependency installs use the latest resolver.
  "$PYTHON" -m pip install --upgrade pip --retries 0 --timeout 5 --quiet
  "$PYTHON" -m pip install --quiet -r requirements.txt
}

ensure_venv() {
  # Reuse setup when the local environment is missing or broken.
  if [ ! -x "$PYTHON" ]; then
    echo "Run ./run.sh setup first."
    exit 1
  fi
}

case "$TARGET" in
  setup)
    setup
    ;;
  verify)
    setup
    echo "=== Running Ruff Formatting Check ==="
    "$PYTHON" -m ruff format --check *.py
    echo "=== Running Ruff Linter ==="
    "$PYTHON" -m ruff check *.py
    echo "=== Running Pyright Type Checker ==="
    "$PYTHON" -m pyright *.py
    echo "=== Compiling Python Files ==="
    "$PYTHON" -m compileall *.py
    ;;
  format)
    setup
    "$PYTHON" -m ruff format *.py
    ;;
  lint)
    setup
    "$PYTHON" -m ruff check *.py
    ;;
  app|run|*)
    ensure_venv
    # Launch through app.py so Gradio receives theme and CSS.
    "$PYTHON" -m gradio app.py
    ;;
esac
