"""The tour of the site on the home page (batches L4 and L5): one full-width chapter per area, after the key indicators.

Each chapter has the area's name, a big figure with a sentence written from the data, two or three supporting facts,
links to the first sections of its page, and that page's signature chart, drawn here as SVG and HTML (no plotting
library): lines in a 1000 × 100 box stretched to fit, with their labels placed over it in %; stacked bars the same
way; a small treemap as HTML boxes in %. static/app.js marks a chapter "is-in" the first time it scrolls into view
and CSS draws its chart then (still for readers who ask for reduced motion, and with no script at all). Hovering
over a bar or a box gives its figures (its title).

A chapter whose data are missing is left out; the tour shows the rest.
"""

import math

import pandas as pd

from . import basket, i18n, transforms
from .i18n import _
from .snapshot import MINUS, fmt_change, fmt_value, period_label
from .tables import Data

VIEW = 1000           # the drawing box's width (its height is 100)
END_GAP = 18          # end labels are kept this far apart (% of the chart's height)


# ---------------------------------------------------------------- helpers

def _series(data: Data, ind_id: str, transform: str = "level") -> pd.Series | None:
    """The indicator as transformed, without gaps, or None."""
    if ind_id not in data.by_id:
        return None
    s = data.raw(ind_id)
    if s is None or s.dropna().empty:
        return None
    try:
        s = transforms.apply(transform, s.dropna(), data.by_id[ind_id].freq).dropna()
    except ValueError:
        return None
    return s if not s.empty else None


def _monthly(s: pd.Series, how: str = "mean") -> pd.Series:
    """A daily series as monthly averages (or month-end values), dated on the first of the month."""
    r = s.resample("MS")
    return (r.mean() if how == "mean" else r.last()).dropna()


def _quarterly(s: pd.Series) -> pd.Series:
    return s.resample("QS").mean().dropna()


def _value(snapshot: dict, ind_id: str, transform: str) -> dict | None:
    item = snapshot.get(ind_id) or {}
    return next((v for v in item.get("values", []) if v["transform"] == transform), None)


def _pct(v: float, decimals: int = 1) -> str:
    return fmt_value(v, "%", decimals)


def _signed_pp(v: float, decimals: int = 1) -> str:
    return fmt_change(v, "pp", decimals)


def _nice_step(span: float, target: int = 4) -> float:
    raw = span / max(target, 1)
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _ticks(lo: float, hi: float, fmt) -> tuple[float, float, list[dict]]:
    """A padded domain and 3 to 5 round ticks inside it, each with its label and its place down the box (%)."""
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad
    step = _nice_step(hi - lo)
    first = math.ceil(lo / step) * step
    ticks, v = [], first
    while v <= hi + 1e-9:
        ticks.append(round(v, 10))
        v += step
    y = lambda t: round((hi - t) / (hi - lo) * 100, 2)
    return lo, hi, [{"label": fmt(t), "y": y(t)} for t in ticks]


def _apart(ends: list[dict], gap: float = END_GAP) -> None:
    """Push end labels apart (down the box) so they don't overlap; each keeps "label_y"."""
    ends.sort(key=lambda e: e["y"])
    for e in ends:
        e["label_y"] = e["y"]
    for _round in range(3):
        for a, b in zip(ends, ends[1:]):
            if b["label_y"] - a["label_y"] < gap:
                mid = (a["label_y"] + b["label_y"]) / 2
                a["label_y"], b["label_y"] = mid - gap / 2, mid + gap / 2
    # inside the box, and still apart: pushed down from the top edge, then up from the bottom one
    pos = [min(97.0, max(3.0, e["label_y"])) for e in ends]
    for k in range(1, len(pos)):
        pos[k] = max(pos[k], pos[k - 1] + gap)
    if pos:
        pos[-1] = min(pos[-1], 97.0)
    for k in range(len(pos) - 2, -1, -1):
        pos[k] = min(pos[k], pos[k + 1] - gap)
    for e, y in zip(ends, pos):
        e["label_y"] = round(y, 2)


LABELS_WIDE, LABELS_NARROW = 7, 4    # at most this many year labels under a chapter's chart on a laptop, on a phone


