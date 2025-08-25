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
            format_number_de(r["ØKap/Tag"], 2),
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


def export_csv_semicolon(rows: List[dict]) -> str:
    # Returns CSV content as a string with semicolon delimiter and DE decimals
    headers = [
        "Projekt","Zeitraum","Tage","Kapazität (h)","ØKap/Tag","Øh/Tag 100%","Øh/Tag 90%","Øh/Tag 80%","Util 100%","Util 90%","Util 80%","Umsatz 100%","Umsatz 90%","Umsatz 80%"
    ]
    out = []
    out.append(";".join(headers))
    for r in rows:
        out.append(";".join([
            str(r["Projekt"]),
            str(r["Zeitraum"]),
            str(r["Tage"]),
            format_number_de(r["Kapazität (h)"], 2),
            format_number_de(r["ØKap/Tag"], 2),
            format_number_de(r["Øh/Tag 100%"], 2),
            format_number_de(r["Øh/Tag 90%"], 2),
            format_number_de(r["Øh/Tag 80%"], 2),
            format_number_de(r["Util 100%"], 2),
            format_number_de(r["Util 90%"], 2),
            format_number_de(r["Util 80%"], 2),
            format_number_de(r["Umsatz 100%"], 2),
            format_number_de(r["Umsatz 90%"], 2),
            format_number_de(r["Umsatz 80%"], 2),
        ]))
    return "\n".join(out)
