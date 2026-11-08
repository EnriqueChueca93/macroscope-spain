"""Macroscope originals: calculations built on the official data, shown on the Analysis page.

    Composites  how activity and inflation compare with their own history since 2013
    Nowcast     a bridge-equation estimate of this quarter's GDP growth, with its track record
    Decomposition  the change in Spain's 10-year yield split into the Bund and the prima de riesgo
    Taylor rules   the policy rate a simple rule suggests for the euro area and for Spain

All of these are Macroscope estimates, not official figures, and the page says how each
is made. Results are cached on the build's Data object, since several blocks share them.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.filters.hp_filter import hpfilter

from . import i18n, seasonal, transforms
from .charts import localise, source_page
from .i18n import _
from .snapshot import MINUS, fmt_change, fmt_value, period_label
from .tables import DASH, Data

HISTORY_START = pd.Timestamp("2013-01-01")
COVID = (2020, 2021)     # left out of the norms and the nowcast estimation: too extreme to describe "normal"
Z_CLIP = 3.0


def _cached(data: Data, key: str, compute):
    if key not in data.cache:
        data.cache[key] = compute()
    return data.cache[key]


def _fmt_signed(v: float | None, decimals: int = 1, unit: str = "") -> str:
    if v is None or pd.isna(v):
        return DASH
    text = f"{abs(v):.{decimals}f}"
    if float(text) == 0:
        return text + unit
    return ("+" if v > 0 else MINUS) + text + unit


def _months_between(a: pd.Timestamp, b: pd.Timestamp) -> int:
    return (b.year - a.year) * 12 + b.month - a.month


# ---------------------------------------------------------------- composites

@dataclass(frozen=True)
class Component:
    id: str
    label: str
    transform: str = "level"
    smooth: int = 1          # rolling window, in periods
    how: str = "mean"        # how the window combines: mean, or sum (a 3-month change from monthly changes)
    sign: int = 1            # -1 when a higher reading means a weaker economy (unemployment)


ACTIVITY = [
    Component("afiliados", "Registrations, monthly change, SA (3-mo avg.)", "sa_diff", smooth=3),
    Component("unemployment_monthly", "Unemployment rate, change over 3 months", "diff", smooth=3, how="sum", sign=-1),
    Component("industrial_production", "Industrial production, y/y", "yoy"),
    Component("retail_sales", "Retail sales, y/y", "yoy"),
    Component("car_sales", "Car sales, y/y (3-mo avg.)", "yoy", smooth=3),
    Component("electricity_demand_monthly", "Electricity demand, y/y (3-mo avg.)", "yoy", smooth=3),
    Component("tourist_arrivals", "Tourists, y/y (3-mo avg.)", "yoy", smooth=3),
    Component("economic_sentiment", "Economic sentiment"),
    Component("consumer_confidence", "Consumer confidence"),
    Component("gdp", "Real GDP, q/q", "pop"),
]
INFLATION = [
    Component("hicp", "HICP inflation"),
    Component("hicp_core", "Core HICP inflation"),
    Component("cpi_services_index", "Services inflation", "yoy"),
    Component("core_cpi_index", "Core CPI, 3-mo annualised, SA", "sa_ann3m"),
    Component("ppi", "Producer prices, y/y", "yoy"),
    Component("price_expectations", "Consumers' price expectations"),
    Component("wage_cost", "Wage cost per worker, y/y", "yoy"),
]


def _component_series(data: Data, c: Component, smooth: bool = True) -> pd.Series | None:
    raw = data.store.load_series(c.id)
    if raw is None or c.id not in data.by_id:
        return None
    freq = data.by_id[c.id].freq
    try:
        s = transforms.apply(c.transform, raw, freq)
    except ValueError:
        return None
    if smooth and c.smooth > 1:
        window = s.rolling(c.smooth, min_periods=c.smooth)
        s = window.sum() if c.how == "sum" else window.mean()
    return s.dropna()


def _norm(s: pd.Series) -> tuple[float, float]:
    """Robust centre and spread of a series' history (median and scaled MAD, 2013 on, Covid years out)."""
    hist = s[(s.index >= HISTORY_START) & ~s.index.year.isin(COVID)]
    centre = float(hist.median())
    spread = float(1.4826 * (hist - centre).abs().median()) or float(hist.std())
    return centre, spread