def _years(start: pd.Timestamp, end: pd.Timestamp, x) -> list[dict]:
    """Year labels at each January: "wide" ones show on a laptop, "narrow" ones on a phone too (every few years,
    counted back from the last, so the latest year is always named)."""
    years = [y for y in range(start.year + (start.month > 1), end.year + 1)]
    wide = max(1, math.ceil(len(years) / LABELS_WIDE))
    narrow = max(1, math.ceil(len(years) / LABELS_NARROW))
    last = years[-1] if years else 0
    return [{"label": y, "x": x(pd.Timestamp(y, 1, 1)), "wide": (last - y) % wide == 0, "narrow": (last - y) % narrow == 0}
            for y in years]


# ---------------------------------------------------------------- charts

def line_chart(lines: list[dict], unit: str, decimals: int, fmt=None, zero: bool = False, title: str = "",
               subtitle: str = "", source: str = "") -> dict | None:
    """Lines over time. Each line: name, s (a series by date), slot (the palette's colour 1-7, or "ink"), and
    optionally dashed (a projection), step (a rate that moves in steps) and end (the text at its end)."""
    lines = [ln for ln in lines if ln.get("s") is not None and len(ln["s"]) >= 2]
    if not lines:
        return None
    fmt = fmt or (lambda v: fmt_value(v, unit, decimals))
    t0 = min(ln["s"].index[0] for ln in lines)
    t1 = max(ln["s"].index[-1] for ln in lines)
    span = (t1 - t0).total_seconds() or 1.0
    lo = min(float(ln["s"].min()) for ln in lines)
    hi = max(float(ln["s"].max()) for ln in lines)
    if zero:
        lo, hi = min(lo, 0.0), max(hi, 0.0)
    lo, hi, ticks = _ticks(lo, hi, lambda t: fmt_value(t, unit, 0 if abs(t - round(t)) < 1e-9 else decimals))
    xf = lambda t: round((t - t0).total_seconds() / span * VIEW, 1)
    yf = lambda v: round((hi - v) / (hi - lo) * 100, 2)
    out, ends = [], []
    for ln in lines:
        s = ln["s"]
        pts = []
        prev = None
        for t, v in s.items():
            x, y = xf(t), yf(float(v))
            if ln.get("step") and prev is not None:
                pts.append(f"{x},{prev}")
            pts.append(f"{x},{y}")
            prev = y
        last_v = float(s.iloc[-1])
        out.append({"name": ln["name"], "slot": ln.get("slot", 1), "dashed": bool(ln.get("dashed")),
                    "points": " ".join(pts)})
        if ln.get("end") is not False:
            ends.append({"name": ln["name"], "slot": ln.get("slot", 1), "x": round(xf(s.index[-1]) / 10, 2),
                         "y": yf(last_v), "text": ln.get("end") or fmt(last_v)})
    _apart(ends)
    return {"kind": "lines", "lines": out, "ends": ends, "ticks": ticks,
            "zero": yf(0.0) if lo < 0 < hi else None,
            "years": _years(t0, t1, lambda t: round(xf(t) / 10, 2)),
            "title": title, "subtitle": subtitle, "source": source}


def bar_chart(periods: list[pd.Timestamp], stacks: list[dict], freq: str, unit: str, decimals: int,
              line: dict | None = None, title: str = "", subtitle: str = "", source: str = "") -> dict | None:
    """Stacked bars, one per period (positive parts up from zero, negative down), with an optional line through
    the bars' centres (the total). Each stack: name, values (one per period, None for none), slot."""
    if not periods or not stacks:
        return None
    n = len(periods)
    tops = [sum(max(0.0, s["values"][k] or 0.0) for s in stacks) for k in range(n)]
    bottoms = [sum(min(0.0, s["values"][k] or 0.0) for s in stacks) for k in range(n)]
    extra = [v for v in (line["values"] if line else []) if v is not None]
    lo, hi, ticks = _ticks(min(bottoms + extra + [0.0]), max(tops + extra + [0.0]),
                           lambda t: fmt_value(t, unit, 0 if abs(t - round(t)) < 1e-9 else decimals))
    yf = lambda v: (hi - v) / (hi - lo) * 100
    slot_w = VIEW / n
    bar_w = slot_w * 0.62
    rects = []
    for k, when in enumerate(periods):
        up, down = 0.0, 0.0
        x = k * slot_w + (slot_w - bar_w) / 2
        for s in stacks:
            v = s["values"][k]
            if v is None or v == 0:
                continue
            if v > 0:
                y0, y1 = yf(up + v), yf(up)
                up += v
            else:
                y0, y1 = yf(down), yf(down + v)
                down += v
            rects.append({"x": round(x, 1), "y": round(y0, 2), "w": round(bar_w, 1), "h": round(y1 - y0, 2),
                          "slot": s["slot"], "neg": v < 0, "i": k,
                          "title": f"{s['name']}, {period_label(when, freq)}: {fmt_change(v, unit, decimals)}"})
    points = None
    if line:
        points = " ".join(f"{round(k * slot_w + slot_w / 2, 1)},{round(yf(v), 2)}"
                          for k, v in enumerate(line["values"]) if v is not None)
    labels = []
    for k, when in enumerate(periods):
        if freq == "Q" and when.month == 1 or freq == "A":
            labels.append({"label": when.year, "x": round((k * slot_w + slot_w / 2) / 10, 2), "wide": True,
                           "narrow": True})
    legend = [{"name": s["name"], "slot": s["slot"]} for s in stacks] + ([{"name": line["name"], "slot": "ink", "line": True}] if line else [])
    return {"kind": "bars", "rects": rects, "line": points, "ticks": ticks, "zero": round(yf(0.0), 2),
            "years": labels, "legend": legend, "title": title, "subtitle": subtitle, "source": source}


