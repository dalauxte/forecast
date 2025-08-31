from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, List, Optional

try:
    from tabulate import tabulate  # type: ignore
except Exception:  # pragma: no cover
    tabulate = None  # type: ignore


def format_number_de(x: Optional[float], decimals: int = 2) -> str:
    if x is None:
        return "-"
    neg = x < 0
    x = abs(x)
    s = f"{x:.{decimals}f}"
    intp, frac = s.split(".")
    groups = []
    while intp:
        groups.append(intp[-3:])
        intp = intp[:-3]
    intf = ".".join(reversed(groups)) if groups else "0"
    s = f"{intf},{frac}"
    if neg:
        s = "-" + s
    return s


def format_currency_eur(x: Optional[float]) -> str:
    if x is None:
        return "-"
    return f"{format_number_de(x, 2)} €"


def render_table(rows: List[dict]) -> str:
    headers = [
        "Projekt",
        "Zeitraum",
        "Tage",
        "Kapazität (h)",
        "ØKap/Tag",
        "Øh/Tag 100%",
        "Øh/Tag 90%",
        "Øh/Tag 80%",
        "Util 100%",
        "Util 90%",
        "Util 80%",
        "Umsatz 100%",
        "Umsatz 90%",
        "Umsatz 80%",
    ]
    table = []
    for r in rows:
        table.append([
            r["Projekt"],
            r["Zeitraum"],
            r["Tage"],
            format_number_de(r["Kapazität (h)"], 2),
            format_number_de(r["ØKap/Tag"], 2),
            format_number_de(r["Øh/Tag 100%"], 2),
            format_number_de(r["Øh/Tag 90%"], 2),
            format_number_de(r["Øh/Tag 80%"], 2),
            format_number_de(r["Util 100%"], 2),
            format_number_de(r["Util 90%"], 2),
            format_number_de(r["Util 80%"], 2),
            format_currency_eur(r["Umsatz 100%"]),
            format_currency_eur(r["Umsatz 90%"]),
            format_currency_eur(r["Umsatz 80%"]),
        ])
    if tabulate:
        return tabulate(table, headers=headers, tablefmt="github")
    # Fallback simple formatting
    col_widths = [max(len(str(h)), *(len(str(row[i])) for row in table)) for i, h in enumerate(headers)]
    def fmt_row(row):
        return " | ".join(str(v).ljust(col_widths[i]) for i, v in enumerate(row))
    lines = [fmt_row(headers), "-+-".join("-" * w for w in col_widths)]
    lines += [fmt_row(r) for r in table]
    return "\n".join(lines)


"""
CSV-Export wurde entfernt. Der HTML-Export ist die primäre Ausgabe.
"""


# ---------------- HTML Export ----------------

def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_html_table(headers, rows: List[List[str]], row_classes: List[str] | None = None) -> str:
    def _th(h):
        if isinstance(h, tuple) and len(h) == 2:
            label, title = h
            return f"<th title=\"{_html_escape(str(title))}\">{_html_escape(str(label))}</th>"
        return f"<th>{_html_escape(str(h))}</th>"
    ths = "".join(_th(h) for h in headers)
    trs = []
    for idx, r in enumerate(rows):
        tds = "".join(f"<td>{_html_escape(str(v))}</td>" for v in r)
        cls = ""
        if row_classes and idx < len(row_classes) and row_classes[idx]:
            cls = f" class=\"{_html_escape(row_classes[idx])}\""
        trs.append(f"<tr{cls}>{tds}</tr>")
    tbody = "\n".join(trs)
    return f"<table><thead><tr>{ths}</tr></thead><tbody>{tbody}</tbody></table>"