def _monthly(s: pd.Series, freq: str) -> pd.Series:
    """Quarterly readings are placed on the last month of their quarter."""
    if freq == "Q":
        s = s.copy()
        s.index = s.index + pd.DateOffset(months=2)
    return s


def weighted_by_age(scores: dict[str, pd.Series], end: pd.Timestamp) -> pd.Series:
    """Monthly weighted average of several monthly score series, from 2013 to ``end``.

    At each month every series contributes its newest reading so far, at full weight in its
    own month and a quarter less for each month it ages; after three months it drops out.
    """
    months = pd.date_range(HISTORY_START, end, freq="MS")
    weighted = pd.Series(0.0, index=months)
    weights = pd.Series(0.0, index=months)
    for z in scores.values():
        z = z.groupby(z.index).last()
        # At each month: the newest reading so far, and how many months old it is.
        value = z.reindex(months, method="ffill")
        seen = pd.Series(z.index, index=z.index).reindex(months, method="ffill")
        age = pd.Series([_months_between(s, m) if pd.notna(s) else 99 for s, m in zip(seen, months)], index=months)
        w = (1 - age / 4).clip(lower=0)
        use = value.notna() & (w > 0)
        weighted[use] += w[use] * value[use]
        weights[use] += w[use]
    return (weighted / weights.replace(0, np.nan)).dropna()


def composite(data: Data, components: list[Component], key: str) -> dict | None:
    """z-scores of each component against its own history, and their weighted average by month
    (see weighted_by_age: the latest value leans on the newest data)."""
    def compute():
        rows, zs = [], {}
        for c in components:
            s = _component_series(data, c)
            if s is None or len(s) < 24:
                continue
            centre, spread = _norm(s)
            if not spread:
                continue
            z = (c.sign * (s - centre) / spread).clip(-Z_CLIP, Z_CLIP)
            freq = data.by_id[c.id].freq
            zs[c.id] = _monthly(z, freq)
            rows.append({"component": c, "value": float(s.iloc[-1]), "date": s.index[-1], "freq": freq,
                         "z": float(z.iloc[-1])})
        if not zs:
            return None
        end = max(z.index[-1] for z in zs.values())
        series = weighted_by_age(zs, end)
        for row in rows:
            row["age"] = _months_between(row["date"] + pd.DateOffset(months=2 if row["freq"] == "Q" else 0), end)
        return {"series": series, "rows": rows, "end": end}

    return _cached(data, f"composite:{key}", compute)


def _describe(z: float, hot: bool) -> str:
    if z >= 0.5:
        return "hotter than normal" if hot else "stronger than normal"
    if z <= -0.5:
        return "cooler than normal" if hot else "weaker than normal"
    return "close to normal"


def composite_facts(data: Data) -> list[dict]:
    facts = []
    for key, comps, label, hot in (("activity", ACTIVITY, "Activity vs history", False),
                                   ("inflation", INFLATION, "Inflation vs history", True)):
        c = composite(data, comps, key)
        if c is None or c["series"].empty:
            continue
        s = c["series"]
        z = float(s.iloc[-1])
        prev = s.asof(s.index[-1] - pd.DateOffset(months=3))
        trend = "" if pd.isna(prev) else _("; {value} three months earlier").format(value=_fmt_signed(float(prev)))
        facts.append({"label": _(label), "value": _fmt_signed(z),
                      "sub": f"{_(_describe(z, hot))}, {i18n.month_year(s.index[-1])}{trend}"})
    return facts


