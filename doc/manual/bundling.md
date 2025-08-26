# Standalone-Build (macOS, Apple Silicon)

Ziel: Eine einzelne ausführbare Datei `forecast`, die ohne venv/Repo nutzbar ist.

## Voraussetzungen
- macOS auf Apple Silicon (arm64)
- Python 3.11+ als ARM-Build (kein Rosetta/x86_64)
- Abhängigkeiten installiert (holidays, PyYAML, tabulate)
- PyInstaller installiert

## Schritte (mit venv)
1) Virtuelle Umgebung anlegen und aktivieren:
```
python3 -m venv .venv
source .venv/bin/activate
```

2) Pip aktualisieren und Projekt + PyInstaller installieren:
```
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pyinstaller
```

3) Build ausführen (Makefile oder Script):
```
make bundle-macos
# oder
./scripts/bundle_macos.sh
```

4) Ergebnis kopieren:
```
cp dist/forecast ~/bin/forecast   # oder in dein Arbeitsverzeichnis
```

## Nutzung
- Im Arbeitsverzeichnis mit deiner `config/config.yml`:
```
./forecast            # nutzt ./config/config.yml und schreibt CSV nach ./output/
./forecast --config myconfig.yml --outdir out
./forecast --output out/run.csv --as-of 2025-03-10
```
- Relative Pfade beziehen sich auf das aktuelle Arbeitsverzeichnis.

## Hinweise
- Architektur: Das Binary erbt die Architektur deines Python-Interpreters. Für Apple Silicon also mit arm64-Python bauen (kein Cross-Compile).
- Feiertage: Das Paket `holidays` wird in das Binary gebündelt, wenn es beim Build installiert ist.
- Clean: `make bundle-clean` bereinigt `build/`, `dist/` und `forecast.spec`.
