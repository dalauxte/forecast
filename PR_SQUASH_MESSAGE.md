feat: HTML report, live simulation, monthly limits, and documentation refresh

Summary
Adds a rich HTML report (replacing CSV), a local live‑simulation server, monthly usage limits per project, sequential budget burn logic, improved tables/units/diagrams, and updates all relevant documentation.

Key Changes
- HTML export is now the primary output; CSV export and --export option removed.
- New HTML report sections:
  - Übersicht (KPIs: ∑ Zugewiesen/Genutzt/Ungenutzt, Projektstatus)
  - Projekte – Zeitraum, Tage (d), Kapazität (h), Genutzt (h), Ungenutzt (h), Restbudget (h), Umsätze
  - Geplante Kapazitäten je Projekt (Monat, h)
  - Ø Zuteilung (h/d) und Ø nötig 100% (h/d)
  - Genutzte Stunden je Projekt (Monat) inkl. (Ø h/d) pro Monat
  - Diagramme: gestapelte Monatskapazität; je Projekt „genutzt vs. verfügbar am Monatsanfang“
  - Abschnittsbeschreibungen + Tooltips
- Limits je Projekt/Monat: `limits_by_month`; nicht genutzte Zuteilung verfällt monatsweise.
- Budgetverbrauch erfolgt sequentiell pro Monat; HTML zeigt Status (grün/gelb/rot).
- Live‑Server (`forecast.server`): YAML links, Report rechts; resizable Split (Drag 20–80%, Alt+←/→ ±1%, Reset 35%).

Docs
- Updated: requirements (HTML, live sim, limits), arc42 (modules `report`, `server`), manual (HTML export, live sim usage, units), sample config (limits example).
- Added release notes: `doc/reviews/2025-08-31_release_notes.md`.

Migration
- Replace CSV workflows with HTML: `PYTHONPATH=src python3 -m forecast.cli --config ... --outdir output`.
- Live preview: `PYTHONPATH=src python3 -m forecast.server` → open `http://127.0.0.1:8765`.

BREAKING CHANGE
- CSV export removed; CLI always writes HTML.