def _component_display(data: Data, row: dict) -> str:
    c, v = row["component"], row["value"]
    ind = data.by_id[c.id]
    if c.transform in transforms.PERCENT_TRANSFORMS:
        return fmt_value(v, "%", 1)
    if c.transform in transforms.DIFF_TRANSFORMS:
        unit = "pp" if ind.unit == "%" else ind.unit
        return fmt_change(v, unit, 1 if unit == "pp" else ind.decimals)
    return fmt_value(v, ind.unit, ind.decimals)


def composite_table(data: Data, key: str) -> dict | None:
    comps, title = {"activity": (ACTIVITY, "Activity"), "inflation": (INFLATION, "Inflation")}[key]
    c = composite(data, comps, key)
    if c is None:
        return None
    rows = []
    for row in c["rows"]:
        ind = data.by_id[row["component"].id]
        weight = max(0.0, 1 - row["age"] / 4)
        rows.append({"heading": False, "label": _(row["component"].label), "label_es": ind.label_es, "indent": 0,
                     "period_note": period_label(row["date"], row["freq"]), "url": source_page(ind, data.by_id),
                     "cells": [_component_display(data, row), _fmt_signed(row["z"]), f"{weight:.2f}" if weight else "–"]})
    end = period_label(c["end"], "M")
    return {"title": _(title), "caption": _("Latest readings and their z-scores · composite for {month}").format(month=end),
            "through": end, "columns": [_("Latest"), _("z-score"), _("Weight")], "rows": rows,
            "note": _("A z-score of +1 means one typical deviation above the 2013–present norm (Covid years "
                      "left out). Weights fall by a quarter for each month a reading is older than the newest data.")}


def composite_chart(data: Data) -> dict | None:
    series = []
    for key, comps, name in (("activity", ACTIVITY, "Activity"), ("inflation", INFLATION, "Inflation")):
        c = composite(data, comps, key)
        if c is not None:
            s = c["series"].round(3)
            series.append({"name": name, "x": [d.strftime("%Y-%m-%d") for d in s.index], "y": s.tolist()})
    if not series:
        return None
    return {"id": "composites", "title": "Activity and inflation against their history",
            "subtitle": "Weighted average of z-scores, monthly; 0 = the 2013–present norm",
            "kind": "line", "unit": "", "decimals": 2, "signed": True, "freq": "M", "series": series,
            "ref_lines": [], "source": _("Macroscope calculation from INE, Eurostat, Seguridad Social, Red Eléctrica")}


# ---------------------------------------------------------------- GDP nowcast

@dataclass(frozen=True)
class NowcastInput:
    id: str
    label: str
    kind: str        # "growth": q/q % change of the quarterly average; "level": quarterly average minus 100
    adjust: bool = False


# Chosen from a few candidates (adding retail sales or economic sentiment made the track
# record worse), together with the previous quarter's GDP growth.
NOWCAST_INPUTS = [
    NowcastInput("afiliados", "Social Security registrations (SA)", "growth", adjust=True),
    NowcastInput("industrial_production", "Industrial production", "growth"),
]


def _ar1_extend(s: pd.Series, end: pd.Timestamp, growth: bool) -> pd.Series:
    """Extend a monthly series to `end` with an AR(1) on its monthly log changes (or on its level)."""
    s = s.dropna().asfreq("MS")
    if s.index[-1] >= end:
        return s
    y = np.log(s).diff() if growth else s
    fit = y[(y.index >= HISTORY_START) & ~y.index.year.isin(COVID)].dropna()
    x0, x1 = fit.shift(1).dropna(), fit.iloc[1:]
    beta = np.polyfit(x0.to_numpy(), x1.to_numpy(), 1)
    last, level = float(y.iloc[-1]), float(s.iloc[-1])
    out = s.copy()
    for d in pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), end, freq="MS"):
        last = beta[0] * last + beta[1]
        level = level * np.exp(last) if growth else last
        out[d] = level
    return out


