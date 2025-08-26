.PHONY: smoke venv install deps init-config bundle-deps bundle-macos bundle-clean

smoke:
	@bash scripts/smoke.sh

venv:
	@test -d .venv || python3 -m venv .venv
	@echo "Run: source .venv/bin/activate"

install:
	@python -m pip install --upgrade pip
	@python -m pip install -e .

deps:
	@python -m pip install --upgrade pip
	@python -m pip install PyYAML holidays tabulate

init-config:
	@mkdir -p config
	@cp -n doc/manual/config.sample.yml config/config.yml || true
	@echo "Config initialisiert unter config/config.yml (falls nicht vorhanden)."

# --- Bundling (macOS) ---
# Baut ein einzelnes Executable in ./dist/forecast
# Voraussetzungen: Python-Umgebung (arm64) + Abhängigkeiten installiert

bundle-deps:
	@python -m pip install --upgrade pip
	@python -m pip install pyinstaller

bundle-macos:
	@pyinstaller --clean --onefile --name forecast --paths src scripts/entry_forecast.py
	@echo "\nFertig. Binary: dist/forecast"

bundle-clean:
	@rm -rf build dist forecast.spec
