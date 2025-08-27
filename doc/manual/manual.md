# Manual – Forecast-Planer (CLI)

Dieses Dokument erklärt die Nutzung des CLI-Tools, akzeptierte Parameter und typische Workflows.

## Zweck
- Errechnet pro Projekt die benötigten Ø-Stunden/Tag (100/90/80%), vergleicht mit zugeordneter Kapazität und projiziert den Umsatz.
- Berücksichtigt Wochenenden, Feiertage (Niedersachsen), Urlaub, variable Kapazitäten und erwartete Krankheit (Wahrscheinlichkeit pro Arbeitstag).

## Voraussetzungen
- Python 3.11+ (getestet mit 3.13)
- Empfohlene Nutzung in einer virtuellen Umgebung (venv)

## Installation (empfohlen)
- Virtuelle Umgebung und Installation:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `make install`
- Alternativ nur Abhängigkeiten (ohne Editable-Install):
  - `make deps`
- Smoke-Test:
  - `make smoke`

## Erstkonfiguration
- Beispiel übernehmen und anpassen:
  - `make init-config` (kopiert `doc/manual/config.sample.yml` nach `config/config.yml` falls nicht vorhanden)
- Danach `config/config.yml` mit eigenen Projekten/Zeiträumen/Kapazitäten befüllen.

## Aufruf
- Standard (nutzt `config/config.yml`, schreibt CSV in `output/`):
  - `forecast`
- Mit explizitem Ausgabeverzeichnis:
  - `forecast --outdir output/runs`
- Mit expliziter Zieldatei (überschreibt `--outdir`):
  - `forecast --output output/mein_run.csv`
- Alternative Config-Datei:
  - `forecast --config path/to/config.yml`
- Planungszeitraum überschreiben (statt Werten aus der Config):
  - `forecast --planning-start 2025-03-01 --planning-end 2025-04-30`
- Stichtag (Arbeitstage vor Stichtag werden nicht berücksichtigt):
  - `forecast --as-of 2025-03-10`
- Rundung (Standard 0.15 h):
  - `forecast --round 0.25`

## Parameter
- `--config PATH`:
  - Pfad zur YAML-Konfiguration. Optional: Wenn nicht gesetzt, wird `config/config.yml` verwendet.
- `--outdir DIR`:
  - Zielordner für CSV. Default: `output`. Datei wird automatisch mit Zeitstempel `forecast_YYYYMMDD_HHMMSS.csv` benannt.
- `--output FILE`:
  - Exakter Dateipfad für CSV. Überschreibt `--outdir`.
- `--as-of YYYY-MM-DD`:
  - Stichtag. Alle Tage vor diesem Datum werden ignoriert (Start des Planungszeitraums wird entsprechend nach vorn verschoben).
- `--planning-start YYYY-MM-DD`, `--planning-end YYYY-MM-DD`:
  - Überschreiben den Planungszeitraum aus der Konfiguration (Start/Ende).
- `--round FLOAT`:
  - Rundung der Øh/Tag-Werte auf Vielfache (z. B. `0.25` für 15-Minuten-Takt). Default: `0.15`.

## Output
- CLI-Tabelle inkl.:
  - `Projekt | Zeitraum (Schnitt) | Verbl. Tage | Kapazität (h) | ØKap/Tag | Øh/Tag (100/90/80) | Util (100/90/80) | Umsatz (100/90/80)`
  - Util (Auslastung):
    - Bedeutung: Verhältnis der benötigten Ø‑Stunden/Tag zum zugeordneten Ø‑Kapazitätswert/Tag.
    - Formel: `Util 100% = Øh/Tag 100% ÷ ØKap/Tag` (entsprechend 90%/80%).
    - Interpretation: `1,00` = exakt passend, `< 1,00` = Reserve, `> 1,00` = Kapazität reicht nicht.
    - Anzeige: dimensionslos; bei fehlender ØKap/Tag wird `-` ausgegeben.
    - Beispiel:
      - Gegeben: `ØKap/Tag = 6,00`, `Øh/Tag 100% = 5,00`, `Øh/Tag 90% = 4,50`, `Øh/Tag 80% = 4,00`.
      - Dann: `Util 100% = 5,00 / 6,00 = 0,83`, `Util 90% = 4,50 / 6,00 = 0,75`, `Util 80% = 4,00 / 6,00 = 0,67`.
- CSV-Export:
  - Wird immer geschrieben.
  - Standard: `output/forecast_YYYYMMDD_HHMMSS.csv` (anpassbar per `--outdir`/`--output`).
  - Enthält eine „GESAMT“-Zeile mit Summen für „Kapazität (h)“ und „Umsatz (100/90/80)“.
- Hinweise/Warnungen:
  - Projekte ohne verbleibende Arbeitstage werden gelistet (ignoriert).
  - Warnung, wenn Ziel (100/90/80) mehr Øh/Tag erfordert als zugeordnete ØKap/Tag.

## Datenformat (Konfiguration)
- Siehe `doc/manual/config.sample.yml` und `doc/manual/README.md`.
- Kernelemente: `settings`, `capacity` (Wochentage/Intervalle), `calendar` (Urlaub/Overrides), `sickness` (Wahrscheinlichkeit), `projects` (Restbudget, Stundensatz, Monatsgewichte).

## Beispiele
- Einfacher Lauf mit Default-Konfig/Output:
  - `forecast`
- Individuelle Datei im Standard-Output-Ordner:
  - `forecast --output output/forecast_meinteam.csv`
- Lauf mit Stichtag und engerem Zeitraum:
  - `forecast --as-of 2025-03-10 --planning-start 2025-03-01 --planning-end 2025-04-30`
- Runde auf 0.25 h:
  - `forecast --round 0.25`

## Fehlerbehebung
- „No module named 'yaml'“: Abhängigkeiten fehlen → `make install` oder `make deps`.
- Feiertage nicht berücksichtigt: `python-holidays` installieren (`make deps`) oder prüfen, ob `state: NI` gesetzt ist.
- „Keine --config angegeben“: Entweder `--config` nutzen oder `config/config.yml` anlegen (`make init-config`).
- Ergebnis leer: Prüfen, ob Projekte im Planungszeitraum aktiv sind und nicht vollständig durch Urlaub/Feiertage/Stichtag ausgeschlossen werden.

## Makefile-Targets
- `make venv`: venv anlegen (einmalig), danach aktivieren: `source .venv/bin/activate`
- `make install`: Paket + Abhängigkeiten installieren (empfohlen)
- `make deps`: nur Abhängigkeiten installieren
- `make smoke`: schneller Testlauf mit Beispielkonfiguration
- `make init-config`: legt `config/config.yml` an (falls nicht vorhanden)
 - `make bundle-deps`: installiert PyInstaller
 - `make bundle-macos`: baut ein Einzel-Binary `dist/forecast` (macOS)
 - `make bundle-clean`: bereinigt Build-Artefakte

## Exit-Codes
- `0` Erfolg, `1` Fehler (Validierung, Pfade, fehlende Abhängigkeiten etc.).

## Hinweise
- Zahlen-/Währungsformat ist im MVP fest auf DE (Dezimal-Komma, EUR). Eine Umschaltung via `settings.locale` ist noch nicht aktiv.
- Die Feiertagsberechnung erfolgt lokal/offline über `python-holidays`.

## Standalone Binary (macOS)
Siehe `doc/manual/bundling.md` für Details. Kurzfassung:
1) `python -m pip install -e . && python -m pip install pyinstaller`
2) `make bundle-macos`
3) `cp dist/forecast <dein Arbeitsverzeichnis>` und dort ausführen.