def _quarterly_regressor(monthly: pd.Series, inp: NowcastInput) -> pd.Series:
    q = monthly.resample("QS").mean()
    counts = monthly.resample("QS").count()
    q = q[counts == 3]
    return (q / q.shift(1) - 1) * 100 if inp.kind == "growth" else q - 100


def nowcast(data: Data) -> dict | None:
    def compute():
        gdp_raw = data.store.load_series("gdp")
        if gdp_raw is None:
            return None
        gdp = transforms.apply("pop", gdp_raw, "Q").dropna()
        target_q = gdp.index[-1] + pd.DateOffset(months=3)
        target_end = target_q + pd.DateOffset(months=2)
        regs, coverage = {}, []
        for inp in NOWCAST_INPUTS:
            raw = data.store.load_series(inp.id)
            if raw is None:
                return None
            monthly = raw.sort_index()
            if inp.adjust:
                try:
                    monthly = seasonal.adjust(monthly, "M")
                except ValueError:
                    return None
            actual = monthly[(monthly.index >= target_q) & (monthly.index <= target_end)]
            coverage.append({"input": inp, "months": len(actual), "last": monthly.index[-1]})
            regs[inp.id] = _quarterly_regressor(_ar1_extend(monthly, target_end, inp.kind == "growth"), inp)
        regs["gdp_lag"] = gdp.shift(1).reindex(gdp.index.append(pd.DatetimeIndex([target_q])))
        regs["gdp_lag"][target_q] = float(gdp.iloc[-1])
        X = pd.DataFrame(regs).dropna()
        sample = X.index.intersection(gdp.index)
        sample = sample[(sample >= HISTORY_START + pd.DateOffset(months=3)) & ~sample.year.isin(COVID)]
        if len(sample) < 20 or target_q not in X.index:
            return None

        def fit_predict(train, row):
            A = np.column_stack([np.ones(len(train)), X.loc[train].to_numpy()])
            coef, *_rest = np.linalg.lstsq(A, gdp.loc[train].to_numpy(), rcond=None)
            return float(coef[0] + X.loc[row].to_numpy() @ coef[1:])

        value = fit_predict(sample, target_q)
        # Track record: each quarter since 2023 predicted from a model fitted on earlier quarters only.
        backtest = []
        for q in sample[sample >= pd.Timestamp("2023-01-01")]:
            train = sample[sample < q]
            if len(train) >= 20:
                backtest.append((q, fit_predict(train, q), float(gdp[q]), float(gdp.shift(1)[q])))
        errors = np.array([p - a for _, p, a, _ in backtest])
        naive = np.array([n - a for _, _, a, n in backtest])
        mean = np.array([float(gdp[sample[sample < q]].mean()) - a for q, _, a, _ in backtest])
        rmse = float(np.sqrt(np.mean(errors ** 2))) if len(errors) else None
        return {"quarter": target_q, "value": value, "rmse": rmse, "coverage": coverage, "backtest": backtest,
                "naive_rmse": float(np.sqrt(np.mean(naive ** 2))) if len(naive) else None,
                "mean_rmse": float(np.sqrt(np.mean(mean ** 2))) if len(mean) else None,
                "mae": float(np.mean(np.abs(errors))) if len(errors) else None,
                "last_gdp": (gdp.index[-1], float(gdp.iloc[-1]))}

    return _cached(data, "nowcast", compute)


def nowcast_facts(data: Data) -> list[dict]:
    n = nowcast(data)
    if n is None:
        return []
    q = period_label(n["quarter"], "Q")
    band = _("± {error} pp typical error").format(error=f"{n['rmse']:.1f}") if n["rmse"] is not None else ""
    last_q, last_v = n["last_gdp"]
    months = sum(c["months"] for c in n["coverage"])
    return [
        {"label": _("GDP nowcast (placeholder), {q}").format(q=q), "value": _fmt_signed(n["value"], 1, "%"),
         "sub": f"{i18n.figures('q/q')}; {band}"},
        {"label": _("Latest official, {q}").format(q=period_label(last_q, 'Q')), "value": _fmt_signed(last_v, 1, "%"),
         "sub": f"{i18n.figures('q/q')}, INE"},
        {"label": _("Data in hand for {q}").format(q=q), "value": _("{n} of {total}").format(n=months, total=3 * len(n['coverage'])),
         "sub": _("monthly readings; the rest is projected")},
    ]


