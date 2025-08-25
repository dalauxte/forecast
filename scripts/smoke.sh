#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for the Forecast-Planer CLI
# Usage: bash scripts/smoke.sh [path/to/config.yml]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${1:-${ROOT_DIR}/doc/manual/config.sample.yml}"

echo "[smoke] Using config: ${CONFIG_PATH}"

# Choose a python executable (prefer python3)
PY="python3"
if ! command -v "$PY" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PY="python"
  else
    echo "[smoke] Python not found. Install Python 3.11+ and deps (PyYAML, holidays, tabulate)." >&2
    exit 1
  fi
fi

echo "[smoke] Python: $($PY -V)"

echo "[smoke] Importing package..."
PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH+:$PYTHONPATH}" $PY - <<'PY'
try:
    import forecast  # noqa: F401
    print('[smoke] import forecast: OK')
except Exception as e:
    print('[smoke] import forecast: FAILED', e)
    raise
PY

echo "[smoke] Running CLI (module)..."
set -o pipefail
if ! PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH+:$PYTHONPATH}" $PY -m forecast.cli --config "$CONFIG_PATH" --export csv | head -n 20; then
  echo "[smoke] CLI run failed" >&2
  exit 1
fi

if command -v forecast >/dev/null 2>&1; then
  echo "[smoke] Running CLI (entry point)..."
  if ! forecast --config "$CONFIG_PATH" --export csv | head -n 10; then
    echo "[smoke] Entry point run failed (this is optional)" >&2
  fi
else
  echo "[smoke] Entry point 'forecast' not on PATH (ok if not installed)."
fi

echo "[smoke] Done."
