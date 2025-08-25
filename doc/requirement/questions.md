# Forecast-Planer – Fragenkatalog zur Präzisierung

Bitte beantworte die Punkte stichpunktartig. „(Zu bestätigen)“ heißt: kurze Bestätigung reicht. Wo Optionen angeboten sind, bitte wählen oder ergänzen.

## Kontext & Ziele
1. Zielbild: Nur Stunden-Forecast (Budgetausschöpfung in Stunden) oder zusätzlich Umsatz-Prognose in EUR? Falls EUR: pro Projekt Stundensatz oder Mischkalkulation?
2. Integration: Muss das Ergebnis in ein bestehendes Tool importiert werden (CSV/Excel/API), oder reicht Copy&Paste/Dateiablage?
3. Planungszeitraum: Forecast-Horizont – laufender Monat, Quartal, oder frei je Projekt?

Zu 1) Sowohl Stunden-Forecast, als auch Umsatzforecast. Dazu kann ich als Input den Stundensatz pro Projekt eintragen.
Zu 2) Es wäre gut das Ergebnis als CSV oder Excel-Datei nutzen zu können. Es muss aber keinem spezifischen Format entsprechen, die Überführung in das Firmentool muss ich manuell vornehmen.
Zu 3) Ich möchte den Planungszeitraum gerne frei vergeben können. Wichtig ist, er muss damit umgehen können das ein Projekt ggf. im Planungszeitraum endet oder über diesen Hinausgeht.

## Projekte & Budgets
4. Budget-Einheit: Stunden (Standard) / Tage / EUR? (Zu bestätigen)
5. Zeitraum: Ein zusammenhängender Zeitraum pro Projekt oder mehrere Phasen/Milestones pro Projekt?
6. Überlappung: Dürfen Projekte überlappen? Falls ja, zunächst nur Kennzahlen je Projekt oder auch eine Verteilungsempfehlung über Projekte?
7. Änderungen: Dürfen Budgets/Zeiträume rückwirkend geändert werden? Versionierung der Stände gewünscht?

Zu 4) Korrekt.
Zu 5) Ein Zusammenhänger Zeitraum über alle Projekte hinweg. Dieser kann kleiner oder größer als die Laufzeit einzelner Projekte sein.
Zu 6) Ja sie dürfen sich überlappen. Ich würde daher gerne prozentual angeben können, wie die Verteilung sein soll.
Zu 7) Nein, ich würde dann eine neue Baseline (etwa mit dem Restbudget und den Reststunden) einstellen und einen neuen Durchlauf machen. Es gibt immer nur um Forecast, niemals darum zurückzublicken.

## Arbeitskalender
8. Arbeitswoche: Standard Mo–Fr und Wochenenden arbeitsfrei? (Zu bestätigen) Standard-Stunden/Tag?
9. Feiertage: Bundesland Niedersachsen korrekt? Automatisch abziehen + manuelle Overrides möglich? (Zu bestätigen)
10. Urlaub: Eingabe als einzelne Tage und/oder Intervalle? Resturlaubs-Tracking pro Jahr gewünscht?
11. Krankheit: Fester Puffer (Anzahl Tage im Zeitraum) oder Wahrscheinlichkeitsmodell? Wie behandeln (voll wie Urlaub oder teilweise)?
12. Kapazität: Variable Kapazität pro Wochentag/Woche (z. B. Teilzeit, fixe Meetingtage) erforderlich?

Zu 8) Korrekt.
Zu 9) Korrekt.
Zu 10) Eingabe der Urlaubstage als einzelne Tage (ggf. in einer Datei), kein Tracking des Resturlaubs notwendig.
Zu 11) Wahrscheinlichkeitsmodell und als vollständige ausgefallene Tage berücksichtigen.
Zu 12) Ja, variable Kapazität erforderlich.

## Eingabedateien
13. Formatpräferenz für Konfiguration: YAML / TOML / JSON? (Vorschlag: YAML)
14. Struktur: Eine zentrale Datei (Projekte, Kalender, Settings) oder mehrere Dateien (`projects.yml`, `calendar.yml`, `settings.yml`)?
15. Pfade: Standardpfade im Repo/Home + CLI-Flags zum Überschreiben? (Zu bestätigen)
16. Versionierung: Sollen Eingaben über Git versioniert werden? Branch/PR-Workflow relevant?

## Historische Daten
17. Quelle/Format: CSV/Excel? Beispielspalten: `date, project, hours` – passt das?
18. Nutzung: Nur Information oder auch zur Hochrechnung (z. B. gleitender Durchschnitt realistischer Tagesleistung)?
19. Granularität: Tages- oder Monatswerte? Müssen wir aggregieren?
20. Mapping: Muss ein Namensmapping zwischen Quelle und Projektliste unterstützt werden?


Zu 17: Ja.
Zu 18: Auch zur Hochrechnung.
Zu 19: Monatswerte
Zu 20: Frage bitte erläutern. Aber ich denke schon.

## Berechnung & Logik
21. Zielmetrik: „Ø Stunden pro verbleibendem Arbeitstag“ für 100/90/80% – korrekt? Weitere Zielstufen nötig?
22. Verbleibende Tage: Basis = Kalendertage im Projektzeitraum minus Wochenenden, Feiertage (NI), Urlaub, Krankheit – korrekt?
23. Rundung: Gewünschte Rundung (z. B. 0.25 h)?
24. Edge Cases: Verhalten bei 0 verbleibenden Tagen, negativem Restbudget, oder wenn Budget schon ausgeschöpft?
25. Historie: Historische Stunden im Projektzeitraum automatisch abziehen – korrekt? Was, wenn Historie Tage außerhalb des Projektzeitraums enthält?