def nowcast_inputs_table(data: Data) -> dict | None:
    n = nowcast(data)
    if n is None:
        return None
    q = period_label(n["quarter"], "Q")
    rows = [{"heading": False, "label": _(c["input"].label), "label_es": data.by_id[c["input"].id].label_es, "indent": 0,
             "period_note": "", "url": source_page(data.by_id[c["input"].id], data.by_id),
             "cells": [period_label(c["last"], "M"), _("{n} of {total}").format(n=c['months'], total=3)]}
            for c in n["coverage"]]
    return {"title": _("Input"), "caption": _("What the {q} nowcast is built on").format(q=q), "through": q,
            "columns": [_("Latest month"), _("Months of {q}").format(q=q)], "rows": rows,
            "note": _("The model also uses the previous quarter's GDP growth. Months not yet published are projected "
                      "from each series' recent momentum (an AR(1) model), so early in a quarter the nowcast leans "
                      "on those projections.")}


def nowcast_record_table(data: Data) -> dict | None:
    n = nowcast(data)
    if n is None or not n["backtest"]:
        return None
    rows = [{"heading": False, "label": period_label(q, "Q"), "label_es": "", "indent": 0, "period_note": "", "url": None,
             "cells": [_fmt_signed(p, 1, "%"), _fmt_signed(a, 1, "%"), _fmt_signed(p - a, 1, " pp")]}
            for q, p, a, _naive in reversed(n["backtest"][-8:])]
    return {"title": _("Quarter"), "caption": _("Track record: each quarter predicted from a model fitted on earlier data"),
            "through": None, "columns": [_("Model"), _("Official"), _("Error")], "rows": rows,
            "note": _("Since 2023 the model's typical (root mean square) error is {rmse} pp, against {naive} pp for "
                      "repeating the previous quarter and {mean} pp for the post-2013 average. The inputs were chosen "
                      "with this same test, and it uses complete quarters of data, so real-time errors, with months "
                      "still missing, will be larger.").format(
                rmse=f"{n['rmse']:.2f}", naive=f"{n['naive_rmse']:.2f}", mean=f"{n['mean_rmse']:.2f}")}


def nowcast_chart(data: Data) -> dict | None:
    n = nowcast(data)
    if n is None or not n["backtest"]:
        return None
    iso = lambda d: d.strftime("%Y-%m-%d")
    bt = n["backtest"]
    spec = localise({"id": "nowcast", "title": "GDP growth: model and official figures", "subtitle": "",
                     "kind": "bar", "unit": "%", "decimals": 1, "signed": True, "freq": "Q", "ref_lines": [],
                     "series": [
                         {"name": "Official (INE)", "x": [iso(b[0]) for b in bt], "y": [round(b[2], 3) for b in bt]},
                         {"name": "Model", "kind": "line", "x": [iso(b[0]) for b in bt] + [iso(n["quarter"])],
                          "y": [round(b[1], 3) for b in bt] + [round(n["value"], 3)]},
                     ],
                     "source": _("Macroscope calculation from INE and Seguridad Social")})
    spec["subtitle"] = _("% change on the previous quarter; the last point is the nowcast for {q}").format(
        q=period_label(n["quarter"], "Q"))
    return spec


# ---------------------------------------------------------------- 10-year decomposition

MOVES = [("1-week", "week"), ("1-month", "month"), ("YTD", "ytd"), ("1-yr", "year")]