def _worst(row: list[float], side: float) -> float:
    s = sum(row)
    return max(max(side * side * r / (s * s), (s * s) / (side * side * r)) for r in row)


def squarify(values: list[float], x: float, y: float, w: float, h: float) -> list[tuple[float, float, float, float]]:
    """Rectangles for values (largest first), laid out to keep them close to square (Bruls, Huizing and van Wijk)."""
    total = sum(values)
    areas = [v / total * w * h for v in values]
    rects = []
    while areas:
        side = min(w, h)
        row, k = [areas[0]], 1
        while k < len(areas) and _worst(row + [areas[k]], side) <= _worst(row, side):
            row.append(areas[k])
            k += 1
        s = sum(row)
        if w >= h:                   # a column down the left side
            rw, yy = s / h, y
            for a in row:
                rects.append((x, yy, rw, a / rw))
                yy += a / rw
            x, w = x + rw, w - rw
        else:                        # a row across the top
            rh, xx = s / w, x
            for a in row:
                rects.append((xx, y, a / rh, rh))
                xx += a / rh
            y, h = y + rh, h - rh
        areas = areas[k:]
    return rects


# ---------------------------------------------------------------- the chapters (L4)

def _gdp(data: Data, snap: dict) -> dict | None:
    yoy, qoq = _value(snap, "gdp", "yoy"), _value(snap, "gdp", "pop")
    dom, ext = _series(data, "contrib_domestic_yy"), _series(data, "contrib_external_yy")
    level = _series(data, "gdp")
    if not yoy or dom is None or ext is None:
        return None
    periods = [t for t in dom.index if t in ext.index][-16:]
    growth = _series(data, "gdp", "yoy")
    chart = bar_chart(periods, [{"name": _("Domestic demand"), "values": [float(dom[t]) for t in periods], "slot": 1},
                                {"name": _("Rest of the world"), "values": [float(ext[t]) for t in periods], "slot": 2}],
                      "Q", "pp", 1, line={"name": _("GDP growth"), "values": [float(growth[t]) if growth is not None and t in growth.index else None for t in periods]},
                      title=_("What drives growth"),
                      subtitle=_("Contributions to real GDP growth on a year earlier, percentage points"), source="INE")
    last = periods[-1]
    facts = []
    if qoq:
        facts.append(_("{value} on the quarter").format(value=qoq["display"]))
    if level is not None and pd.Timestamp("2019-10-01") in level.index:
        since = (float(level.iloc[-1]) / float(level[pd.Timestamp("2019-10-01")]) - 1) * 100
        facts.append(_("{change} since the end of 2019, before Covid").format(change=fmt_change(since, "%", 1)))
    return {"id": "gdp", "big": yoy["display"], "big_label": _("GDP growth, {period}, on a year earlier").format(period=yoy["period"]),
            "sentence": _("Domestic demand added {domestic} points to growth in {period} and the rest of the world "
                          "{external}.").format(domestic=_signed_pp(float(dom[last])).replace(" pp", ""),
                                                 external=_signed_pp(float(ext[last])).replace(" pp", ""),
                                                 period=period_label(last, "Q")),
            "facts": facts, "chart": chart}


