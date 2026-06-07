#!/usr/bin/env bash
set -euo pipefail

# Get project root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"



TARGET="${1:-app}"
PYTHON=".venv/bin/python"

setup() {
  # Create or repair the local Python environment
  if [ ! -x "$PYTHON" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
  fi



  echo "Upgrading pip..."
  "$PYTHON" -m pip install --upgrade pip --retries 0 --timeout 5
  
  echo "Installing dependencies from requirements.txt..."
  "$PYTHON" -m pip install -r requirements.txt
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
    if [ ! -x "$PYTHON" ]; then
      setup
    fi
    echo "=== Running Ruff Formatter (Auto-fixing) ==="
    "$PYTHON" -m ruff format *.py
    echo "=== Running Ruff Linter (Auto-fixing) ==="
    "$PYTHON" -m ruff check --fix *.py
    echo "=== Running Pyright Type Checker ==="
    "$PYTHON" -m pyright *.py
    echo "=== Compiling Python Files ==="
    "$PYTHON" -m compileall *.py
    ;;
  app|run|*)
    ensure_venv
    # Launch through app.py so Gradio receives theme and CSS.
    "$PYTHON" -m gradio app.py
    ;;
esac
