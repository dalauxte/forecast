# Projektstruktur – Plan (MVP)

Geplante Verzeichnisstruktur für die Implementierung. Ziel: klare Trennung von Parsing, Domain-Logik und Ausgabe.

```
.
├─ src/
│  └─ forecast/
│     ├─ __init__.py
│     ├─ cli.py               # CLI-Entry (argparse/typer), Orchestrierung
│     ├─ config.py            # YAML-Parsing, Validierung (dataclasses), Defaults
│     ├─ calendar.py          # Arbeitstage, Feiertage (NI), Urlaub, Overrides
│     ├─ capacity.py          # Kapazität pro Tag/Intervall, Krankheitsabzug
│     ├─ weights.py           # Monatsweise Verteilung, Gleichverteilung
│     ├─ compute.py           # Øh/Tag, Auslastung, Umsatz, Rundung
│     ├─ formatting.py        # DE-Formatierung, Tabellen, CSV-Export
│     └─ audit.py             # Optional: Rechenschritte sammeln/ausgeben
│
├─ tests/
│  ├─ test_calendar.py
│  ├─ test_capacity.py
│  ├─ test_weights.py
│  ├─ test_compute.py
│  └─ data/
│     └─ config_min.yml
│
├─ doc/
│  ├─ requirement/
│  ├─ architecture/
│  └─ manual/
│
├─ pyproject.toml             # Build/Deps (z. B. PyYAML, holidays, tabulate)
├─ README.md                  # Projekt-Übersicht, Installation, Beispiele
└─ LICENSE (optional)
```

## Abhängigkeiten (geplant)
- PyYAML: YAML-Parsing (`config.yml`).
- holidays (python-holidays): Feiertage Deutschland/Niedersachsen offline berechnen.
- tabulate (optional): CLI-Tabellen.

## Implementierungsreihenfolge (vorschlag)
1) `config.py` (Schema, Defaults, Validierung), Beispiel laden.
2) `calendar.py` (Arbeitstage + Feiertage NI + Urlaub + Overrides).
3) `capacity.py` (per_weekday/interval_overrides + Krankheit)
4) `weights.py` (Monatsweise, inkl. Gleichverteilung-Default)
5) `compute.py` (Kennzahlen, Rundung, Auslastung, Umsatz)
6) `formatting.py` (DE-Format, CLI-Tabelle, CSV)
7) `cli.py` (End-to-End zusammenführen)
8) Tests pro Modul, Beispiel-Configs nutzen.

## Konventionen
- Datumsformat ISO `YYYY-MM-DD` in allen Dateien.
- Prozentangaben als Ganzzahlen 0–100.
- Rundung auf `round_hours` via banker's rounding vermeiden; immer "round half up".
- Fehlermeldungen deutsch, prägnant; Hinweise bei unerfüllbaren Zielen.

