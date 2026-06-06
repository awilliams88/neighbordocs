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
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
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
    python verify_code.py
    ;;
  format)
    setup
    python -m ruff format .
    ;;
  test)
    setup
    pytest
    ;;
  app|run|*)
    ensure_venv
    python app.py
    ;;
esac
