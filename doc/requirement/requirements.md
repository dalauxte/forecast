# Forecast-Planer – Anforderungen (Req42-kompakt)

- Status: v1.0 (finalisiert)
- Autor: Assistenz (Requirements Engineer)
- Datum: 2025-08-25
- Bezug: Fragenkatalog in `doc/requirement/questions.md` (inkl. Antworten + Nachfragen v2)

## Zweck und Zielbild
- Ziel: Unterstützung bei der Erstellung eines Stunden- und Umsatz-Forecasts zur Budgetausschöpfung je Projekt.
- Ergebnis: Kennzahlen, wie viele Stunden pro verbleibendem Arbeitstag durchschnittlich gearbeitet werden müssen, um 100%, 90% oder 80% des (Rest‑)Budgets auszuschöpfen; zusätzlich Umsatz-Projektion (EUR) basierend auf Stundensatz je Projekt.
- Fokus: CLI mit HTML‑Bericht und optionale Live‑Simulation im lokalen Browser; lokale Ausführung, Eingaben/Outputs per Datei möglich.

## Systemkontext
- Eingaben:
  - Projektdefinitionen (Name, Zeitraum, Restbudget in Stunden, Stundensatz EUR/h, Verteilungsgewichte je Monat).
  - Planungszeitraum (frei wählbar); kann Projekte schneiden (Teilüberdeckung) oder überlappen.
  - Persönlicher Arbeitskalender: Urlaub (Einzeltage), Krankheit (Wahrscheinlichkeitsmodell → erwartete Ausfalltage), variable Tageskapazität über Kalenderintervalle/Einzeltage.
  - Gesetzliche Feiertage Niedersachsen (automatisch; manuelle Overrides möglich).
  - Historische Arbeitszeiten: Für MVP außen vor; optional später nutzbar für Trend/Verteilung.
- Ausgaben:
  - Pro Projekt: erforderliche Ø-Stunden/Arbeitstag für 100/90/80% Ziel; Auslastung im Vergleich zur zugeordneten Kapazität; prognostizierter Umsatz.
  - Gesamt: aggregierte Kennzahlen (Summe Stunden/Tag, Umsatz) für den Planungszeitraum.
  - Export: HTML‑Bericht (mit Tabellen und Diagrammen); CLI zeigt eine ASCII‑Tabelle.
  - Live‑Simulation: YAML links, Report rechts, lokal im Browser.

## Stakeholder
- Primärnutzer: Berater (Einzelperson).
- Sekundär: Optional zukünftige Teammitglieder mit ähnlichem Bedarf.

## Begriffe / Definitionen
- Budget (Std): Freigegebene Stunden je Projekt und Zeitraum.
- Verbleibender Arbeitstag: Kalendertag im Projektzeitraum ab heute, exkl. Wochenenden, Feiertagen (NI), Urlaub, Krankheit (falls angegeben).
- Historische Stunden: Bereits geleistete Stunden innerhalb eines Zeitraums, die Budget reduzieren.

## Randbedingungen und Annahmen
- A1: Budget wird als Restbudget in Stunden eingegeben; kein automatischer Abzug historischer Stunden (Forecast-only).
- A2: Projekte haben eigene Start-/Enddaten; der Planungszeitraum kann darüber hinausgehen; Berechnung berücksichtigt die Schnittmenge.
- A3: Projekte dürfen überlappen; Verteilungsgewichte werden pro Monat angegeben und steuern die Kapazitätszuordnung.
- A4: Wochenenden arbeitsfrei; Standard-Arbeitswoche Mo–Fr.
- A5: Krankheit wird als erwartete Ausfalltage über eine Wahrscheinlichkeit pro Arbeitstag modelliert und wie Urlaub/Feiertag abgezogen (Erwartungswertverfahren, fraktional erlaubt).
- A6: Feiertage Niedersachsen automatisch; manuelle Korrekturen möglich.
- A7: Historische Daten bleiben im MVP ungenutzt; spätere Nutzung optional.
- A8: Rundung der Ergebniswerte auf 0,15 h.
- A9: Export als CSV im MVP.
- A10: Konfiguration als zentrale YAML-Datei (`config.yml`); Standardpfade definierbar und via CLI überschreibbar.
- A11: Zielumgebung: macOS, Python 3.11+, offline.
- A12: Währungs-/Zahlformat: Deutsch (de-DE), EUR.
 - A13: Fehlen Monatsgewichte, wird die Kapazität im jeweiligen Monat gleichmäßig auf alle aktiven Projekte verteilt (Gleichverteilung).
- A14: `limits_by_month` begrenzen die pro Monat für das Projekt nutzbaren Stunden; nicht genutzte Zuteilung verfällt (projektbezogen) für den Monat.
- A15: „Genutzt“ im Monat = min(Zuteilung, Monats‑Limit, Restbudget zu Monatsbeginn); Budget wird monatsweise sequentiell verbraucht.