def export_html_page(
    title: str,
    overview_items: List[tuple[str, str]],
    vacations: List[str],
    proj_summary_headers: List[str],
    proj_summary_rows: List[List[str]],
    cap_headers: List[str],
    cap_rows: List[List[str]],
    perday_headers: List[str],
    perday_rows: List[List[str]],
    req_headers: List[str],
    req_rows: List[List[str]],
    used_headers: List[str],
    used_rows: List[List[str]],
    used_perday_headers: List[str],
    used_perday_rows: List[List[str]],
    budget_headers: List[str],
    budget_rows: List[List[str]],
    budget_row_classes: List[str] | None = None,
    monthly_stack_chart_html: str | None = None,
    monthly_project_chart_html: str | None = None,
) -> str:
    styles = """
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
      h1 { font-size: 20px; margin-bottom: 8px; }
      h2 { font-size: 16px; margin-top: 24px; }
      table { border-collapse: collapse; margin: 12px 0; width: 100%; }
      th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }
      th { background: #f7f7f7; text-align: left; }
      .kv { width: auto; }
      .kv td:first-child { font-weight: 600; width: 220px; }
      .muted { color: #666; }
      .desc { color: #444; font-size: 13px; margin: 0 0 8px; }
      /* Status coloring for budget table */
      tr.status-ok { background: #e8f5e9; }      /* green */
      tr.status-warn { background: #fff8e1; }    /* yellow */
      tr.status-error { background: #ffebee; }   /* red */
      .legend { font-size: 12px; color: #444; }
      .legend span { display: inline-block; padding: 3px 6px; margin-right: 8px; border-radius: 3px; }
      .legend .ok { background: #e8f5e9; }
      .legend .warn { background: #fff8e1; }
      .legend .err { background: #ffebee; }
      /* Stacked chart */
      .chart { margin: 12px 0; }
      .chart .row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
      .chart .label { width: 90px; font-size: 12px; color: #333; }
      .chart .bar { flex: 1; display: flex; height: 16px; background: #f1f1f1; border: 1px solid #e0e0e0; }
      .chart .seg { height: 100%; position: relative; }
      .chart .seg .lbl { position: absolute; left: 50%; transform: translateX(-50%); font-size: 10px; line-height: 16px; white-space: nowrap; }
      .legend .swatch { display: inline-block; width: 10px; height: 10px; vertical-align: middle; margin-right: 6px; border: 1px solid #ddd; }
    </style>
    """

    # Overview as key-value table
    ov_rows = [[k, v] for (k, v) in overview_items]
    overview_html = _render_html_table(["Name", "Wert"], ov_rows).replace("<table>", "<table class=\"kv\">", 1)

    vac_html = "<p class=\"muted\">Keine Einträge</p>" if not vacations else (
        "<ul>" + "".join(f"<li>{_html_escape(v)}</li>" for v in vacations) + "</ul>"
    )

    parts = [
        "<!DOCTYPE html>",
        "<html lang=\"de\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{_html_escape(title)}</title>",
        styles,
        "</head>",
        "<body>",
        f"<h1>{_html_escape(title)}</h1>",
        "<h2>Hilfe</h2>",
        "<p class=\"desc\">Kurze Erläuterungen zu Begriffen und Berechnungen.</p>",
        "<ul class=\"desc\">"
        "<li><strong>Zuteilung (Kapazität)</strong>: Verfügbarkeit, die monatsweise per <em>weights_by_month</em> auf Projekte verteilt wird.</li>"
        "<li><strong>Genutzt</strong>: Tatsächlich verwendete Stunden je Monat: min(Zuteilung, Monats-Limit, verbleibendes Budget).</li>"
        "<li><strong>Ungenutzt</strong>: Zuteilung − Genutzt im Monat (verfällt für das Projekt).</li>"
        "<li><strong>Ø/Tag (Zuteilung)</strong>: Zuteilung im Monat geteilt durch Arbeitstage des Projekts in diesem Monat.</li>"
        "<li><strong>Erforderlicher Ø/Tag</strong>: Budget proportional zur Zuteilung auf Monate verteilt, dann durch Arbeitstage geteilt.</li>"
        "<li><strong>Status</strong>: Grün = Budget exakt am Projektende verbraucht; Gelb = Restbudget bleibt; Rot = Budget vor Projektende erschöpft.</li>"
        "</ul>",
        "<h2>Übersicht</h2>",
        "<p class=\"desc\">Kompakte Kennzahlen zum Planungszeitraum: Arbeitstage, Gesamt-\nKapazität sowie Verteilung auf Projekte (zugewiesen/genutzt/ungenutzt)\nund Zahl der Projekte nach Status.</p>",
        overview_html,
        "<h2>Urlaube und Abwesenheiten</h2>",
        "<p class=\"desc\">Auflistung aller hinterlegten Urlaubs- und Abwesenheitstage im\nPlanungszeitraum. Diese Tage reduzieren die verfügbaren Arbeitstage\nund damit die Kapazität.</p>",
        vac_html,
        "<h2>Projekte – Zeitraum, Tage, Kapazität</h2>",
        "<p class=\"desc\">Pro Projekt: aktiver Zeitraum, Anzahl Arbeitstage, gesamte zugewiesene\nKapazität, tatsächlich genutzte Stunden (unter Limits/Budget),\nungenutzte Stunden, verbleibendes Budget und erwartete Umsätze.</p>",
        _render_html_table(proj_summary_headers, proj_summary_rows),
        "<h2>Geplante Kapazitäten je Projekt</h2>",
        "<p class=\"desc\">Zuteilung nach Monaten auf Basis der Gewichte (weights_by_month).\nDiese Werte zeigen die geplante Verfügbarkeit, noch ohne Limits/Budget.</p>",
        _render_html_table(cap_headers, cap_rows),
        "<h2>Verteilung Stunden pro Projekt (Øh/Arbeitstag im Monat)</h2>",
        "<p class=\"desc\">Durchschnittliche tägliche Zuteilung im jeweiligen Monat:\nZuteilung (h) geteilt durch Arbeitstage des Projekts in diesem Monat.</p>",
        _render_html_table(perday_headers, perday_rows),
        "<h2>Erforderliche Øh/Arbeitstag je Monat (für 100%)</h2>",
        "<p class=\"desc\">Notwendiger täglicher Durchschnitt, damit das Projektbudget bis zum\nProjektende aufgeht. Das Budget wird proportional zur Zuteilung auf\nMonate verteilt und durch die jeweiligen Arbeitstage geteilt.</p>",
        _render_html_table(req_headers, req_rows),
        "<h2>Genutzte Stunden je Projekt (Monat)</h2>",
        "<p class=\"desc\">Reale Nutzung je Monat unter Berücksichtigung von Monats-Limits und\nRestbudget: min(Zuteilung, Limit, verbleibendes Budget).</p>",
        _render_html_table(used_headers, used_rows),
        "<h2>Ø genutzte Stunden/Arbeitstag (Monat)</h2>",
        "<p class=\"desc\">Durchschnittlich genutzte Stunden pro Arbeitstag je Monat: genutzte Stunden geteilt durch Projekt‑Arbeitstage im Monat.</p>",
        _render_html_table(used_perday_headers, used_perday_rows),
        "<h2>Kapazitätsnutzung je Monat (gestapelt)</h2>",
        "<p class=\"desc\">Gesamtkapazität pro Monat mit den genutzten Anteilen je Projekt und dem verbleibenden Rest (nicht genutzt/zugewiesen).</p>",
        (monthly_stack_chart_html or '<p class="muted">Keine Daten</p>'),
        "<h2>Projekt‑Kapazität je Monat (genutzt vs. verfügbar)</h2>",
        "<p class=\"desc\">Für jeden Monat/Projekt: Anteil der genutzten Stunden im Verhältnis zum Restbudget, das zu Monatsbeginn verfügbar ist (sequentieller Verbrauch des Projektbudgets).</p>",
        (monthly_project_chart_html or '<p class="muted">Keine Daten</p>'),
        "<h2>Budgetverbrauch pro Projekt (h)</h2>",
        "<p class=\"desc\">Monatlicher Budget-Burn. Status: Grün = Budget exakt am Projektende\nverbraucht; Gelb = Restbudget bleibt; Rot = Budget vor Projektende\nerreicht 0.</p>",
        "<div class=\"legend\"><span class=\"ok\">Grün: passt genau</span><span class=\"warn\">Gelb: Budget nicht voll verbraucht</span><span class=\"err\">Rot: Budget vor Projektende erschöpft</span></div>",
        _render_html_table(budget_headers, budget_rows, row_classes=budget_row_classes or []),
        "</body></html>",
    ]
    return "\n".join(parts)
