Forecast Planner – Kapazitäts- und Budgetplanung

Kurzbeschreibung
- Planungs-Tool, das verfügbare Kapazität (Arbeitstage × Stunden) monatsweise auf Projekte verteilt.
- Projekte haben Restbudget (h), Stundensätze, Gewichte pro Monat (`weights_by_month`) und optional Limits pro Monat (`limits_by_month`).
- Ausgabe als Tabelle im Terminal und als ausführlicher HTML-Bericht.
- Live-Simulation im Browser: YAML links bearbeiten, Report rechts live sehen.

Voraussetzungen
- Python 3.10+ (lokal installierter `python3`)
- Optional: Paket `tabulate` für schönere CLI-Tabellen (Fallback vorhanden)

Schnellstart
- CLI (HTML erzeugen):
  - `PYTHONPATH=src python3 -m forecast.cli --config config/config.yml --outdir output`
- Live-Server (Browser-Vorschau):
  - `PYTHONPATH=src python3 -m forecast.server`
  - Im Browser öffnen: `http://127.0.0.1:8765`
  - Optional Host/Port: `FORECAST_HOST=0.0.0.0 FORECAST_PORT=8080 PYTHONPATH=src python3 -m forecast.server`

Konfiguration (YAML)

settings:
  state: NI                 # Bundesland für Feiertage (NI = Niedersachsen)
  planning_period:          # Planungszeitraum
    start: 2025-10-01
    end: 2025-12-31
  round_hours: 0.15         # Rundung in Stunden (z. B. 0.15 = 9 Minuten)
  locale: de-DE

capacity:
  per_weekday: { mon: 8, tue: 8, wed: 8, thu: 8, fri: 8 }  # Basiskapazität in h pro Arbeitstag
  interval_overrides:                                       # Optional: Intervalle mit abweichenden Stunden pro Tag
    - { start: 2025-10-09, end: 2025-10-10, hours_per_day: 2 }

calendar:
  vacation_days: [2025-10-20]          # Urlaubstage oder Bereiche {start,end}
  holiday_overrides: { add: [], remove: [] }  # Zusätzliche/zu entfernende Feiertage

sickness:
  prob_per_workday: 0.02    # Erwartete Ausfallwahrscheinlichkeit/Tag (reduziert Kapazität proportional)

projects:
  - name: Projekt A
    start: 2025-10-01
    end: 2025-12-31
    rest_budget_hours: 120
    rate_eur_per_h: 100
    weights_by_month:            # Steuerung der Verteilung der Monatskapazität
      "2025-10": 100
      "2025-11": 100
      "2025-12": 30
    limits_by_month:             # Optional: harte Obergrenze der nutzbaren Stunden je Monat
      "2025-12": 20

Wirkung der Gewichte (`weights_by_month`)
- Pro Monat wird die vorhandene Monatskapazität auf aktive Projekte gemäß Gewichten verteilt.
- Keine Angabe für irgendein aktives Projekt im Monat (Summe = 0): Gleichverteilung 100%/N über alle aktiven Projekte.
- Mindestens ein Projekt hat ein Gewicht (> 0): Projekte ohne Eintrag bekommen 0% in diesem Monat.
- Summe der Gewichte über Projekte < 100%: Restkapazität des Monats bleibt ungenutzt.
- Summe > 100%: Fehler (Abbruch mit Meldung).

Monats-Limits (`limits_by_month`)
- Optional pro Projekt/Monat: maximale nutzbare Stunden.
- Effektiv genutzte Stunden je Monat: `min(zugeteilt, limit, verbleibendes Budget)`.
- Nicht genutzte Kapazität = `zugeteilt - genutzt` (verfällt für dieses Projekt und diesen Monat).

HTML-Bericht (Sektionen)
- Übersicht: Planungszeitraum, Anzahl Urlaub-/Feiertage, Gesamtkapazität, Anzahl Projekte.
- Urlaube und Abwesenheiten: Liste der Urlaubstage/-zeiträume.
- Projekte – Zeitraum, Tage, Kapazität: pro Projekt Gesamtkapazität, ØKap/Tag, Umsätze, Hinweise (z. B. “100% Ziel > Kap/Tag”).
- Geplante Kapazitäten je Projekt: zugeteilte Stunden je Monat (nur Zuteilung, noch ohne Limits/Budget).
- Verteilung Stunden pro Projekt (Øh/Arbeitstag im Monat): `zugeteilte Stunden / Arbeitstage (Projekt, Monat)`.
- Erforderliche Øh/Arbeitstag je Monat (für 100%): Budget proportional zur Zuteilung auf Monate verteilt, dann durch Arbeitstage im Monat geteilt.
- Genutzte Stunden je Projekt (Monat): tatsächlich genutzte Stunden mit Limits/Budget berücksichtigt.
- Ungenutzte Kapazität je Projekt (Monat): Differenz aus Zuteilung und Nutzung.
- Budgetverbrauch pro Projekt (h): monatsweise Budgetnutzung mit Statusfarbe
  - Grün: Budget exakt im letzten aktiven Monat verbraucht
  - Gelb: Restbudget verbleibt am Ende
  - Rot: Budget vor dem letzten aktiven Monat erschöpft

CLI-Optionen (Auszug)
- `--config`: Pfad zur YAML-Datei (Default: `config/config.yml` falls vorhanden)
- `--outdir`: Ausgabeverzeichnis (Default: `output`)
- `--as-of`: Stichtag (YYYY-MM-DD), verschiebt Planungsstart nach vorne
- `--planning-start`, `--planning-end`: überschreiben den Planungszeitraum
- `--round`: Rundung in Stunden (z. B. 0.15)

Typische Fragen
- “Warum ist die zugewiesene Kapazität größer als mein Budget?”
  - Das Tool verteilt Verfügbarkeit; das Restbudget limitiert nicht die Zuteilung, sondern fließt in Bedarf/Util/Umsatz ein. Die echte Nutzung (Budgetverbrauch) siehst du in den Tabellen “Genutzte Stunden …” und “Budgetverbrauch …”.
- “Wie stelle ich sicher, dass das Budget nicht überschritten wird?”
  - Nutze `limits_by_month` oder reduziere Kapazität (z. B. `interval_overrides`, `sickness`) oder passe `weights_by_month` an.

Live-Simulation (Browser)
- Start: `PYTHONPATH=src python3 -m forecast.server`
- Linke Seite: YAML editieren (vorbefüllt mit `config/config.yml`, sofern vorhanden)
- Rechte Seite: Bericht wird bei Änderungen automatisch neu gerendert (oder per Button)

Beispielberichte
- Siehe `doc/example/example report.md` für Strukturideen eines Berichts.