def yield_decomposition_table(data: Data) -> dict | None:
    es, de = data.raw("es_10y"), data.raw("de_10y")
    if es is None or de is None:
        return None
    both = pd.DataFrame({"es": es, "de": de}).dropna()
    if len(both) < 2:
        return None
    d = both.index[-1]
    refs = {"week": d - pd.Timedelta(days=7), "month": d - pd.DateOffset(months=1),
            "ytd": pd.Timestamp(d.year, 1, 1) - pd.Timedelta(days=1), "year": d - pd.DateOffset(years=1)}
    cols = {}
    for _label, key in MOVES:
        before = both[both.index <= refs[key]]
        cols[key] = None if before.empty else (both.iloc[-1] - before.iloc[-1]) * 100
    labels = [("Spain 10-year yield", lambda c: c["es"]), ("German Bund: euro-wide rates", lambda c: c["de"]),
              ("Prima de riesgo: Spain-specific", lambda c: c["es"] - c["de"])]
    rows = [{"heading": False, "label": _(label), "label_es": "", "indent": 0 if i == 0 else 1, "period_note": "",
             "url": None, "cells": [DASH if cols[k] is None else fmt_change(float(f(cols[k])), "bp", 0)
                                    for _head, k in MOVES]}
            for i, (label, f) in enumerate(labels)]
    day = i18n.day_month_year(d)
    return {"title": _("Change"), "caption": _("Basis points, to {day}, the latest day with both yields").format(day=day),
            "through": day, "columns": [_(h) for h, _key in MOVES], "rows": rows,
            "note": _("Spain's yield is the German yield plus the prima de riesgo, so the two parts add up to the "
                      "total. A rising Bund means rates are rising across the euro area; a rising prima de riesgo "
                      "is about Spain.")}


# ---------------------------------------------------------------- Taylor rules

R_STAR = 0.5         # neutral real interest rate assumed, %
TARGET = 2.0         # ECB inflation target, %
HP_LAMBDA = 129_600  # smoothing for monthly trend unemployment (Ravn and Uhlig)


def _rule(inflation: pd.Series, unemployment: pd.Series) -> pd.DataFrame | None:
    u = unemployment.dropna()
    if len(u) < 60:
        return None
    _cycle, trend = hpfilter(u, lamb=HP_LAMBDA)
    df = pd.DataFrame({"inflation": inflation, "unemployment": u, "trend": trend}).dropna()
    df["u_gap"] = df["unemployment"] - df["trend"]
    # Taylor (1993): r* + inflation + 0.5 x inflation gap + 0.5 x output gap, with an
    # output gap of -2 x the unemployment gap (Okun's law).
    df["rule"] = R_STAR + df["inflation"] + 0.5 * (df["inflation"] - TARGET) - df["u_gap"]
    return df


def taylor(data: Data) -> dict | None:
    def compute():
        out = {}
        for key, infl, unemp in (("ea", "hicp_euro_area", "unemployment_ea"), ("es", "hicp", "unemployment_monthly")):
            i, u = data.raw(infl), data.raw(unemp)
            if i is None or u is None:
                return None
            df = _rule(i, u)
            if df is None:
                return None
            out[key] = df
        dfr = data.raw("ecb_deposit_rate")
        out["dfr"] = None if dfr is None else dfr.dropna().resample("MS").mean()
        return out

    return _cached(data, "taylor", compute)


def taylor_facts(data: Data) -> list[dict]:
    t = taylor(data)
    if t is None:
        return []
    facts = []
    if t["dfr"] is not None:
        facts.append({"label": _("ECB deposit rate"), "value": fmt_value(float(t["dfr"].iloc[-1]), "%", 2),
                      "sub": _("{month} average").format(month=i18n.month_year(t["dfr"].index[-1]))})
    for key, label in (("ea", "Taylor rule, euro area"), ("es", "Taylor rule, Spain")):
        df = t[key]
        facts.append({"label": _(label), "value": fmt_value(float(df["rule"].iloc[-1]), "%", 1),
                      "sub": period_label(df.index[-1], "M")})
    gap = float(t["es"]["rule"].iloc[-1] - t["ea"]["rule"].iloc[-1])
    facts.append({"label": _("Spain minus euro area"), "value": _fmt_signed(gap, 1, " pp"),
                  "sub": _("the one-size-fits-all gap")})
    return facts


