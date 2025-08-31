# Release Notes — 2025-08-31

## Highlights
- HTML report replaces CSV export (cleaner, richer visuals and context).
- Live simulation server (local): YAML left, HTML report right; resizable split, keyboard adjust, reset.
- Per-project monthly limits (`limits_by_month`) supported; sequential budget burn logic.
- New report content:
  - Portfolio KPIs (assigned/used/unused sums, project status counts).
  - Enhanced project summary (used/unused/restbudget, revenues) with units.
  - Monthly tables with units and clearer headers.
  - “Genutzt” per month now shows average per workday in parentheses (h and h/d).
  - Diagrams: stacked monthly capacity usage; per-project per-month used vs available (rest_budget at month start).
  - Section descriptions and header tooltips.
- Simulation UI refinements: drag handle (20–80%), Alt+←/→ (±1%), Reset (35%).

## Breaking Changes
- CSV export and `--export` option removed; CLI always writes HTML (`--outdir` or `--output`).

## Documentation
- Requirements, Architecture (arc42), and Manual updated to reflect HTML export, live simulation, limits, and report sections.
- Sample config shows `limits_by_month` usage.

## Internal
- Introduced `report` module (build full HTML) and simplified `formatting`.
- `server` module for live simulation (no external deps).

## Upgrade Notes
- Replace any CSV-based workflows with HTML export.
- Use `PYTHONPATH=src python3 -m forecast.cli --config ... --outdir output` to generate HTML.
- Live preview: `PYTHONPATH=src python3 -m forecast.server` and open `http://127.0.0.1:8765`.

