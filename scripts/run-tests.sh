#!/usr/bin/env bash
set -euo pipefail

# Lightweight test runner that creates an isolated venv, installs pinned deps,
# and runs pytest for the repository. Designed for CI and local reproducibility.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv_ci"

echo "Using venv: $VENV_DIR"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt"
"$VENV_DIR/bin/python" -m pip install pytest==8.4.1

PYTHONPATH="$ROOT_DIR" "$VENV_DIR/bin/python" -m pytest "$@"