def taylor_table(data: Data) -> dict | None:
    t = taylor(data)
    if t is None:
        return None
    ea, es = t["ea"].iloc[-1], t["es"].iloc[-1]
    fmt = lambda v: fmt_value(float(v), "%", 1)
    lines = [
        ("Inflation (HICP)", fmt(ea["inflation"]), fmt(es["inflation"]), 0),
        ("Gap with the 2% target", _fmt_signed(ea["inflation"] - TARGET, 1, " pp"), _fmt_signed(es["inflation"] - TARGET, 1, " pp"), 1),
        ("Unemployment rate", fmt(ea["unemployment"]), fmt(es["unemployment"]), 0),
        ("Trend unemployment", fmt(ea["trend"]), fmt(es["trend"]), 1),
        ("Unemployment gap", _fmt_signed(ea["u_gap"], 1, " pp"), _fmt_signed(es["u_gap"], 1, " pp"), 1),
        ("Rate the rule suggests", fmt(ea["rule"]), fmt(es["rule"]), 0),
    ]
    rows = [{"heading": False, "label": _(label), "label_es": "", "indent": indent, "period_note": "", "url": None,
             "cells": [a, b]} for label, a, b, indent in lines]
    month = period_label(min(t["ea"].index[-1], t["es"].index[-1]), "M")
    return {"title": _("Input"), "caption": _("Latest month with every input · {month}").format(month=month),
            "through": month, "columns": [_("Euro area"), _("Spain")], "rows": rows,
            "note": _("Rule: {r_star}% neutral real rate + inflation + 0.5 × (inflation − 2%) − unemployment gap "
                      "(Taylor's 1993 rule, with an output gap of twice the unemployment gap). Trend unemployment is a "
                      "statistical trend (Hodrick–Prescott filter), so the latest gap is uncertain. A rule is a "
                      "yardstick, not a forecast of what the ECB will do.").format(r_star=R_STAR)}


def taylor_chart(data: Data) -> dict | None:
    t = taylor(data)
    if t is None:
        return None
    iso = lambda idx: [d.strftime("%Y-%m-%d") for d in idx]
    start = pd.Timestamp("2002-01-01")
    series = []
    if t["dfr"] is not None:
        d = t["dfr"][t["dfr"].index >= start].round(3)
        series.append({"name": "ECB deposit rate", "x": iso(d.index), "y": d.tolist(), "shape": "hv"})
    for key, name in (("ea", "Rule, euro area"), ("es", "Rule, Spain")):
        r = t[key]["rule"]
        r = r[r.index >= start].round(3)
        series.append({"name": name, "x": iso(r.index), "y": r.tolist()})
    return {"id": "taylor", "title": "The ECB rate and what a Taylor rule suggests",
            "subtitle": "%, monthly", "kind": "line", "unit": "%", "decimals": 1, "freq": "M", "series": series,
            "ref_lines": [], "source": _("Macroscope calculation from Eurostat and the ECB")}


# ---------------------------------------------------------------- home page

def home_facts(data: Data) -> list[dict]:
    """The strip of Macroscope readings on the home page."""
    facts = composite_facts(data)
    n = nowcast_facts(data)
    if n:
        facts.append(n[0])
    t = taylor(data)
    if t is not None and t["dfr"] is not None:
        gap = float(t["dfr"].iloc[-1] - t["ea"]["rule"].iloc[-1])
        facts.append({"label": _("ECB rate vs Taylor rule"), "value": _fmt_signed(gap, 1, " pp"),
                      "sub": _("deposit rate minus the euro-area rule")})
    return facts
