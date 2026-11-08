"""The economy at a glance, on the home page: a heat map of the past twelve months and the key figures at their
highest or lowest in years.

The heat map has a row for each reading behind the Analysis page's activity and inflation composites
(econpulse/analytics.py), each month shaded by how far the reading is from its own normal since 2013 (its
z-score: the median and spread of its history, Covid years left out). Warm colours are above normal (activity
stronger, inflation hotter; a fall in unemployment counts as stronger), cool colours below. Each block opens
with its composite. Quarterly readings span the three months of their quarter.

The records are the key figures whose latest reading, as shown, is the highest or lowest in at least two years.
"""

import pandas as pd

from . import analytics, i18n
from .analytics import ACTIVITY, INFLATION, MINUS, Z_CLIP
from .charts import source_page
from .homepage import _format, extreme, headline_series, since_text
from .i18n import _
from .snapshot import period_label
from .tables import Data

MONTHS = 12
STEPS = (0.5, 1.0, 2.0)          # |z| at which a cell takes the first, second and third shade
RECORD_YEARS = 2                 # how far back a reading must reach to count as a record
MAX_RECORDS = 8
# The figures watched for records, as their tiles show them, besides the key indicators themselves.
RECORD_EXTRA = [("afiliados", "level"), ("unemployment_monthly", "level"), ("employment_epa", "level"),
                ("industrial_production", "yoy"), ("retail_sales", "yoy"), ("economic_sentiment", "level"),
                ("consumer_confidence", "level"), ("ppi", "yoy"), ("hicp_core", "level"), ("gdp", "yoy")]


def shade(z: float | None) -> str:
    """The cell's class: mid (within half a typical deviation of normal), hot1-3 above it, cool1-3 below."""
    if z is None or pd.isna(z):
        return "none"
    level = sum(abs(z) >= s for s in STEPS)
    return "mid" if level == 0 else f"{'hot' if z > 0 else 'cool'}{level}"


def _compact(v: float) -> str:
    """A reading in a cell: one decimal, none from 100 on, a typographic minus."""
    text = f"{abs(v):,.0f}" if abs(v) >= 100 else f"{abs(v):.1f}"
    return (MINUS + text) if v < 0 and float(text.replace(",", "")) != 0 else text


def _describe(z: float, hot: bool) -> str:
    return _(analytics._describe(z, hot))


def _score(z: float) -> str:
    return analytics._fmt_signed(z)


def _months(end: pd.Timestamp) -> list[dict]:
    months = pd.date_range(end - pd.DateOffset(months=MONTHS - 1), end, freq="MS")
    return [{"date": m, "mon": i18n.mon(m), "year": m.year if (i == 0 or m.month == 1) else None}
            for i, m in enumerate(months)]


def _component_rows(data: Data, components, hot: bool, months: list[pd.Timestamp]) -> list[dict]:
    rows = []
    for c in components:
        s = analytics._component_series(data, c)
        if s is None or len(s) < 24:
            continue
        centre, spread = analytics._norm(s)
        if not spread:
            continue
        z = (c.sign * (s - centre) / spread).clip(-Z_CLIP, Z_CLIP)
        ind = data.by_id[c.id]
        label = _(c.label)

        def cell(date, span):
            if date not in s.index:
                return {"span": span, "shade": "none", "text": "",
                        "title": _("{label}, {period}: not out yet").format(label=label, period=period_label(date, ind.freq))}
            row = {"component": c, "value": float(s[date]), "date": date, "freq": ind.freq}
            return {"span": span, "shade": shade(float(z[date])), "text": _compact(float(s[date])),
                    "title": _("{label}, {period}: {value}; score {score}, {describe}").format(
                        label=label, period=period_label(date, ind.freq), value=analytics._component_display(data, row),
                        score=_score(float(z[date])), describe=_describe(float(z[date]), hot))}

        if ind.freq == "Q":       # one cell for each quarter, across its months in the window
            quarters: dict[pd.Timestamp, int] = {}
            for m in months:
                q = m - pd.DateOffset(months=(m.month - 1) % 3)
                quarters[q] = quarters.get(q, 0) + 1
            cells = [cell(q, span) for q, span in quarters.items()]
        else:
            cells = [cell(m, 1) for m in months]
        rows.append({"label": label, "label_es": ind.label_es, "url": source_page(ind, data.by_id), "cells": cells})
    return rows


def heatmap(data: Data) -> dict | None:
    """The past twelve months of the composites' readings, shaded against their normal."""
    blocks = []
    for key, components, title, overall, hot in (
            ("activity", ACTIVITY, "Activity", "Activity, overall score", False),
            ("inflation", INFLATION, "Inflation", "Inflation, overall score", True)):
        comp = analytics.composite(data, components, key)
        if comp is not None and not comp["series"].empty:
            blocks.append((key, title, overall, hot, comp))
    if not blocks:
        return None
    end = max(comp["end"] for *_rest, comp in blocks)
    months = _months(end)
    dates = [m["date"] for m in months]
    out = []
    for key, title, overall, hot, comp in blocks:
        series = comp["series"]
        overall_cells = []
        for m in dates:
            z = series.get(m)
            if z is None or pd.isna(z):
                overall_cells.append({"span": 1, "shade": "none", "text": "", "title": ""})
                continue
            overall_cells.append({"span": 1, "shade": shade(float(z)), "text": _score(float(z)),
                                  "title": _("{label}, {period}: {score}, {describe}").format(
                                      label=_(overall), period=i18n.month_year(m), score=_score(float(z)),
                                      describe=_describe(float(z), hot))})
        out.append({"id": key, "title": _(title), "overall": {"label": _(overall), "cells": overall_cells},
                    "rows": _component_rows(data, ACTIVITY if key == "activity" else INFLATION, hot, dates)})
    return {"months": months, "blocks": out, "through": i18n.month_year(end)}


def _record_value(ind, transform: str, v: float) -> str:
    fmt, _decimals = _format(ind, transform)
    if transform == "level" and ind.unit == "thousands" and abs(v) >= 1000:     # 21,950k people: 21.95 million
        return _("{n} million").format(n=f"{v / 1000:.2f}")
    return fmt(v)


def records(data: Data, tiles: list[dict]) -> list[dict]:
    """The key figures at their highest or lowest in at least two years, longest first."""
    watched = [(t["id"], t["headline"]["transform"]) for t in tiles if t["headline"]] + RECORD_EXTRA
    out, seen = [], set()
    for ind_id, transform in watched:
        ind = data.by_id.get(ind_id)
        if ind is None or (ind_id, transform) in seen:
            continue
        seen.add((ind_id, transform))
        ts = headline_series(ind, data.store.load_series(ind_id), transform)
        if len(ts) < 3:
            continue
        found = extreme(ts, _format(ind, transform)[1])
        if not found:
            continue
        rising, since, _count = found
        start = since if since is not None else ts.index[0]
        years = (ts.index[-1] - start).days / 365.25
        if years < RECORD_YEARS:
            continue
        when = i18n.day_month_year(ts.index[-1]) if ind.freq == "D" else period_label(ts.index[-1], ind.freq)
        out.append({"id": ind_id, "label": i18n.pick(ind.label, ind.label_es), "value": _record_value(ind, transform, float(ts.iloc[-1])),
                    "when": when, "up": rising, "text": since_text(rising, since, ts, ind.freq),
                    "page": f"{ind.section}.html", "years": years if since is not None else 1000 + years})
    out.sort(key=lambda r: -r["years"])
    return out[:MAX_RECORDS]