## Qualitätsziele
- Nachvollziehbarkeit: Rechenweg transparent (z. B. Log/Audit-Abschnitt).
- Einfachheit: Einfache, lesbare Konfigurationsdateien; klare CLI.
- Robustheit: Sinnvolle Warnungen bei unmöglicher Zielerreichung (z. B. zu wenige Tage).
- Portabilität: Lokale Ausführung ohne externe Abhängigkeiten zur Laufzeit (außer Standardbibliothek oder lokal installierte Packages).

## Funktionale Anforderungen (FR)
- FR-01: Projekteingabe aus zentraler YAML laden (Name, Start, End, Restbudgetstunden, Stundensatz EUR/h, Gewichte je Monat).
- FR-02: Planungszeitraum als Eingabe; Schnittmenge je Projekt berücksichtigen.
- FR-03: Arbeitskalender anwenden: Wochenenden ausschließen; Feiertage NI abziehen; Urlaub (Einzeltage) abziehen; Krankheit als erwartete Ausfalltage abziehen; variable Tageskapazität über Intervalle/Einzeltage berücksichtigen.
- FR-04: Pro Projekt erforderliche Ø-Stunden/Arbeitstag für 100/90/80% Ziel berechnen; zusätzlich Auslastung vs. Kapazität und Umsatzprojektion ausgeben.
- FR-05: Verteilungsgewichte pro Monat anwenden, um Kapazität bei überlappenden Projekten zuzuordnen; Konflikte erkennen und als Warnung melden (Summe Gewichte pro Monat ≤ 100%).
- FR-06: Ergebnisse als CLI-Tabelle anzeigen; Export als CSV im DE-Format (Komma als Dezimaltrennzeichen optional konfigurierbar).
- FR-07: Manuelle Overrides für Feiertage/Arbeitstage; Rundung der Ergebniswerte auf 0,15 h.
- FR-08: Warnungen/Fehlermeldungen ausgeben (z. B. 0 verbleibende Tage/Kapazität, Ziel unerreichbar, inkonsistente Gewichte).
- FR-09 (Future): Historische Daten einlesen (Monats-CSV) zur Ableitung von Gewichten/Trend (deaktiviert im MVP).

## Abgrenzung / Out of Scope
- Keine grafische UI.
- Keine direkte API-Integration in Drittsysteme (Import/Export per Datei ist ausreichend).
- Keine automatische Umsatz-/EUR-Berechnung (nur falls später gewünscht).

## Datenmodell (YAML, zentral in `config.yml`)
- `settings`:
  - `state: NI`
  - `round_hours: 0.15`
  - `as_of: YYYY-MM-DD` (optional)
  - `planning_period: { start: YYYY-MM-DD, end: YYYY-MM-DD }`
  - `locale: de-DE`
- `capacity`:
  - `per_weekday`: `{ mon: 8, tue: 8, wed: 8, thu: 8, fri: 8 }` (optional; Default 8h für Mo–Fr)
  - `interval_overrides`: Liste von Blöcken `{ start: YYYY-MM-DD, end: YYYY-MM-DD, hours_per_day: 6 }` (Einzeltage: `start == end`)
- `calendar`:
  - `vacation_days`: Liste von Datumswerten `[YYYY-MM-DD, ...]`
  - `holiday_overrides`: `{ add: [YYYY-MM-DD, ...], remove: [YYYY-MM-DD, ...] }`
- `sickness`:
  - `prob_per_workday: 0.02` (Default – konfigurierbar; Erwartungswertverfahren)
- `projects`: Liste von Objekten:
  - `{ name: "Projekt A", start: YYYY-MM-DD, end: YYYY-MM-DD, rest_budget_hours: 120, rate_eur_per_h: 120.0,
       weights_by_month: { "2025-03": 60, "2025-04": 40 } }`
- (Future) `name_map`: Mapping Historie→Projektname für spätere Importe.

## Berechnungslogik (hochlevel)
1. Projekte laden; Planungszeitraum mit Projektzeiträumen schneiden (Schnittintervall pro Projekt).
2. Arbeitstage und Kapazität im Planungszeitraum ermitteln:
   - Wochenenden/Feiertage (NI) ausschließen; `holiday_overrides` anwenden.
   - Urlaub (Einzeltage) ausschließen.
   - Variable Kapazität: `per_weekday` und `interval_overrides` anwenden (Einzeltage via `start=end`).
   - Krankheit: Erwartete Ausfalltage = `prob_per_workday * anzahl_arbeitstage_vor_sick` (fraktional). Abzug vom Arbeitstage-Kontingent bzw. entsprechender Stundenkapazität.
