from __future__ import annotations

from typing import Dict, List, Tuple


def compute_month_weights(
    active_projects: List[str],
    explicit_weights: Dict[str, Dict[str, float]],
    month: str,
) -> Dict[str, float]:
    """
    Returns weights per project for the given month.
    - If sum of explicit weights for the month is 0 (i.e., no weights provided), distribute equally among active_projects.
    - If some explicit weights exist: use them, projects without entry get 0. Validate sum <= 100.
    """
    weights_this_month = {p: float(explicit_weights.get(p, {}).get(month, 0.0)) for p in active_projects}
    total = sum(weights_this_month.values())
    if total == 0:
        if not active_projects:
            return {}
        eq = 100.0 / len(active_projects)
        return {p: eq for p in active_projects}
    if total > 100.0 + 1e-9:
        raise ValueError(f"Summe der Gewichte für {month} überschreitet 100%: {total}")
    return weights_this_month


def assign_capacity_by_project_month(
    capacity_by_month: Dict[str, float],
    projects_by_month: Dict[str, List[str]],
    explicit_weights: Dict[str, Dict[str, float]],
) -> Dict[Tuple[str, str], float]:
    """
    Returns mapping of (project, month) -> assigned capacity hours.
    """
    res: Dict[Tuple[str, str], float] = {}
    for month, cap in capacity_by_month.items():
        actives = projects_by_month.get(month, [])
        if not actives or cap <= 0:
            continue
        w = compute_month_weights(actives, explicit_weights, month)
        for p in actives:
            res[(p, month)] = cap * (w.get(p, 0.0) / 100.0)
    return res