def _labour(data: Data, snap: dict) -> dict | None:
    regs = _series(data, "afiliados")
    year = _value(snap, "afiliados", "diff_yoy")
    if regs is None:
        return None
    millions = regs / 1000
    latest = float(millions.iloc[-1])
    record = float(regs.iloc[-1]) >= float(regs.max()) - 1e-9
    sentence = (_("Social Security registrations reached a record in {month}, {change} on a year earlier.") if record else
                _("Social Security registrations in {month}, {change} on a year earlier.")).format(
        month=i18n.month_year(regs.index[-1]), change=year["display"] if year else "")
    facts = []
    unemp = _value(snap, "unemployment_epa", "level")
    if unemp:
        facts.append(_("Unemployment rate {value} ({period}, EPA)").format(value=unemp["display"], period=unemp["period"]))
    emp = _series(data, "employment_epa")
    if emp is not None:
        facts.append(_("{value} million people in work ({period}, EPA)").format(
            value=f"{float(emp.iloc[-1]) / 1000:.2f}", period=period_label(emp.index[-1], "Q")))
    chart = line_chart([{"name": _("Registrations"), "s": millions[millions.index >= "2008-01-01"], "slot": 1,
                         "end": f"{latest:.2f} {_('million')}"}], "", 1,
                       title=_("Social Security registrations"), subtitle=_("Monthly average, millions, since 2008"),
                       source=_("Seguridad Social"))
    return {"id": "labour", "big": f"{latest:.2f}", "big_unit": _("million"),
            "big_label": _("Social Security registrations, {month}").format(month=i18n.month_year(regs.index[-1])),
            "sentence": sentence, "facts": facts, "chart": chart}


def _wages(data: Data, snap: dict) -> dict | None:
    pay = _series(data, "wage_cost", "yoy")
    cpi = _series(data, "cpi")
    if pay is None or cpi is None:
        return None
    cpi_q = _quarterly(cpi)
    last = pay.index[-1]
    prices = float(cpi_q[last]) if last in cpi_q.index else None
    facts = []
    real = _series(data, "real_wage", "yoy")
    if real is not None:
        facts.append(_("Real wage cost per worker {change} on a year earlier ({period})").format(
            change=fmt_change(float(real.iloc[-1]), "%", 1), period=period_label(real.index[-1], "Q")))
    agreed = _series(data, "wage_agreements")
    if agreed is not None:
        facts.append(_("Pay rises agreed in collective agreements: {value} ({month})").format(
            value=_pct(float(agreed.iloc[-1]), 2), month=i18n.month_year(agreed.index[-1])))
    start = pd.Timestamp("2022-01-01")
    chart = line_chart([{"name": _("Wage cost per worker"), "s": pay[pay.index >= start], "slot": 1},
                        {"name": _("Consumer prices"), "s": cpi_q[cpi_q.index >= start], "slot": 2}], "%", 1, zero=True,
                       title=_("Pay against prices"), subtitle=_("% change on a year earlier, quarterly, since 2022"),
                       source="INE")
    sentence = (_("Wage cost per worker rose {pay} on a year earlier in {period}, against consumer prices up {prices}.")
                .format(pay=_pct(float(pay.iloc[-1])), period=period_label(last, "Q"),
                        prices=_pct(prices) if prices is not None else "–"))
    return {"id": "wages", "big": fmt_change(float(pay.iloc[-1]), "%", 1),
            "big_label": _("Wage cost per worker, {period}, on a year earlier").format(period=period_label(last, "Q")),
            "sentence": sentence, "facts": facts, "chart": chart}


