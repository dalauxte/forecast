from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from .config import Config
from .calendar import intersection, workdays_in_period, month_key, niedersachsen_holidays
from .capacity import compute_capacity_by_date, aggregate_capacity_by_month
from .weights import assign_capacity_by_project_month
from .compute import compute_results
from .formatting import export_html_page, format_number_de, format_currency_eur, _html_escape


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
    # Precompute used/unused totals per project for KPIs
    # assigned computed later; for overview we fill after assigned is known
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
    cap_headers = [("Projekt", "Projektname")] + [(mk, f"Zugewiesen {mk} (h)") for mk in all_months]
    cap_rows: List[List[str]] = []
    for r in results:
        row = [r.name]
        for mk in all_months:
            val = assigned.get((r.name, mk), 0.0)
            row.append(format_number_de(val, 2))
        cap_rows.append(row)

    # Per-day assigned avg
    perday_headers = [("Projekt", "Projektname")] + [(mk, f"Ø Zuteilung {mk} (h/d)") for mk in all_months]
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
    req_headers = [("Projekt", "Projektname")] + [(mk, f"Ø nötig 100% {mk} (h/d)") for mk in all_months]
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

    # Used per month considering monthly limits and total budget (sequential)
    used_by_project_month: Dict[Tuple[str, str], float] = {}
    for r in results:
        remaining = float(r.rest_budget_hours or 0.0)
        # find original project to read limits
        p = next((pp for pp in cfg.projects if pp.name == r.name), None)
        limits = dict(getattr(p, "limits_by_month", {}) or {}) if p else {}
        for mk in all_months:
            a = assigned.get((r.name, mk), 0.0)
            lim = float(limits.get(mk, float("inf")))
            allow = min(a, lim)
            use = min(allow, remaining)
            if use < 0:
                use = 0.0
            used_by_project_month[(r.name, mk)] = use
            remaining = max(0.0, remaining - use)

    used_headers = [("Projekt", "Projektname")] + [(mk, f"Genutzt in {mk} (h)") for mk in all_months]
    used_rows: List[List[str]] = []
    for r in results:
        row_used = [r.name]
        # count project workdays per month
        month_counts: Dict[str, int] = {}
        for d in workdays_by_project.get(r.name, []):
            mk = month_key(d)
            month_counts[mk] = month_counts.get(mk, 0) + 1
        for mk in all_months:
            a = assigned.get((r.name, mk), 0.0)
            u = used_by_project_month.get((r.name, mk), 0.0)
            days = month_counts.get(mk, 0)
            if days > 0 and u > 0:
                cell = f"{format_number_de(u,2)} h ({format_number_de(u/days,2)} h/d)"
            else:
                cell = f"{format_number_de(u,2)} h"
            row_used.append(cell)
        used_rows.append(row_used)
    
    # Build monthly stacked chart HTML
    proj_names = [r.name for r in results]
    def color_for(idx: int) -> str:
        hue = (idx * 67) % 360
        return f"hsl({hue}, 65%, 55%)"
    legend_items = []
    for i, name in enumerate(proj_names):
        legend_items.append(f"<span class=\"swatch\" style=\"background:{color_for(i)}\"></span>{_html_escape(name)}")
    legend_items.append("<span class=\"swatch\" style=\"background:#cccccc\"></span>Rest")
    chart_rows = []
    for mk in all_months:
        total = float(capacity_by_month.get(mk, 0.0))
        segs = []
        used_sum = 0.0
        for i, name in enumerate(proj_names):
            # nur aktive Projekte im Monat berücksichtigen
            if name not in projects_by_month.get(mk, []):
                continue
            u = float(used_by_project_month.get((name, mk), 0.0))
            used_sum += u
            width = 0 if total <= 0 else max(0.0, (u / total) * 100.0)
            pct = (u/total*100.0) if total>0 else 0.0
            if width >= 12:
                lbl = f'<span class="lbl" style="color:#fff">{format_number_de(u,2)} h ({pct:.1f}%)</span>'
            else:
                lbl = ""
            segs.append(f"<div class=\"seg\" title=\"{_html_escape(name)}: {format_number_de(u,2)} h ({pct:.1f}%)\" style=\"width:{width:.4f}%;background:{color_for(i)}\">{lbl}</div>")
        rest = max(0.0, total - used_sum)
        rest_w = 0 if total <= 0 else max(0.0, (rest / total) * 100.0)
        if rest_w > 0:
            pct_r = (rest/total*100.0) if total>0 else 0.0
            if rest_w >= 12:
                lbl_r = f'<span class="lbl" style="color:#333">{format_number_de(rest,2)} h ({pct_r:.1f}%)</span>'
            else:
                lbl_r = ""
            segs.append(f"<div class=\"seg\" title=\"Rest: {format_number_de(rest,2)} h ({pct_r:.1f}%)\" style=\"width:{rest_w:.4f}%;background:#cccccc\">{lbl_r}</div>")
        chart_rows.append(f"<div class=\"row\"><div class=\"label\">{_html_escape(mk)}</div><div class=\"bar\">{''.join(segs)}</div><div class=\"label\">{format_number_de(total,2)} h</div></div>")
    monthly_stack_chart_html = "".join([
        "<div class=\"chart\">",
        "<div class=\"legend\">" + " &nbsp; ".join(legend_items) + "</div>",
        "".join(chart_rows),
        "</div>",
    ])

    # Second chart: per project within each month – used vs available (remaining budget at month start)
    proj_chart_rows = []
    for mk in all_months:
        # compute remaining budget per project at month start
        remaining_at_start = {}
        for name in proj_names:
            # recompute sequentially for this project up to this month
            rproj = next((rr for rr in results if rr.name == name), None)
            rem = float(rproj.rest_budget_hours if rproj else 0.0)
            for mk2 in all_months:
                if mk2 == mk:
                    break
                rem = max(0.0, rem - float(used_by_project_month.get((name, mk2), 0.0)))
            remaining_at_start[name] = rem
        max_avail = max(remaining_at_start.values()) if remaining_at_start else 0.0
        if max_avail <= 0:
            max_avail = 1.0
        # add a month header row
        proj_chart_rows.append(f"<div class=\"row\"><div class=\"label\"><strong>{_html_escape(mk)}</strong></div><div class=\"bar\"></div><div class=\"label\"></div></div>")
        for i, name in enumerate(proj_names):
            if name not in projects_by_month.get(mk, []):
                continue
            avail_total = float(remaining_at_start.get(name, 0.0))
            used = float(used_by_project_month.get((name, mk), 0.0))
            avail_after = max(0.0, avail_total - used)
            total_w = max(0.0, (avail_total / max_avail) * 100.0)
            used_w = max(0.0, (used / max_avail) * 100.0)
            avail_w = max(0.0, total_w - used_w)
            used_pct = (used / avail_total * 100.0) if avail_total > 0 else 0.0
            avail_pct = (avail_after / avail_total * 100.0) if avail_total > 0 else 0.0
            if used_w >= 12:
                lbl_u = f'<span class="lbl" style="color:#fff">{format_number_de(used,2)} h ({used_pct:.1f}%)</span>'
            else:
                lbl_u = ""
            seg_used = f"<div class=\"seg\" title=\"{_html_escape(name)} genutzt: {format_number_de(used,2)} h ({used_pct:.1f}%)\" style=\"width:{used_w:.4f}%;background:{color_for(i)}\">{lbl_u}</div>"
            # lighter color for available
            hue = (i * 67) % 360
            if avail_w >= 12:
                lbl_a = f'<span class="lbl" style="color:#333">{format_number_de(avail_after,2)} h ({avail_pct:.1f}%)</span>'
            else:
                lbl_a = ""
            seg_avail = f"<div class=\"seg\" title=\"{_html_escape(name)} verfügbar: {format_number_de(avail_after,2)} h ({avail_pct:.1f}%)\" style=\"width:{avail_w:.4f}%;background:hsl({hue}, 45%, 85%)\">{lbl_a}</div>"
            bar = f"<div class=\"bar\">{seg_used}{seg_avail}</div>"
            label_left = f"{_html_escape(name)}"
            label_right = f"{format_number_de(used,2)} / {format_number_de(avail_total,2)} h"
            proj_chart_rows.append(f"<div class=\"row\"><div class=\"label\">{label_left}</div>{bar}<div class=\"label\">{label_right}</div></div>")
    monthly_project_chart_html = "".join(["<div class=\"chart\">", "".join(proj_chart_rows), "</div>"])

    # Budget consumption rows (reuse used_by_project_month)
    budget_headers = [("Projekt", "Projektname")] + [(mk, f"Budgetverbrauch {mk} (h)") for mk in all_months] + [("Restbudget (h)", "Verbleibendes Budget am Projektende"), ("Status", "Budgetstatus zum Projektende")]
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

    # Enhance overview with totals (assigned/used/unused) and project status counts
    total_assigned_all = sum(assigned.get((r.name, mk), 0.0) for r in results for mk in all_months)
    total_used_all = sum(used_by_project_month.get((r.name, mk), 0.0) for r in results for mk in all_months)
    total_unused_all = max(0.0, total_assigned_all - total_used_all)
    overview_items.extend([
        ("∑ Zugewiesen (h)", format_number_de(total_assigned_all, 2)),
        ("∑ Genutzt (h)", format_number_de(total_used_all, 2)),
        ("∑ Ungenutzt (h)", format_number_de(total_unused_all, 2)),
    ])

    status_counts = {"ok": 0, "warn": 0, "error": 0}
    for cls in budget_row_classes:
        if cls == "status-ok":
            status_counts["ok"] += 1
        elif cls == "status-warn":
            status_counts["warn"] += 1
        elif cls == "status-error":
            status_counts["error"] += 1
    overview_items.extend([
        ("Projekte (grün)", str(status_counts["ok"])),
        ("Projekte (gelb)", str(status_counts["warn"])),
        ("Projekte (rot)", str(status_counts["error"])),
    ])

    # Add portfolio-level aggregates per project: used/unused and remaining budget columns
    # Extend proj_summary_headers and rows accordingly
    # We reconstruct with additional columns
    new_headers = [
        ("Projekt", "Projektname"),
        ("Zeitraum", "Aktiver Zeitraum innerhalb der Planung"),
        ("Tage (d)", "Arbeitstage des Projekts im Zeitraum"),
        ("Kapazität (h)", "Summe zugeteilter Stunden über den Zeitraum"),
        ("Genutzt (h)", "Summe tatsächlich genutzter Stunden (mit Limits/Budget)"),
        ("Ungenutzt (h)", "Summe nicht genutzter Zuteilung (verfallen)"),
        ("Restbudget (h)", "Verbleibendes Projektbudget nach Nutzung"),
        ("Umsatz 100%", "Budget × Satz"),
        ("Umsatz 90%", "90% von Budget × Satz"),
        ("Umsatz 80%", "80% von Budget × Satz"),
        ("Hinweise", "Wichtige Hinweise zur Auslastung"),
    ]
    new_rows: List[List[str]] = []
    for row in proj_summary_rows:
        name = row[0]
        assigned_total = 0.0
        used_total = 0.0
        for mk in all_months:
            assigned_total += assigned.get((name, mk), 0.0)
            used_total += used_by_project_month.get((name, mk), 0.0)
        unused_total = max(0.0, assigned_total - used_total)
        rproj = next((rr for rr in results if rr.name == name), None)
        rest_remaining = (rproj.rest_budget_hours if rproj else 0.0) - used_total
        rest_remaining = max(0.0, rest_remaining)

        new_rows.append([
            row[0],
            row[1],
            row[2],
            format_number_de(assigned_total, 2),
            format_number_de(used_total, 2),
            format_number_de(unused_total, 2),
            format_number_de(rest_remaining, 2),
            row[4],  # Umsatz 100%
            row[5],  # Umsatz 90%
            row[6],  # Umsatz 80%
            row[7],  # Hinweise
        ])
    proj_summary_headers = new_headers
    proj_summary_rows = new_rows

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
        monthly_stack_chart_html=monthly_stack_chart_html,
        monthly_project_chart_html=monthly_project_chart_html,
        budget_headers=budget_headers,
        budget_rows=budget_rows,
        budget_row_classes=budget_row_classes,
    )
    return html