3. Restbudgetstunden je Projekt = Eingabe `rest_budget_hours` (keine Historienverrechnung im MVP).
4. Zielstunden je Projekt = `{100%,90%,80%} * rest_budget_hours`.
5. Verfügbare Gesamtkapazität (Stunden) im Schnittintervall berechnen und gemäß `weights_by_month` monatsweise auf Projekte verteilen. Fehlen Monatsgewichte, erfolgt eine Gleichverteilung auf alle aktiven Projekte des Monats. Summe Gewichte pro Monat ≤ 100%.
6. Erforderliche Ø-Stunden/Tag je Projekt = `Zielstunden / verbleibende_Arbeitstage_im_Schnittintervall` (Ergebnis auf `round_hours` runden).
7. Auslastung je Ziel = `erforderlicher_Ø_pro_Tag / (zugeordnete_Ø_Kapazität_pro_Tag)`; Warnung bei > 1.0.
8. Umsatzprojektion je Ziel = `Zielstunden * rate_eur_per_h` (in EUR, de-DE formatiert).
9. Edge Cases: Bei 0 verbleibenden Arbeitstagen/0 Kapazität Projekt ignorieren und Hinweis ausgeben.

## Benutzerschnittstelle (CLI)
- Start: Ein Befehl `forecast calc --config config.yml [--export csv] [--output out.csv]`.
- Flags (Beispiele): `--as-of YYYY-MM-DD`, `--planning-start YYYY-MM-DD`, `--planning-end YYYY-MM-DD`, `--round 0.15`.
- Ausgabe (CLI-Tabelle, ASCII-Visuals optional):
  - Spalten: `Projekt | Zeitraum (Schnitt) | Verbl. Tage | Zugeordnete Kapazität (h) | Restbudget (h) | Øh/Tag (100/90/80) | Auslastung (100/90/80) | Umsatz (100/90/80)`.
  - Gesamtzeile: Summe Kapazität (h), Summe Umsatz (je Ziel).

## Nicht-funktionale Anforderungen (NFR)
- NFR-01: Ausführung < 2s bei typischen Datenmengen (≈ 3 Projekte, Planungszeitraum ≤ 3 Monate).
- NFR-02: Verständliche Fehlermeldungen und Validierung der Eingabedateien.
- NFR-03: Unit-Tests für Kernlogik (Kalender, Kapazität, Verteilung, Berechnung) und Beispiel-Dateien.
- NFR-04: Konfigurierbare Lokalisierung für Datums-/Zahlformat (Standard: DE), Währungsformat DE.
- NFR-05: Audit-Abschnitt mit Rechenschritten optional ausgeben.

## Risiken / Offene Punkte
 - O1: Typischer Krankheitswert (prob_per_workday) – initial 0.02 gesetzt, bitte bei Bedarf anpassen.
 - O2: Namensmapping für Historie (Future), Beispiel wird in der Bedienungsanleitung erläutert.

## Abnahmekriterien (Beispiele)
- AK-01: Gegeben ein Projekt mit Restbudget 100 h, 20 verbleibenden Arbeitstagen, Standard-Kapazität 8 h/Tag → 100%: 5,00 h/Tag; 90%: 4,50 h/Tag; 80%: 4,00 h/Tag (Rundung 0,15 h beibehalten).
- AK-02: Feiertage Niedersachsen innerhalb des Planungs-/Projekt-Schnitts sind keine Arbeitstage (manuelle Overrides berücksichtigt).
- AK-03: Variable Kapazität (per_weekday/Intervalle) beeinflusst die zugeordnete Ø-Kapazität und Auslastung korrekt.
- AK-04: Krankheit mit `prob_per_workday=0.02` reduziert die verfügbare Kapazität erwartungswertbasiert; Änderung des Werts ändert das Ergebnis nachvollziehbar.
- AK-05: CSV-Export enthält je Projekt Spalten für Øh/Tag (100/90/80), Auslastung (100/90/80) und Umsatz (100/90/80) im DE-Format; Gesamtzeile vorhanden.
- AK-06: Bei 0 verbleibenden Arbeitstagen oder 0 Kapazität wird das Projekt ignoriert und ein Hinweis ausgegeben.
 - AK-07: Wenn für einen Monat keine Gewichte definiert sind, verteilt das System die Kapazität gleichmäßig auf alle in diesem Monat aktiven Projekte.

## Nächste Schritte
1. Kurzanleitung und Beispiel-`config.yml` in `doc/manual` erstellen (inkl. Namensmapping-Beispiel für Future).
2. MVP-Implementierung planen (Parser, Kalender/Kapazität, Verteilung, Berechnung, Export, Tests).
3. Umsetzung starten und mit Beispielkonfiguration validieren.