Zu 21) Korrekt und nein.
Zu 22) Korrekt.
Zu 23) Korrekt. Rundung auf 0.15 h
Zu 24) Dann wird das Projekt nicht mehr berücksichtigt. Hinweisausgabe.
Zu 25) Nein. Nur Forecast auf Basis der zuletzt eingegebenen Tage. Es ist die Aufgabe des Nutzers nur noch verfügbare Tage einzugeben.

## CLI & Output
26. Bedienung: Ein Befehl `forecast calc` mit Pfaden/Flags ausreichend? Brauchen wir Subcommands (`import`, `plan`, `report`)?
27. Formate: CLI-Tabelle ausreichend? Export als CSV/Markdown/JSON gewünscht? Bevorzugtes Default-Format?
28. Visuals: ASCII-Tabellen/kleine Balken hilfreich oder weglassen?
29. Sprache/Format: Deutsch als Standard; DE-Datum-/Zahlformat? (Zu bestätigen)

Zu 26) Hängt von der Entwicklung ab. Starten mit einem Befehlt.
Zu 27) Import als CSV gewünscht.
Zu 28) Hilfreich
Zu 29) Bestätigt.

## Nicht-funktionales
30. Performance: Typische Projektanzahl und Zeitraumgröße der Historie?
31. Nachvollziehbarkeit: Soll ein „Audit“-Abschnitt mit Rechenschritten im Output enthalten sein?
32. Tests: Beispielfiles + Unit-Tests gewünscht?
33. Portabilität: Zielumgebung macOS, Python 3.11+? Offline ausführbar ohne Netz? (Zu bestätigen)

Zu 30) 3 Projekte, 3 bis 12 Monate
Zu 31) Ja.
Zu 32) Ja.
Zu 33) Ja.

## Zukunft/Erweiterungen
34. Kapazitätsplanung pro Woche/Monat (variable Ziele) gewünscht?
35. Szenarien/What-ifs (z. B. „2 Tage krank im März“ vs. „0 Tage“)?
36. Umsatzsicht (Stundensätze, Projektkosten, Marge) später integrieren?

Zu 34) Nein.
Zu 35) Ja.
Zu 36) Ja.

---

## Nachfragen v2 (zur Finalisierung v0.2)
1. Konfiguration: Bevorzugst du YAML als Format für die Konfig (Settings, Kalender, Projekte)? Falls nein: TOML/JSON?
2. Dateistruktur: Eine zentrale Datei `config.yml` (mit `settings`, `calendar`, `projects`) oder getrennt (`projects.yml`, `calendar.yml`, `settings.yml`)?
3. Standardpfade: Sollen wir Standardpfade im Repo/Home definieren (z. B. `./config.yml`, `./history.csv`) und via CLI-Flags überschreibbar machen?
4. Mapping Historie→Projekte: Ist ein explizites Mapping gewünscht (z. B. `name_map: { "Proj A (Timesheet)": "Projekt A" }`) für abweichende Bezeichnungen?
5. Verteilungsgewichte: Sind die Prozentanteile pro Projekt über den gesamten Planungszeitraum konstant, oder möchtest du Zeitfenster (z. B. pro Monat/Woche) mit unterschiedlichen Gewichten angeben?
6. Variable Kapazität: Wie willst du sie definieren?
   - a) Pro Wochentag feste Stunden (z. B. Mo 8, Di 6, ...)
   - b) Kalenderintervalle mit abweichender Tageskapazität (z. B. 01–15.03 → 6h/Tag)
7. Krankheit (Wahrscheinlichkeitsmodell): Bitte präzisieren:
   - a) Erwartete Krankentage pro Monat (z. B. 0.5 Tage/Monat)
   - b) Wahrscheinlichkeit pro Arbeitstag (z. B. 2%)
   - c) Andere Definition? (Wir rechnen als erwartete Ausfalltage und ziehen sie vom Arbeitstage-Kontingent ab.)
8. Historische Daten für Hochrechnung: Wie genau sollen sie einfließen?
   - a) Gesamtkapazität: gleitender Durchschnitt Stunden/Arbeitstag (alle Projekte)
   - b) Projektverteilung: Gewichte aus den letzten N Monaten ableiten (falls keine manuelle Gewichtung angegeben)
   - c) Fenstergröße N (z. B. 3 Monate)
9. Export: Reicht CSV als Export? Sollen wir zusätzlich Excel (XLSX) anbieten? Falls ja, optional (Flag) oder standardmäßig?
10. Umsatzsicht: Stundensatz pro Projekt fix hinterlegen (EUR/h). Sollen Währungen/Kommata formatiert (DE) ausgegeben werden?

Zu 1) YAML ist super. Bitte erstelle mir eine Beispiel und auch eine Anleitung im Ordner /doc/manual
Zu 2) Eine zentrale Datei. Trennung möglicherweise als späteres Feature.
Zu 3) Ja.
Zu 4) Bitte anhand eines Beispiels erläutern, ich habe die Frage nicht verstanden.
Zu 5) Getrennt nach Monanten angeben.
Zu 6) Kalenderintervalle. Wobei es auch mglich sein muss Einzeltage anzugeben.
Zu 7) Wahrscheinlichkeit. Recherchiere was für Wissensarbeiter eine typische Anzahl an AUsfällen ist. Dieses Prozentsatz nehmen wir als start.
Zu 8) Wir lassen die Historischen Daten zunächst außen vor.
Zu 9) CSV reicht als Start aus.
Zu 10) Ja.