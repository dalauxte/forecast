from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple

from .calendar import intersection, month_key


@dataclass
class ProjectResult:
    name: str
    period_start: date
    period_end: date
    workdays: int
    rest_budget_hours: float
    required_per_day_100: float
    required_per_day_90: float
    required_per_day_80: float
    assigned_capacity_hours: float
    assigned_avg_per_day: float
    utilization_100: float | None
    utilization_90: float | None
    utilization_80: float | None
    revenue_100: float
    revenue_90: float
    revenue_80: float


def _safe_div(a: float, b: float) -> float | None:
    if b == 0:
        return None
    return a / b


def compute_results(
    planning_period: Tuple[date, date],
    projects: List[dict],  # dict: {name, start, end, rest_budget_hours, rate, weights_by_month}
    workdays_by_project: Dict[str, List[date]],
    assigned_capacity_by_project_month: Dict[Tuple[str, str], float],
    round_hours: float,
) -> List[ProjectResult]:
    results: List[ProjectResult] = []
    for p in projects:
        name = p["name"]
        pj_period = (p["start"], p["end"])
        cut = intersection(planning_period, pj_period)
        if cut is None:
            continue
        wdays = workdays_by_project.get(name, [])
        wd_count = len(wdays)
        if wd_count == 0:
            # ignore project without workdays in intersection
            continue

        rest = float(p["rest_budget_hours"]) if p.get("rest_budget_hours") is not None else 0.0
        rate = float(p["rate_eur_per_h"]) if p.get("rate_eur_per_h") is not None else 0.0

        # Assigned capacity
        assigned_total = 0.0
        for d in wdays:
            mk = month_key(d)
            assigned_total += assigned_capacity_by_project_month.get((name, mk), 0.0) / max(1, len([x for x in wdays if month_key(x) == mk]))
        # average per day from assigned
        assigned_avg = assigned_total / wd_count if wd_count > 0 else 0.0

        def r(v: float) -> float:
            if round_hours <= 0:
                return v
            # round half away from zero to nearest multiple of round_hours
            q = v / round_hours
            from math import floor
            return round_hours * (floor(q + 0.5))

        def req_per_day(q: float) -> float:
            need = q * rest
            return r(need / wd_count) if wd_count > 0 else 0.0

        r100 = req_per_day(1.0)
        r90 = req_per_day(0.9)
        r80 = req_per_day(0.8)

        u100 = _safe_div(r100, assigned_avg if assigned_avg > 0 else 0.0) if assigned_avg > 0 else None
        u90 = _safe_div(r90, assigned_avg if assigned_avg > 0 else 0.0) if assigned_avg > 0 else None
        u80 = _safe_div(r80, assigned_avg if assigned_avg > 0 else 0.0) if assigned_avg > 0 else None

        results.append(
            ProjectResult(
                name=name,
                period_start=cut[0],
                period_end=cut[1],
                workdays=wd_count,
                rest_budget_hours=rest,
                required_per_day_100=r100,
                required_per_day_90=r90,
                required_per_day_80=r80,
                assigned_capacity_hours=assigned_total,
                assigned_avg_per_day=assigned_avg,
                utilization_100=u100,
                utilization_90=u90,
                utilization_80=u80,
                revenue_100=1.0 * rest * rate,
                revenue_90=0.9 * rest * rate,
                revenue_80=0.8 * rest * rate,
            )
        )

    return results

