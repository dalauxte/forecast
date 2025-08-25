from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Iterable, List, Set, Tuple

try:
    import holidays  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    holidays = None  # type: ignore

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def daterange(start: date, end: date) -> Iterable[date]:
    d = start
    while d <= end:
        yield d
        d = d + timedelta(days=1)


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def intersection(a: Tuple[date, date], b: Tuple[date, date]) -> Tuple[date, date] | None:
    s = max(a[0], b[0])
    e = min(a[1], b[1])
    if s > e:
        return None
    return (s, e)


def niedersachsen_holidays(years: Iterable[int]) -> Set[date]:
    found: Set[date] = set()
    if holidays is None:
        # Fallback: keine automatische Berechnung, nur leer
        return found
    try:
        de = holidays.Germany(years=list(years), prov="NI")  # type: ignore
        for d in de:
            found.add(d)
        return found
    except Exception:
        return found


def workdays_in_period(period: Tuple[date, date], state: str, holiday_overrides_add: List[date], holiday_overrides_remove: List[date], vacation_days: List[date]) -> List[date]:
    start, end = period
    years = set(range(start.year, end.year + 1))
    hols: Set[date] = set()
    if state.upper() == "NI":
        hols = niedersachsen_holidays(years)
    # Apply overrides
    hols.update(holiday_overrides_add)
    hols.difference_update(holiday_overrides_remove)

    vac = set(vacation_days)

    res: List[date] = []
    for d in daterange(start, end):
        if d.weekday() >= 5:  # Weekend
            continue
        if d in hols:
            continue
        if d in vac:
            continue
        res.append(d)
    return res

