from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
from typing import Dict, List, Tuple
import sys

from .config import load_config, Config
from .calendar import intersection, workdays_in_period, month_key
from .capacity import compute_capacity_by_date, aggregate_capacity_by_month
from .weights import assign_capacity_by_project_month
from .compute import compute_results
from .formatting import render_table, export_csv_semicolon


def _collect_interval_overrides(capacity_cfg) -> List[Tuple[date, date, float]]:
    res = []
    for o in capacity_cfg.interval_overrides:
        res.append((o.start, o.end, o.hours_per_day))
    return res


def run(config_path: str, output_path: str | None = None, export: str | None = None,
        as_of: str | None = None, planning_start: str | None = None, planning_end: str | None = None,
        round_hours: float | None = None) -> int:
    cfg: Config = load_config(config_path)

    if round_hours is not None:
        cfg.settings.round_hours = float(round_hours)

    if planning_start or planning_end:
        start = cfg.settings.planning_period.start if not planning_start else date.fromisoformat(planning_start)
        end = cfg.settings.planning_period.end if not planning_end else date.fromisoformat(planning_end)
        cfg.settings.planning_period.start = start
        cfg.settings.planning_period.end = end

    planning_period = (cfg.settings.planning_period.start, cfg.settings.planning_period.end)

    # Workdays for overall planning period
    all_workdays = workdays_in_period(
        planning_period,
        cfg.settings.state,
        cfg.calendar.holiday_overrides_add,
        cfg.calendar.holiday_overrides_remove,
        cfg.calendar.vacation_days,
    )

    # Capacity per date (after sickness reduction)
    capacity_by_date = compute_capacity_by_date(
        workdays=all_workdays,
        per_weekday=cfg.capacity.per_weekday,
        interval_overrides=_collect_interval_overrides(cfg.capacity),
        sick_prob_per_workday=cfg.sickness.prob_per_workday,
    )
    capacity_by_month = aggregate_capacity_by_month(capacity_by_date)

    # Determine active projects per month within planning cut
    projects: List[dict] = []
    projects_by_month: Dict[str, List[str]] = {}
    explicit_weights: Dict[str, Dict[str, float]] = {}
    workdays_by_project: Dict[str, List[date]] = {}

    for p in cfg.projects:
        cut = intersection(planning_period, (p.start, p.end))
        if cut is None:
            continue
        projects.append({
            "name": p.name,
            "start": cut[0],
            "end": cut[1],
            "rest_budget_hours": p.rest_budget_hours,
            "rate_eur_per_h": p.rate_eur_per_h,
            "weights_by_month": dict(p.weights_by_month),
        })
        # Active months
        months = set()
        d = cut[0]
        while d <= cut[1]:
            mk = month_key(d)
            months.add(mk)
            # next month first day
            if d.month == 12:
                d = d.replace(year=d.year + 1, month=1, day=1)
            else:
                d = d.replace(month=d.month + 1, day=1)
        for m in months:
            projects_by_month.setdefault(m, []).append(p.name)
        explicit_weights[p.name] = dict(p.weights_by_month)

        # Workdays per project (within its cut)
        wdays = workdays_in_period(cut, cfg.settings.state, cfg.calendar.holiday_overrides_add, cfg.calendar.holiday_overrides_remove, cfg.calendar.vacation_days)
        workdays_by_project[p.name] = wdays

    assigned = assign_capacity_by_project_month(capacity_by_month, projects_by_month, explicit_weights)

    results = compute_results(
        planning_period=planning_period,
        projects=projects,
        workdays_by_project=workdays_by_project,
        assigned_capacity_by_project_month=assigned,
        round_hours=cfg.settings.round_hours,
    )

    # Format output rows
    rows = []
    for r in results:
        rows.append({
            "Projekt": r.name,
            "Zeitraum": f"{r.period_start}–{r.period_end}",
            "Tage": r.workdays,
            "Øh/Tag 100%": r.required_per_day_100,
            "Øh/Tag 90%": r.required_per_day_90,
            "Øh/Tag 80%": r.required_per_day_80,
            "ØKap/Tag": r.assigned_avg_per_day,
            "Util 100%": r.utilization_100,
            "Umsatz 100%": r.revenue_100,
            "Umsatz 90%": r.revenue_90,
            "Umsatz 80%": r.revenue_80,
        })

    # Print table
    print(render_table(rows))

    # Export
    if export and export.lower() == "csv":
        content = export_csv_semicolon(rows)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print("\nCSV:\n" + content)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Forecast-Planer (CLI)")
    parser.add_argument("--config", required=True, help="Pfad zur config.yml")
    parser.add_argument("--output", help="Pfad für Exportdatei")
    parser.add_argument("--export", choices=["csv"], help="Exportformat")
    parser.add_argument("--as-of", dest="as_of", help="Stichtag (YYYY-MM-DD)")
    parser.add_argument("--planning-start", help="Start des Planungszeitraums (YYYY-MM-DD)")
    parser.add_argument("--planning-end", help="Ende des Planungszeitraums (YYYY-MM-DD)")
    parser.add_argument("--round", dest="round_hours", type=float, help="Rundung (z. B. 0.15)")
    args = parser.parse_args(argv)
    try:
        return run(
            config_path=args.config,
            output_path=args.output,
            export=args.export,
            as_of=args.as_of,
            planning_start=args.planning_start,
            planning_end=args.planning_end,
            round_hours=args.round_hours,
        )
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

