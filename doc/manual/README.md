# Forecast-Planer – Kurzanleitung (MVP)

Diese Anleitung beschreibt die zentrale Konfiguration per `config.yml` und das erwartete Verhalten des MVP gemäß Anforderungen v1.1.

## Inhalte
- Konfiguration: zentrale YAML `config.yml`
- Felderklärung und Beispiele
- Regeln zur Verteilung (Monatsgewichte, Gleichverteilung)
- Hinweise zu Feiertagen/Urlaub/Krankheit und Kapazität
- Export und Ausgabe

## Konfiguration (`config.yml`)
Standard-Suchpfad: `config/config.yml` (dann ist `--config` optional). Beispiel siehe `doc/manual/config.sample.yml`.
Kernbereiche:

- `settings`:
  - `state`: Bundesland für Feiertage (z. B. `NI`).
  - `planning_period`: Zeitraum des Forecasts (`start`, `end`).
  - `round_hours`: Rundung der Ergebniswerte (z. B. `0.15`).
  - `locale`: Formatierung (Standard `de-DE`).
- `capacity`:
  - `per_weekday`: Standardstunden pro Wochentag (Mo–Fr), optional.
  - `interval_overrides`: Abweichende Kapazität in Intervallen oder Einzeltagen (`start == end`).
- `calendar`:
  - `vacation_days`: Liste einzelner Urlaubstage (YYYY-MM-DD).
  - `holiday_overrides`: Feiertage hinzufügen/entfernen.
- `sickness`:
  - `prob_per_workday`: Wahrscheinlichkeit pro Arbeitstag (Default 0.02). Erwartungswertverfahren.
- `projects` (Liste):
  - `name`, `start`, `end`, `rest_budget_hours`, `rate_eur_per_h`.
  - `weights_by_month`: pro Monat Prozentanteile (0–100). Fehlt ein Monat → Gleichverteilung auf aktive Projekte.

## Verteilung und Kapazität
- Jeden Monat wird die verfügbare Gesamtkapazität berechnet (Wochenenden/Feiertage/Urlaub abgezogen; Kapazitäts-Overrides angewandt; Krankheit als erwartete Ausfalltage berücksichtigt).
- Anschließend wird monatsweise verteilt:
  - Wenn `weights_by_month` angegeben sind: Zuweisung gemäß Prozenten; Summe ≤ 100%.
  - Wenn keine Gewichte angegeben sind: Gleichverteilung auf alle aktiven Projekte in diesem Monat.

## Ausgabe und Export
- CLI-Tabellenansicht mit:
  - `Projekt | Zeitraum (Schnitt) | Verbl. Tage | Zugeordnete Kapazität (h) | Restbudget (h) | Øh/Tag (100/90/80) | Auslastung (100/90/80) | Umsatz (100/90/80)`
- CSV-Export: Standardmäßig wird bei jedem Lauf eine Datei in `output/` gespeichert.
  - Dateiname: `forecast_YYYYMMDD_HHMMSS.csv`
  - Zielordner anpassbar mit `--outdir`, oder exakte Datei mit `--output`.

## Schnellstart (empfohlen)
- `cp doc/manual/config.sample.yml config/config.yml`
- `make install` (oder `make deps`)
- `forecast --outdir output` (oder ohne Flags, da Default-Pfade genutzt werden)

## Historie
- Im MVP werden historische Daten nicht verwendet. Perspektivisch: Monats-CSV zur Ableitung von Gewichten/Trends und Namensmapping.

## Namensmapping (Future)
- Falls historische Daten aus Fremdsystemen abweichen, kann ein Mapping vorgesehen werden:
```
name_map:
  "Proj A (Timesheet)": "Projekt A"
```
(Dies ist für das MVP noch nicht erforderlich.)

## Hinweise
- Einzeltage in `interval_overrides` durch `start == end` definieren.
- Rundung `round_hours` wirkt auf Øh/Tag-Ausgaben.
- Krankheit wird erwartungswertbasiert fraktional abgezogen (z. B. 2% von Arbeitstagen im Monat).
