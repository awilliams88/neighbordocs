#!/usr/bin/env bash
# Script to setup, format, lint, typecheck, and run the Gradio app
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

TARGET="${1:-app}"

# Helper function to create virtualenv and install dependencies
setup() {
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --disable-pip-version-check -r requirements.txt
}

# Helper function to ensure virtualenv exists
ensure_venv() {
  if [ ! -d ".venv" ]; then
    echo "Run ./run.sh setup first."
    exit 1
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
}

case "$TARGET" in
  setup)
    setup
    ;;
  verify)
    setup
    echo "=== Running Ruff Formatting Check ==="
    python -m ruff format --check *.py
    echo "=== Running Ruff Linter ==="
    python -m ruff check *.py
    echo "=== Running Pyright Type Checker ==="
    python -m pyright *.py
    echo "=== Compiling Python Files ==="
    python -m compileall *.py
    ;;
  format)
    setup
    python -m ruff format *.py
    ;;
  lint)
    setup
    python -m ruff check *.py
    ;;
  app|run|*)
    ensure_venv
    python app.py
    ;;
esac
