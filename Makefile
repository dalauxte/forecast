.PHONY: smoke venv install deps init-config

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
