from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List, Tuple

from .calendar import month_key

WEEKDAY_INDEX_TO_KEY = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}


def compute_capacity_by_date(
    workdays: List[date],
    per_weekday: Dict[str, float],
    interval_overrides: List[Tuple[date, date, float]],
    sick_prob_per_workday: float,
) -> Dict[date, float]:
    cap: Dict[date, float] = {}
    # Base from per_weekday
    for d in workdays:
        cap[d] = float(per_weekday.get(WEEKDAY_INDEX_TO_KEY[d.weekday()], 0.0))

    # Apply interval overrides
    for (s, e, hpd) in interval_overrides:
        if e < s:
            continue
        dd = s
        while dd <= e:
            if dd in cap:
                cap[dd] = float(hpd)
            dd = dd.fromordinal(dd.toordinal() + 1)

    # Apply sickness as expected fractional reduction
    if sick_prob_per_workday > 0:
        factor = max(0.0, 1.0 - sick_prob_per_workday)
        for d in list(cap.keys()):
            cap[d] = round(cap[d] * factor, 6)

    return cap


def aggregate_capacity_by_month(capacity_by_date: Dict[date, float]) -> Dict[str, float]:
    res: Dict[str, float] = {}
    for d, h in capacity_by_date.items():
        mk = month_key(d)
        res[mk] = res.get(mk, 0.0) + h
    return res

