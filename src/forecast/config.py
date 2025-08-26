from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
import os
import yaml


def _parse_date(s, field_name: str) -> date:
    """Accept str (YYYY-MM-DD), datetime, or date from YAML and return date."""
    if isinstance(s, date) and not isinstance(s, datetime):
        return s
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, str):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError(f"Ungültiges Datum für {field_name}: {s} (erwartet YYYY-MM-DD)") from e
    raise ValueError(f"Ungültiger Typ für {field_name}: {type(s).__name__}")


def _parse_month(s: str, field_name: str) -> str:
    try:
        datetime.strptime(s, "%Y-%m")
        return s
    except Exception as e:
        raise ValueError(f"Ungültiger Monat für {field_name}: {s} (erwartet YYYY-MM)") from e


@dataclass
class PlanningPeriod:
    start: date
    end: date

    @staticmethod
    def from_dict(d: dict) -> "PlanningPeriod":
        return PlanningPeriod(
            start=_parse_date(d["start"], "planning_period.start"),
            end=_parse_date(d["end"], "planning_period.end"),
        )

    def validate(self) -> None:
        if self.end < self.start:
            raise ValueError("planning_period.end liegt vor planning_period.start")


@dataclass
class Settings:
    state: str = "NI"
    round_hours: float = 0.15
    locale: str = "de-DE"
    as_of: Optional[date] = None
    planning_period: PlanningPeriod = field(default_factory=lambda: PlanningPeriod(date.today(), date.today()))

    @staticmethod
    def from_dict(d: dict) -> "Settings":
        as_of = _parse_date(d["as_of"], "as_of") if d.get("as_of") else None
        pp = PlanningPeriod.from_dict(d["planning_period"]) if d.get("planning_period") else None
        if pp is None:
            raise ValueError("settings.planning_period ist erforderlich")
        s = Settings(
            state=d.get("state", "NI"),
            round_hours=float(d.get("round_hours", 0.15)),
            locale=d.get("locale", "de-DE"),
            as_of=as_of,
            planning_period=pp,
        )
        s.validate()
        return s

    def validate(self) -> None:
        if self.round_hours <= 0:
            raise ValueError("round_hours muss > 0 sein")
        self.planning_period.validate()


@dataclass
class IntervalOverride:
    start: date
    end: date
    hours_per_day: float

    @staticmethod
    def from_dict(d: dict) -> "IntervalOverride":
        return IntervalOverride(
            start=_parse_date(d["start"], "interval_overrides.start"),
            end=_parse_date(d["end"], "interval_overrides.end"),
            hours_per_day=float(d["hours_per_day"]),
        )

    def validate(self) -> None:
        if self.end < self.start:
            raise ValueError("interval_overrides.end liegt vor start")
        if self.hours_per_day < 0:
            raise ValueError("hours_per_day darf nicht negativ sein")


@dataclass
class CapacityConfig:
    per_weekday: Dict[str, float] = field(default_factory=dict)
    interval_overrides: List[IntervalOverride] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict) -> "CapacityConfig":
        per_weekday = d.get("per_weekday", {}) or {}
        # Defaults: 8h Mo–Fr, 0 am Wochenende
        defaults = {"mon": 8.0, "tue": 8.0, "wed": 8.0, "thu": 8.0, "fri": 8.0, "sat": 0.0, "sun": 0.0}
        merged = {**defaults, **{k: float(v) for k, v in per_weekday.items()}}
        overrides = [IntervalOverride.from_dict(x) for x in (d.get("interval_overrides") or [])]
        cfg = CapacityConfig(per_weekday=merged, interval_overrides=overrides)
        for o in cfg.interval_overrides:
            o.validate()
        return cfg


