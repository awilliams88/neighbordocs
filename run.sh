#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

TARGET="${1:-app}"

setup() {
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --disable-pip-version-check -r requirements.txt
  python -m pip install --disable-pip-version-check gradio==6.16.0 ruff==0.15.16
}

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
    python -m ruff format --check .
    python -m ruff check .
    python -m compileall app.py src
    ;;
  format)
    setup
    python -m ruff format .
    ;;
  lint)
    setup
    python -m ruff check .
    ;;
  app|run|*)
    ensure_venv
    python app.py
    ;;
esac
