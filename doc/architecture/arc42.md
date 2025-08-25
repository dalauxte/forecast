# Forecast-Planer – Architektur (Arc42 Kurzfassung)

## 1. Einleitung & Ziele
- Zweck: CLI-Tool zur Stunden- und Umsatzprognose je Projekt, inkl. Kapazitäts- und Kalendermodell (Feiertage NI, Urlaub, Krankheit) und Verteilungslogik.
- Qualitätsziele: Einfachheit, Nachvollziehbarkeit (Audit), Performance (kurze Laufzeit), Portabilität (lokal, offline), korrekte DE-Formatierung.

## 2. Randbedingungen
- Umgebung: Python 3.11+, macOS, offline.
- Daten: Zentrale YAML-Konfiguration; CSV-Export.
- Domäne: Feiertage Niedersachsen; Arbeitswoche Mo–Fr.

## 3. Kontextabgrenzung
- Nutzer liefert Eingaben (YAML) → Tool berechnet und exportiert CSV.
- Keine externe Systemintegration (optional später: Historie-Import).

## 4. Lösungsstrategie
- Trennung „Konfiguration laden“ → „Kalender/Kapazität“ → „Verteilungslogik“ → „Berechnung“ → „Formatierung/Export“.
- Erwartungswertverfahren für Krankheit (prob_per_workday) zur robusten, einfachen Modellierung.
- Monatsweise Verteilungsgewichte, Default: Gleichverteilung bei fehlenden Angaben.

## 5. Bausteinsicht (wesentliche Module)
- `cli`: CLI-Parsing, Orchestrierung, Fehlerbehandlung.
- `config`: Schema-Validierung, YAML-Parsing, Defaults.
- `calendar`: Arbeitstage, Feiertage (NI), Urlaub, Overrides.
- `capacity`: Tageskapazität (per_weekday + interval_overrides), Krankheitsabzug.
- `weights`: Monatsweise Verteilung (explizit oder Gleichverteilung), Schnittmenge Projekt/Planungszeitraum.
- `compute`: Kennzahlen (Øh/Tag, Auslastung, Umsatz) je Ziel (100/90/80), Rundung.
- `formatting`: DE-Zahlen/Währung, Tabellenanzeige (ASCII), CSV-Export.
- `audit` (optional): nachvollziehbare Zwischengrößen/Begründungen.

## 6. Laufzeitsicht (Hauptfluss)
1) `cli` lädt YAML mit `config` und validiert.
2) `calendar` ermittelt Arbeitstage pro Monat im Planungsschnitt (Wochenenden/Feiertage/Urlaub/Overrides).
3) `capacity` berechnet Kapazität (Stunden) und zieht Krankheits-Erwartungswert ab.
4) `weights` verteilt monatsweise Kapazität auf Projekte (Gewichte oder Gleichverteilung).
5) `compute` berechnet pro Projekt Øh/Tag, Auslastung, Umsatz für 100/90/80.
6) `formatting` zeigt Tabelle an und exportiert CSV.

## 7. Verteilungssicht / Deployment
- Single-binary Skriptausführung (Python CLI) lokal. Keine externen Services.

## 8. Querschnittliche Konzepte
- Zeit/Datumsbehandlung in UTC-lokal konsequent (naiv lokal, DE-Format nur für Ausgabe).
- Konfig-Defaults: Rundung 0.15 h, `prob_per_workday` 0.02, Gleichverteilung bei fehlenden Gewichten.
- Validierung: Frühzeitige Prüfung von Datumsformaten, Gewichts-Summen, negativen Budgets.
- Fehler-/Warning-Policy: Deutliche Hinweise bei unerfüllbaren Zielen/0-Tagen.

## 9. Entscheidungen (ADR-Kurznotizen)
- Python + YAML: Lesbar, verbreitet (PyYAML). Alternative TOML verworfen (User-Präferenz).
- Krankheit via Wahrscheinlichkeit statt fixer Tage: Flexibler, skaliert mit Zeitraum.
- Gewichte pro Monat: Transparente Planung; Default-Gleichverteilung bei Lücken.

## 10. Qualitätsanforderungen
- Performanz: < 2s für ~3 Projekte, ≤ 3 Monate.
- Zuverlässigkeit: Tests für Kalender, Kapazität, Verteilung, Berechnung.
- Benutzbarkeit: Verständliche Fehlermeldungen, klare CLI-Flags.

## 11. Risiken & Schulden
- Abhängigkeit Feiertage: Nutzung einer Bibliothek (z. B. `holidays`) oder eigene Logik; Offline-Fähigkeit sicherstellen.
- YAML-Parsing erfordert Third-Party (PyYAML) – Packaging/Installation beachten.
- Erweiterung Historie/Mapping noch offen, später integrieren.

## 12. Glossar
- Restbudget (h): Verbleibende Stunden im Projekt.
- Planungsschnitt: Schnittmenge Planungszeitraum ∩ Projektzeitraum.
- Gewichte: Prozentuale Kapazitätsverteilung je Monat.
