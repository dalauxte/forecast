---
Created: 31.08.2025
Tags: #example #report
---
# Beispiel‑Bericht (Struktur)

Dieser Markdown dient als Vorlage, wie der HTML‑Report aufgebaut ist. Die HTML‑Ausgabe enthält zusätzlich Tooltips und Abschnittsbeschreibungen.

## Hilfe (Definitionen)

- Zuteilung (Kapazität): Verfügbarkeit, die monatsweise per weights_by_month auf Projekte verteilt wird.
- Genutzt: Tatsächlich verwendete Stunden je Monat: min(Zuteilung, Monats‑Limit, verbleibendes Budget).
- Ungenutzt: Zuteilung − Genutzt (verfällt für das Projekt und den Monat).
- Ø/Tag (Zuteilung): Zuteilung im Monat / Arbeitstage (Projekt, Monat).
- Erforderlicher Ø/Tag: Budget proportional zur Zuteilung auf Monate verteilt, dann ÷ Arbeitstage (Planungsziel für 100%).
- Status (Budget): Grün = Budget exakt am Projektende verbraucht; Gelb = Restbudget bleibt; Rot = Budget vor Projektende erschöpft.

## Übersicht

| Name               | Wert |
|--------------------|------|
| Planungszeitraum   | …    |
| ∑ Urlaubstage      | …    |
| ∑ Feiertage        | …    |
| ∑ Kapazität (h)    | …    |
| ∑ Projekte         | …    |
| ∑ Zugewiesen (h)   | …    |
| ∑ Genutzt (h)      | …    |
| ∑ Ungenutzt (h)    | …    |
| Projekte (grün)    | …    |
| Projekte (gelb)    | …    |
| Projekte (rot)     | …    |

## Urlaube und Abwesenheiten

Liste aller Urlaubs‑ und Abwesenheitstage/Zeiträume im Planungszeitraum.

## Projekte – Zeitraum, Tage, Kapazität

| Projekt | Zeitraum     | Tage | Kapazität (h) | Genutzt (h) | Ungenutzt (h) | Restbudget (h) | Umsatz 100% | Umsatz 90% | Umsatz 80% | Hinweise |
|---------|--------------|-----:|--------------:|------------:|--------------:|---------------:|------------:|-----------:|-----------:|----------|
| …       | 2025‑MM–MM   |  …  |           …   |         …   |           …   |            …   |         …   |        …   |        …   | …        |

## Geplante Kapazitäten je Projekt

Zuteilung nach Monaten auf Basis der Gewichte (ohne Limits/Budget).

| Projekt | 2025‑09 | 2025‑10 | … |
|---------|--------:|--------:|---|
| …       |     …   |     …   | … |

## Verteilung Stunden pro Projekt (Øh/Arbeitstag im Monat)

Ø/Tag (Zuteilung/Arbeitstage) je Monat.

| Projekt | 2025‑09 | 2025‑10 | … |
|---------|--------:|--------:|---|
| …       |     …   |     …   | … |

## Erforderliche Øh/Arbeitstag je Monat (für 100%)

Budget proportional zur Zuteilung auf Monate verteilt, dann ÷ Arbeitstage des Projekts im Monat.

Formeln:
- A_total = Σ assigned(p, m)
- B_m = rest_budget_hours × (assigned(p, m) / A_total)
- need_avg_m = B_m / D_m (D_m = Arbeitstage im Monat)

| Projekt | 2025‑09 | 2025‑10 | … |
|---------|--------:|--------:|---|
| …       |     …   |     …   | … |

## Genutzte Stunden je Projekt (Monat)

Genutzt = min(Zuteilung, Monats‑Limit, verbleibendes Budget), sequentiell über Monate.

| Projekt | 2025‑09 | 2025‑10 | … |
|---------|--------:|--------:|---|
| …       |     …   |     …   | … |

## Ungenutzte Kapazität je Projekt (Monat)

Ungenutzt = Zuteilung − Genutzt (nicht negativ).

| Projekt | 2025‑09 | 2025‑10 | … |
|---------|--------:|--------:|---|
| …       |     …   |     …   | … |

## Budgetverbrauch pro Projekt (h)

Monatlicher Budget‑Burn inkl. Status (Ampel):
- Grün: Budget exakt im letzten aktiven Monat verbraucht
- Gelb: Restbudget verbleibt am Ende
- Rot: Budget vor dem letzten aktiven Monat erschöpft

| Projekt | 2025‑09 | 2025‑10 | … | Restbudget (h) | Status |
|---------|--------:|--------:|---|---------------:|--------|
| …       |     …   |     …   | … |            …   |  …     |