@dataclass
class CalendarConfig:
    vacation_days: List[date] = field(default_factory=list)
    holiday_overrides_add: List[date] = field(default_factory=list)
    holiday_overrides_remove: List[date] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict) -> "CalendarConfig":
        # Accept both single dates and ranges {start, end} inside vacation_days.
        raw_vac = d.get("vacation_days") or []

        def _expand_range(s: date, e: date) -> List[date]:
            if e < s:
                raise ValueError("calendar.vacation_days[*]: end liegt vor start")
            out: List[date] = []
            cur = s
            while cur <= e:
                out.append(cur)
                cur = cur + timedelta(days=1)
            return out

        vacations: List[date] = []
        for idx, x in enumerate(raw_vac):
            # Allow mapping with {start, end} or single date-like value
            if isinstance(x, dict):
                if "start" in x and "end" in x:
                    s = _parse_date(x["start"], f"calendar.vacation_days[{idx}].start")
                    e = _parse_date(x["end"], f"calendar.vacation_days[{idx}].end")
                    vacations.extend(_expand_range(s, e))
                elif "date" in x:
                    vacations.append(_parse_date(x["date"], f"calendar.vacation_days[{idx}].date"))
                else:
                    raise ValueError(
                        "calendar.vacation_days[*]: erwartet Datum (YYYY-MM-DD) oder Mapping mit 'start'/'end'"
                    )
            else:
                vacations.append(_parse_date(x, f"calendar.vacation_days[{idx}]"))
        overrides = d.get("holiday_overrides") or {}
        add = [_parse_date(x, "holiday_overrides.add[*]") for x in (overrides.get("add") or [])]
        rem = [_parse_date(x, "holiday_overrides.remove[*]") for x in (overrides.get("remove") or [])]
        return CalendarConfig(vacation_days=vacations, holiday_overrides_add=add, holiday_overrides_remove=rem)


@dataclass
class SicknessConfig:
    prob_per_workday: float = 0.02

    @staticmethod
    def from_dict(d: dict) -> "SicknessConfig":
        p = float(d.get("prob_per_workday", 0.02))
        if p < 0 or p > 1:
            raise ValueError("sickness.prob_per_workday muss zwischen 0 und 1 liegen")
        return SicknessConfig(prob_per_workday=p)


@dataclass
class Project:
    name: str
    start: date
    end: date
    rest_budget_hours: float
    rate_eur_per_h: float
    weights_by_month: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def from_dict(d: dict) -> "Project":
        weights = { _parse_month(k, f"projects.weights_by_month[{k}]"): float(v) for k, v in (d.get("weights_by_month") or {}).items() }
        p = Project(
            name=str(d["name"]),
            start=_parse_date(d["start"], "projects.start"),
            end=_parse_date(d["end"], "projects.end"),
            rest_budget_hours=float(d["rest_budget_hours"]),
            rate_eur_per_h=float(d["rate_eur_per_h"]),
            weights_by_month=weights,
        )
        p.validate()
        return p

    def validate(self) -> None:
        if self.end < self.start:
            raise ValueError(f"Projekt {self.name}: end liegt vor start")
        if self.rest_budget_hours < 0:
            raise ValueError(f"Projekt {self.name}: rest_budget_hours darf nicht negativ sein")
        if self.rate_eur_per_h < 0:
            raise ValueError(f"Projekt {self.name}: rate_eur_per_h darf nicht negativ sein")
        for m, w in self.weights_by_month.items():
            if w < 0 or w > 100:
                raise ValueError(f"Projekt {self.name}: Gewicht {w} für Monat {m} außerhalb 0–100")


@dataclass
class Config:
    settings: Settings
    capacity: CapacityConfig
    calendar: CalendarConfig
    sickness: SicknessConfig
    projects: List[Project]


def load_config(path: str) -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config nicht gefunden: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    try:
        settings = Settings.from_dict(data.get("settings") or {})
        capacity = CapacityConfig.from_dict(data.get("capacity") or {})
        calendar = CalendarConfig.from_dict(data.get("calendar") or {})
        sickness = SicknessConfig.from_dict(data.get("sickness") or {})
        projects = [Project.from_dict(x) for x in (data.get("projects") or [])]

        if not projects:
            raise ValueError("Mindestens ein Projekt muss in projects definiert sein")

        return Config(settings=settings, capacity=capacity, calendar=calendar, sickness=sickness, projects=projects)
    except Exception:
        # Re-raise with context
        raise
