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


def _render_html_table(headers: List[str], rows: List[List[str]], row_classes: List[str] | None = None) -> str:
    ths = "".join(f"<th>{_html_escape(h)}</th>" for h in headers)
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
    unused_headers: List[str],
    unused_rows: List[List[str]],
    budget_headers: List[str],
    budget_rows: List[List[str]],
    budget_row_classes: List[str] | None = None,
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
      /* Status coloring for budget table */
      tr.status-ok { background: #e8f5e9; }      /* green */
      tr.status-warn { background: #fff8e1; }    /* yellow */
      tr.status-error { background: #ffebee; }   /* red */
      .legend { font-size: 12px; color: #444; }
      .legend span { display: inline-block; padding: 3px 6px; margin-right: 8px; border-radius: 3px; }
      .legend .ok { background: #e8f5e9; }
      .legend .warn { background: #fff8e1; }
      .legend .err { background: #ffebee; }
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
        "<h2>Übersicht</h2>",
        overview_html,
        "<h2>Urlaube und Abwesenheiten</h2>",
        vac_html,
        "<h2>Projekte – Zeitraum, Tage, Kapazität</h2>",
        _render_html_table(proj_summary_headers, proj_summary_rows),
        "<h2>Geplante Kapazitäten je Projekt</h2>",
        _render_html_table(cap_headers, cap_rows),
        "<h2>Verteilung Stunden pro Projekt (Øh/Arbeitstag im Monat)</h2>",
        _render_html_table(perday_headers, perday_rows),
        "<h2>Erforderliche Øh/Arbeitstag je Monat (für 100%)</h2>",
        _render_html_table(req_headers, req_rows),
        "<h2>Genutzte Stunden je Projekt (Monat)</h2>",
        _render_html_table(used_headers, used_rows),
        "<h2>Ungenutzte Kapazität je Projekt (Monat)</h2>",
        _render_html_table(unused_headers, unused_rows),
        "<h2>Budgetverbrauch pro Projekt (h)</h2>",
        "<div class=\"legend\"><span class=\"ok\">Grün: passt genau</span><span class=\"warn\">Gelb: Budget nicht voll verbraucht</span><span class=\"err\">Rot: Budget vor Projektende erschöpft</span></div>",
        _render_html_table(budget_headers, budget_rows, row_classes=budget_row_classes or []),
        "</body></html>",
    ]
    return "\n".join(parts)