def _inflation(data: Data, snap: dict) -> dict | None:
    cpi, core, hicp = _value(snap, "cpi", "level"), _value(snap, "core_cpi", "level"), _value(snap, "hicp", "level")
    raw = data.store.load_json(basket.STORE, None)
    if not cpi or not raw or not raw.get("months"):
        return None
    k = len(raw["months"]) - 1
    year = max(raw["weights"], key=int)
    weights = raw["weights"][year]
    cats = []
    for code, full in raw["categories"].items():
        items = [i for i in weights if i.startswith(code)]
        w = sum(weights[i] for i in items)
        rated = [(weights[i], raw["rates"][i][k]) for i in items if i in raw["rates"] and raw["rates"][i][k] is not None]
        if not w or not rated:
            continue
        rate = sum(wi * r for wi, r in rated) / sum(wi for wi, _r in rated)
        contrib = sum(raw["contributions"][i][k] or 0.0 for i in items if i in raw["contributions"])
        cats.append({"code": code, "name": _(basket.SHORT.get(code, full)), "weight": w, "rate": rate, "contrib": contrib})
    if not cats:
        return None
    cats.sort(key=lambda c: -c["weight"])
    rects = squarify([c["weight"] for c in cats], 0, 0, 160, 100)
    total = sum(c["weight"] for c in cats)
    target = basket.TARGET
    boxes = []
    for i, (c, (x, y, w, h)) in enumerate(zip(cats, rects)):
        gap = c["rate"] - target
        size = sum(abs(gap) >= s for s in basket.STEPS)
        shade = "mid" if size == 0 else ("hot" if gap > 0 else "cool") + str(size)
        boxes.append({"name": c["name"], "rate": _pct(c["rate"]), "shade": shade, "i": i,
                      "left": round(x / 1.6, 2), "top": round(y, 2), "width": round(w / 1.6, 2), "height": round(h, 2),
                      "small": w * h < 160 * 100 * 0.03, "tiny": w * h < 160 * 100 * 0.012,
                      "title": _("{name}: {share} of the basket, prices {rate} on a year earlier, adding {points} "
                                 "points").format(name=c["name"], share=_pct(c["weight"] / total * 100),
                                                  rate=_pct(c["rate"]), points=f"{c['contrib']:.2f}")})
    month = pd.Timestamp(raw["months"][-1] + "-01")
    top = sorted(cats, key=lambda c: -c["contrib"])[:2]
    facts = []
    if core:
        facts.append(_("Core inflation {value}").format(value=core["display"]))
    if hicp:
        facts.append(_("Harmonised index (HICP) {value}").format(value=hicp["display"]))
    chart = {"kind": "treemap", "boxes": boxes, "title": _("The basket"),
             "subtitle": _("Each category sized by its weight in the {year} basket and shaded by its prices' change "
                           "on a year earlier, {month}, around the ECB's 2% target").format(year=year, month=i18n.month_year(month)),
             "source": "Eurostat",
             "legend": {"below": _("Below 2%"), "above": _("Above 2%")}}
    return {"id": "inflation", "big": cpi["display"],
            "big_label": _("CPI inflation, {period}").format(period=cpi["period"]),
            "sentence": _("{first} adds the most to inflation, {a} points, then {second}, {b}.").format(
                first=top[0]["name"], a=f"{top[0]['contrib']:.1f}", second=top[1]["name"].lower(),
                b=f"{top[1]['contrib']:.1f}") if len(top) > 1 else "",
            "facts": facts, "chart": chart}


def _financial(data: Data, snap: dict) -> dict | None:
    es, de = _series(data, "es_10y"), _series(data, "de_10y")
    if es is None or de is None:
        return None
    start = pd.Timestamp("2019-01-01")
    es_m, de_m = _monthly(es[es.index >= start]), _monthly(de[de.index >= start])
    day = es.index[-1]
    gap = (float(es.iloc[-1]) - float(de.asof(day))) * 100
    facts = []
    eur = _value(snap, "euribor_12m", "level")
    if eur:
        facts.append(_("12-month Euribor {value} ({period})").format(value=eur["display"], period=eur["period"]))
    ibex = snap.get("ibex35") or {}
    if ibex.get("headline"):
        facts.append(_("IBEX 35 {value} ({period}), {change} this year").format(
            value=ibex["headline"]["display"], period=ibex["headline"]["period"], change=ibex.get("subline", "").split(" ")[0]))
    chart = line_chart([{"name": _("Spain"), "s": es_m, "slot": 1}, {"name": _("Germany"), "s": de_m, "slot": "ink"}],
                       "%", 2, zero=True, title=_("Ten-year government bond yields"),
                       subtitle=_("Monthly average, %, since 2019; the gap between them is the prima de riesgo"),
                       source=_("Banco de España; Bundesbank"))
    return {"id": "financial", "big": _pct(float(es.iloc[-1]), 2),
            "big_label": _("Spain's 10-year bond yield, {day}").format(day=i18n.day_month_year(day)),
            "sentence": _("{bp} basis points above Germany's: the prima de riesgo.").format(bp=f"{gap:.0f}"),
            "facts": facts, "chart": chart}


