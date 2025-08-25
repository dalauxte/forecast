.PHONY: smoke venv install

smoke:
	@bash scripts/smoke.sh

venv:
	@test -d .venv || python3 -m venv .venv
	@echo "Run: source .venv/bin/activate"

install:
	@python -m pip install --upgrade pip
	@python -m pip install -e .
