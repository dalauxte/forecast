#!/usr/bin/env bash
set -euo pipefail

# Build standalone executable for macOS (Apple Silicon) using PyInstaller
# Usage: ./scripts/bundle_macos.sh

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller nicht gefunden. Installiere mit: python -m pip install pyinstaller" >&2
  exit 1
fi

pyinstaller --clean --onefile --name forecast --paths src scripts/entry_forecast.py

echo
echo "Fertig. Binary unter: dist/forecast"