def _ecb(data: Data, snap: dict) -> dict | None:
    rate, ea = _series(data, "ecb_deposit_rate"), _series(data, "hicp_euro_area")
    if rate is None or ea is None:
        return None
    changes = rate[rate.diff().fillna(0) != 0]
    start = pd.Timestamp("2019-01-01")
    monthly = _monthly(rate[rate.index >= start], how="last")
    monthly.loc[rate.index[-1].replace(day=1)] = float(rate.iloc[-1])
    sentence = ""
    if not changes.empty:
        when = changes.index[-1]
        before = float(rate[rate.index < when].iloc[-1])
        move = float(changes.iloc[-1]) - before
        sentence = (_("Raised by {n} points on {day}.") if move > 0 else _("Cut by {n} points on {day}.")).format(
            n=f"{abs(move):.2f}", day=i18n.day_month_year(when))
    facts = [_("Euro-area inflation {value} ({month})").format(value=_pct(float(ea.iloc[-1])), month=i18n.month_year(ea.index[-1]))]
    hicp = _value(snap, "hicp", "level")
    if hicp:
        facts.append(_("Spain's harmonised inflation {value} ({period})").format(value=hicp["display"], period=hicp["period"]))
    chart = line_chart([{"name": _("Deposit rate"), "s": monthly.sort_index(), "slot": 1, "step": True},
                        {"name": _("Euro-area inflation"), "s": ea[ea.index >= start], "slot": 2}], "%", 2, zero=True,
                       title=_("The ECB's rate and euro-area inflation"), subtitle=_("%, monthly, since 2019"),
                       source=_("ECB; Eurostat"))
    return {"id": "ecb", "big": _pct(float(rate.iloc[-1]), 2), "big_label": _("ECB deposit rate"),
            "sentence": sentence, "facts": facts, "chart": chart}


def _fiscal(data: Data, snap: dict) -> dict | None:
    debt_q, debt_a = _series(data, "government_debt"), _series(data, "debt_annual")
    if debt_q is None or debt_a is None:
        return None
    from . import fiscal
    path = None
    try:
        rows = fiscal.baseline(fiscal.load())
        last_year = debt_a.index[-1].year
        path = pd.Series({pd.Timestamp(y, 1, 1): r["debt"] for y, r in rows.items()
                          if r["source"] == "Commission" and y >= last_year})
        path[pd.Timestamp(last_year, 1, 1)] = float(debt_a.iloc[-1])
        path = path.sort_index()
    except (OSError, KeyError, ValueError):
        path = None
    facts = []
    deficit, interest = _series(data, "deficit_annual"), _series(data, "interest_annual")
    if deficit is not None:
        facts.append(_("Deficit {value} of GDP in {year}").format(value=_pct(-float(deficit.iloc[-1])), year=deficit.index[-1].year))
    if interest is not None:
        facts.append(_("Interest on the debt {value} of GDP in {year}").format(value=_pct(float(interest.iloc[-1])), year=interest.index[-1].year))
    hist = debt_a[debt_a.index >= "2000-01-01"]
    lines = [{"name": _("Debt"), "s": hist, "slot": 1, "end": False}]
    sentence = ""
    if path is not None and len(path) > 1:
        lines.append({"name": _("Commission's projection"), "s": path, "slot": 1, "dashed": True,
                      "end": _pct(float(path.iloc[-1]), 0) + f" ({path.index[-1].year})"})
        sentence = _("The European Commission's baseline has it at {value} in {year} without new measures.").format(
            value=_pct(float(path.iloc[-1]), 0), year=path.index[-1].year)
    chart = line_chart(lines, "%", 0, title=_("Government debt"),
                       subtitle=_("% of GDP at year end since 2000, and the Commission's projection"),
                       source=_("Eurostat; European Commission"))
    return {"id": "fiscal", "big": _pct(float(debt_q.iloc[-1])), "big_unit": _("of GDP"),
            "big_label": _("Government debt, {period}").format(period=period_label(debt_q.index[-1], "Q")),
            "sentence": sentence, "facts": facts, "chart": chart}


CHAPTERS = [("gdp", _gdp), ("labour", _labour), ("wages", _wages), ("inflation", _inflation),
            ("financial", _financial), ("ecb", _ecb), ("fiscal", _fiscal)]


def chapters(data: Data, snapshot: dict, sections: dict, links: dict) -> list[dict]:
    """The tour: each area's chapter, numbered, with its page, title and section links. `sections` maps a section
    to its (title, intro) and `links` to its [(href, title)]."""
    out = []
    for key, build in CHAPTERS:
        try:
            ch = build(data, snapshot)
        except (KeyError, ValueError, IndexError, TypeError, ZeroDivisionError):
            ch = None
        if not ch or not ch.get("chart"):
            continue
        title = _(sections[key][0]) if key in sections else key
        ch.update({"n": f"{len(out) + 1:02d}", "area": title, "page": f"{key}.html",
                   "explore": _("Explore {area}").format(area=title), "links": links.get(key, [])[:4]})
        out.append(ch)
    return out
