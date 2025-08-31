from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from .config import Config
from .calendar import intersection, workdays_in_period, month_key, niedersachsen_holidays
from .capacity import compute_capacity_by_date, aggregate_capacity_by_month
from .weights import assign_capacity_by_project_month
from .compute import compute_results
from .formatting import export_html_page, format_number_de, format_currency_eur


def create_html_report(cfg: Config) -> str:
    planning_period = (cfg.settings.planning_period.start, cfg.settings.planning_period.end)

    all_workdays = workdays_in_period(
        planning_period,
        cfg.settings.state,
        cfg.calendar.holiday_overrides_add,
        cfg.calendar.holiday_overrides_remove,
        cfg.calendar.vacation_days,
    )

    capacity_by_date = compute_capacity_by_date(
        workdays=all_workdays,
        per_weekday=cfg.capacity.per_weekday,
        interval_overrides=[(o.start, o.end, o.hours_per_day) for o in cfg.capacity.interval_overrides],
        sick_prob_per_workday=cfg.sickness.prob_per_workday,
    )
    capacity_by_month = aggregate_capacity_by_month(capacity_by_date)

    projects: List[dict] = []
    projects_by_month: Dict[str, List[str]] = {}
    explicit_weights: Dict[str, Dict[str, float]] = {}
    explicit_limits: Dict[str, Dict[str, float]] = {}
    workdays_by_project: Dict[str, List[date]] = {}

    for p in cfg.projects:
        cut = intersection(planning_period, (p.start, p.end))
        if cut is None:
            continue
        wdays = workdays_in_period(
            cut,
            cfg.settings.state,
            cfg.calendar.holiday_overrides_add,
            cfg.calendar.holiday_overrides_remove,
            cfg.calendar.vacation_days,
        )
        if not wdays:
            continue

        projects.append(
            {
                "name": p.name,
                "start": cut[0],
                "end": cut[1],
                "rest_budget_hours": p.rest_budget_hours,
                "rate_eur_per_h": p.rate_eur_per_h,
                "weights_by_month": dict(p.weights_by_month),
            }
        )
        # months active
        months = set()
        d = cut[0]
        while d <= cut[1]:
            months.add(month_key(d))
            if d.month == 12:
                d = d.replace(year=d.year + 1, month=1, day=1)
            else:
                d = d.replace(month=d.month + 1, day=1)
        for m in months:
            projects_by_month.setdefault(m, []).append(p.name)
        explicit_weights[p.name] = dict(p.weights_by_month)
        explicit_limits[p.name] = dict(getattr(p, "limits_by_month", {}) or {})
        workdays_by_project[p.name] = wdays

    assigned = assign_capacity_by_project_month(capacity_by_month, projects_by_month, explicit_weights)

    results = compute_results(
        planning_period=planning_period,
        projects=projects,
        workdays_by_project=workdays_by_project,
        assigned_capacity_by_project_month=assigned,
        round_hours=cfg.settings.round_hours,
    )

    # Collect all months
    all_months: List[str] = []
    months_set = set()
    for days in workdays_by_project.values():
        for d in days:
            mk = month_key(d)
            if mk not in months_set:
                months_set.add(mk)
                all_months.append(mk)
    all_months.sort()

    # Overview
    years = set(range(planning_period[0].year, planning_period[1].year + 1))
    hols = set()
    if cfg.settings.state.upper() == "NI":
        hols = niedersachsen_holidays(years)
    hols.update(cfg.calendar.holiday_overrides_add)
    hols.difference_update(cfg.calendar.holiday_overrides_remove)
    hols_in_period = [d for d in hols if planning_period[0] <= d <= planning_period[1] and d.weekday() < 5]
    vac_in_period = [d for d in cfg.calendar.vacation_days if planning_period[0] <= d <= planning_period[1]]
    sum_capacity = sum(capacity_by_date.values())
    overview_items = [
        ("Planungszeitraum", f"{planning_period[0]} – {planning_period[1]}"),
        ("∑ Urlaubstage", str(len(vac_in_period))),
        ("∑ Feiertage", str(len(hols_in_period))),
        ("∑ Kapazität (h)", format_number_de(sum_capacity, 2)),
        ("∑ Projekte", str(len(results))),
    ]

    # Project summary
    proj_summary_headers = [
        "Projekt",
        "Zeitraum",
        "Tage",
        "Kapazität (h)",
        "Umsatz 100%",
        "Umsatz 90%",
        "Umsatz 80%",
        "Hinweise",
    ]
    proj_summary_rows: List[List[str]] = []
    for r in results:
        notes: List[str] = []
        if r.assigned_avg_per_day > 0:
            if r.required_per_day_100 and r.required_per_day_100 > r.assigned_avg_per_day:
                notes.append("100% Ziel > Kap/Tag")
            if r.required_per_day_90 and r.required_per_day_90 > r.assigned_avg_per_day:
                notes.append("90% Ziel > Kap/Tag")
            if r.required_per_day_80 and r.required_per_day_80 > r.assigned_avg_per_day:
                notes.append("80% Ziel > Kap/Tag")
        else:
            notes.append("Keine Kapazität zugewiesen")
        note_text = ", ".join(notes) if notes else ""
        proj_summary_rows.append(
            [
                r.name,
                f"{r.period_start}–{r.period_end}",
                str(r.workdays),
                format_number_de(r.assigned_capacity_hours, 2),
                format_currency_eur(r.revenue_100),
                format_currency_eur(r.revenue_90),
                format_currency_eur(r.revenue_80),
                note_text,
            ]
        )

    # Capacities table
    cap_headers = ["Projekt"] + all_months
    cap_rows: List[List[str]] = []
    for r in results:
        row = [r.name]
        for mk in all_months:
            val = assigned.get((r.name, mk), 0.0)
            row.append(format_number_de(val, 2))
        cap_rows.append(row)

    # Per-day assigned avg
    perday_headers = ["Projekt"] + all_months
    perday_rows: List[List[str]] = []
    for r in results:
        month_counts: Dict[str, int] = {}
        for d in workdays_by_project.get(r.name, []):
            mk = month_key(d)
            month_counts[mk] = month_counts.get(mk, 0) + 1
        row = [r.name]
        for mk in all_months:
            days = month_counts.get(mk, 0)
            hours = assigned.get((r.name, mk), 0.0)
            avg = (hours / days) if days > 0 else 0.0
            row.append(format_number_de(avg, 2))
        perday_rows.append(row)

    # Required per-day avg to use full budget by end
    req_headers = ["Projekt"] + all_months
    req_rows: List[List[str]] = []
    for r in results:
        month_counts: Dict[str, int] = {}
        for d in workdays_by_project.get(r.name, []):
            mk = month_key(d)
            month_counts[mk] = month_counts.get(mk, 0) + 1
        total_assigned = sum(assigned.get((r.name, mk), 0.0) for mk in all_months)
        row = [r.name]
        for mk in all_months:
            cap_m = assigned.get((r.name, mk), 0.0)
            days = month_counts.get(mk, 0)
            if total_assigned > 0 and days > 0:
                share_budget = r.rest_budget_hours * (cap_m / total_assigned)
                need_avg = share_budget / days
            else:
                need_avg = 0.0
            row.append(format_number_de(need_avg, 2))
        req_rows.append(row)

    # Used vs unused considering limits and remaining budget
    used_by_project_month: Dict[Tuple[str, str], float] = {}
    for r in results:
        remaining = float(r.rest_budget_hours or 0.0)
        # find original project to read limits
        p = next((pp for pp in cfg.projects if pp.name == r.name), None)
        limits = dict(getattr(p, "limits_by_month", {}) or {}) if p else {}
        for mk in all_months:
            a = assigned.get((r.name, mk), 0.0)
            lim = float(limits.get(mk, float("inf")))
            use = min(a, lim, remaining)
            if use < 0:
                use = 0.0
            used_by_project_month[(r.name, mk)] = use
            remaining = max(0.0, remaining - use)

    used_headers = ["Projekt"] + all_months
    used_rows: List[List[str]] = []
    unused_headers = ["Projekt"] + all_months
    unused_rows: List[List[str]] = []
    for r in results:
        row_used = [r.name]
        row_unused = [r.name]
        for mk in all_months:
            a = assigned.get((r.name, mk), 0.0)
            u = used_by_project_month.get((r.name, mk), 0.0)
            row_used.append(format_number_de(u, 2))
            row_unused.append(format_number_de(max(0.0, a - u), 2))
        used_rows.append(row_used)
        unused_rows.append(row_unused)

    # Budget consumption rows (reuse used_by_project_month)
    budget_headers = ["Projekt"] + all_months + ["Restbudget (h)", "Status"]
    budget_rows: List[List[str]] = []
    budget_row_classes: List[str] = []
    for r in results:
        remaining = float(r.rest_budget_hours or 0.0)
        month_counts: Dict[str, int] = {}
        for d in workdays_by_project.get(r.name, []):
            mk = month_key(d)
            month_counts[mk] = month_counts.get(mk, 0) + 1
        active_months = [mk for mk in all_months if month_counts.get(mk, 0) > 0]
        last_active_month = active_months[-1] if active_months else None
        zero_month = None
        row = [r.name]
        for mk in all_months:
            consume = used_by_project_month.get((r.name, mk), 0.0)
            row.append(format_number_de(consume, 2))
            remaining = max(0.0, remaining - consume)
            if remaining == 0.0 and zero_month is None and consume > 0:
                zero_month = mk
        total_used = sum(used_by_project_month.get((r.name, mk), 0.0) for mk in all_months)
        row.append(format_number_de(remaining, 2))
        if remaining > 1e-9:
            status = "status-warn"
            status_text = "nicht voll verbraucht"
        else:
            if last_active_month and zero_month == last_active_month and abs(total_used - float(r.rest_budget_hours)) <= 1e-6:
                status = "status-ok"
                status_text = "passt genau"
            else:
                status = "status-error"
                status_text = "vor Projektende erschöpft"
        row.append(status_text)
        budget_rows.append(row)
        budget_row_classes.append(status)

    vacations_fmt = [str(d) for d in sorted(vac_in_period)]
    html = export_html_page(
        title="Forecast – Bericht",
        overview_items=overview_items,
        vacations=vacations_fmt,
        proj_summary_headers=proj_summary_headers,
        proj_summary_rows=proj_summary_rows,
        cap_headers=cap_headers,
        cap_rows=cap_rows,
        perday_headers=perday_headers,
        perday_rows=perday_rows,
        req_headers=req_headers,
        req_rows=req_rows,
        used_headers=used_headers,
        used_rows=used_rows,
        unused_headers=unused_headers,
        unused_rows=unused_rows,
        budget_headers=budget_headers,
        budget_rows=budget_rows,
        budget_row_classes=budget_row_classes,
    )
    return html

