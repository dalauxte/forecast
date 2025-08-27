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
  - `vacation_days`: Liste von Urlauben – Einzeltage (YYYY-MM-DD) oder Intervalle als Mapping `{ start, end }`.
    Beispiel:
    
    ```yaml
    calendar:
      vacation_days:
        - 2025-03-28              # Einzeltag
        - { start: 2025-04-15, end: 2025-04-19 }  # Zeitraum (inkl. Start/Ende)
    ```
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
  - `Projekt | Zeitraum (Schnitt) | Verbl. Tage | Kapazität (h) | ØKap/Tag | Øh/Tag (100/90/80) | Util (100/90/80) | Umsatz (100/90/80)`
  - Erläuterung „Util …“ (Auslastung):
    - Bedeutung: Verhältnis der benötigten Ø‑Stunden/Tag zum zugeordneten Ø‑Kapazitätswert/Tag.
    - Formel: `Util 100% = Øh/Tag 100% ÷ ØKap/Tag` (analog für 90%/80%).
    - Interpretation: `1.00` = genau passend, `< 1.00` = Reserve, `> 1.00` = Kapazität reicht nicht.
    - Anzeige: dimensionsloser Faktor (kein Prozent). Bei fehlender ØKap/Tag wird `-` gezeigt.
    - Beispiel: Wenn `ØKap/Tag = 6,00` und `Øh/Tag 100% = 5,00`, dann `Util 100% = 5,00 / 6,00 = 0,83`. Für 90% wären es `4,50 / 6,00 = 0,75`.
- CSV-Export: Standardmäßig wird bei jedem Lauf eine Datei in `output/` gespeichert.
  - Dateiname: `forecast_YYYYMMDD_HHMMSS.csv`
  - Zielordner anpassbar mit `--outdir`, oder exakte Datei mit `--output`.
- Gesamtzeile: Am Tabellenende werden Summen für „Kapazität (h)“ und „Umsatz (100/90/80)“ ausgewiesen.
- Hinweise: Projekte ohne verbleibende Arbeitstage werden genannt; zusätzlich Warnung, wenn Ziel (100/90/80) mehr als zugeordnete Kapazität/Tag erfordert.

## Schnellstart (empfohlen)
- `cp doc/manual/config.sample.yml config/config.yml`
- `make install` (oder `make deps`)
- `forecast --outdir output` (oder ohne Flags, da Default-Pfade genutzt werden)

## Locale/Formatierung
- Derzeit fest auf DE (Dezimal-Komma, EUR); `settings.locale` wird im MVP nicht ausgewertet.

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
