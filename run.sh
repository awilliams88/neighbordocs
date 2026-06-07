#!/usr/bin/env bash
# run.sh — local dev utility for InnerSpace.
# Usage: ./run.sh [setup|verify|app]
set -euo pipefail

# Set ROOT_DIR
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Set PYTHON and TARGET
PYTHON=".venv/bin/python"
TARGET="${1:-app}"

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

# Create the virtual environment and install dependencies.
setup() {
  if [ ! -x "$PYTHON" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
  fi
  echo "Installing dependencies..."
  "$PYTHON" -m pip install --quiet --upgrade pip
  "$PYTHON" -m pip install --quiet -r requirements.txt
  echo "Setup complete."
}

# Abort early if the virtual environment is missing.
ensure_venv() {
  if [ ! -x "$PYTHON" ]; then
    echo "Error: run ./run.sh setup first."
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
case "$TARGET" in
  setup)
    setup
    ;;

  verify)
    # Auto-install if the environment is missing.
    [ ! -x "$PYTHON" ] && setup
    echo "→ format"
    "$PYTHON" -m ruff format app.py env/*.py core/*.py ui/*.py modal/*.py
    echo "→ lint"
    "$PYTHON" -m ruff check --fix app.py env/*.py core/*.py ui/*.py modal/*.py
    echo "→ types"
    "$PYTHON" -m pyright app.py env/*.py core/*.py ui/*.py modal/*.py
    echo "→ compile"
    "$PYTHON" -m compileall -q app.py env/ core/ ui/ modal/
    echo "✓ All checks passed."
    ;;

  app | run | *)
    ensure_venv
    # Launch via gradio so the custom theme and CSS are applied correctly.
    "$PYTHON" -m gradio app.py
    ;;
esac

# ---------------------------------------------------------------------------
# Cleanup — remove Python and linter cache dirs on exit.
# ---------------------------------------------------------------------------
cleanup() {
  find "$ROOT_DIR" \
    -not -path "$ROOT_DIR/.git/*" \
    -not -path "$ROOT_DIR/.venv/*" \
    \( -type d -name "__pycache__" -o -type d -name ".ruff_cache" \) \
    -exec rm -rf {} + 2>/dev/null || true
}
trap cleanup EXIT
