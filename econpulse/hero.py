"""The opening of the home page (batches L1 and L2): a headline written from the data, the cycle clock, a long line
and four big numbers.

- The headline says what Macroscope's two scores (the Analysis page's composites: activity and inflation against
  their history since 2013, Covid years left out) say this month, in words: "Spain's economy is running close to
  its normal pace, while prices are rising much faster than normal." Five steps each way, at ±0.5 and ±1, the
  same cut-offs as the words beside the scores elsewhere ("close to normal" within ±0.5).
- The big numbers are four of the key indicators, as their tiles show them: GDP growth on a year earlier, Social
  Security registrations, CPI inflation and the unemployment rate, each with its period and a line of context.
  A script counts them up from zero when the page opens; without one they are simply there.
- The line is both scores month by month since 2013, drawn here as SVG on a fixed scale (+2.5 to −3: the scores
  are clipped at ±3, and their low was −2.9 in April 2020), with the normal range as a band and the Covid years
  shaded. The lines draw themselves from left to right when the page opens (CSS; still for readers who ask for
  reduced motion), and the labels are HTML placed over the drawing in percentages, so the drawing can stretch to
  any width without stretching the text. Hovering gives each month's two scores (static/app.js).
- The cycle clock (L2) follows the activity score's three-month average across (below or above normal) and its
  change over six months up (falling or rising), so its four quarters are expansion, slowdown, downturn and
  recovery. The past 24 months draw in as a trail, older months fainter, ending in a large dot. The scale is fixed
  at ±1.25, not the ±2.5 first planned: the average has stayed within ±0.5 since 2023, and on ±2.5 the trail was a
  speck in the middle. A month beyond the scale (2020's) sits on the edge, hollow.
"""

import json
import math

import pandas as pd

from . import analytics, i18n
from .analytics import ACTIVITY, COVID, INFLATION
from .i18n import _
from .snapshot import MINUS, fmt_value, period_label
from .tables import Data

Y_TOP, Y_BOTTOM = 2.5, -3.0     # the line's fixed scale
NORMAL = 0.5                    # within ±0.5 of zero, a score is "close to normal"
VIEW_W = 1000                   # the line's drawing box: 1000 across and 100 down, stretched to fit its box
TICKS = (2, 0, -2)
MIN_GAP = 26                    # the two end labels are kept at least this far apart (% of the chart's height:
                                # three lines of a phone's label in its 190 px chart)

# (the lowest score for the words, the words); the first that the score reaches
ECONOMY = [(1.0, "Spain's economy is running well above its normal pace"),
           (NORMAL, "Spain's economy is running above its normal pace"),
           (-NORMAL, "Spain's economy is running close to its normal pace"),
           (-1.0, "Spain's economy is running below its normal pace"),
           (-math.inf, "Spain's economy is running well below its normal pace")]
PRICES = [(1.0, "prices are rising much faster than normal"),
          (NORMAL, "prices are rising faster than normal"),
          (-NORMAL, "inflation is close to normal"),       # below normal, prices may not be rising at all
          (-1.0, "inflation is running below normal"),
          (-math.inf, "inflation is running well below normal")]
PAGE = "analysis.html#composites"


def _words(z: float, steps: list[tuple[float, str]]) -> str:
    return next(words for low, words in steps if z >= low)


def _side(z: float) -> int:
    """Above normal (1), close to it (0) or below (-1)."""
    return 1 if z >= NORMAL else -1 if z <= -NORMAL else 0


def _signed(v: float, decimals: int = 1) -> str:
    return analytics._fmt_signed(v, decimals)


def _scores(data: Data) -> tuple[pd.Series, pd.Series] | None:
    a = analytics.composite(data, ACTIVITY, "activity")
    p = analytics.composite(data, INFLATION, "inflation")
    if a is None or p is None or a["series"].empty or p["series"].empty:
        return None
    return a["series"], p["series"]


def headline(data: Data) -> dict | None:
    """The sentence, and the scores and month behind it."""
    scores = _scores(data)
    if scores is None:
        return None
    a, p = scores
    month = min(a.index[-1], p.index[-1])
    za, zp = float(a.asof(month)), float(p.asof(month))
    joiner = _("and") if _side(za) == _side(zp) else _("while")
    sentence = _("{economy}, {joiner} {prices}.").format(economy=_(_words(za, ECONOMY)), joiner=joiner,
                                                          prices=_(_words(zp, PRICES)))
    sub = _("Macroscope's scores for {month}: activity {activity}, inflation {inflation}, where zero is normal "
            "for 2013 to today (Covid years left out).").format(month=i18n.month_year(month), activity=_signed(za),
                                                                  inflation=_signed(zp))
    return {"text": sentence, "sub": sub, "link": PAGE, "link_text": _("How the scores work")}


def _value(item: dict | None, transform: str) -> dict | None:
    if not item:
        return None
    return next((v for v in item.get("values", []) if v["transform"] == transform), None)


def _number(label: str, display: str, value: float, decimals: int, suffix: str, period: str, note: str,
            page: str, unit: str = "") -> dict:
    """`display` is the number as the tile writes it (counted up to by the script, ending on exactly this);
    `unit` is a word set smaller after it ("million")."""
    return {"label": label, "display": display, "value": round(value, decimals), "decimals": decimals,
            "suffix": suffix, "unit": unit, "period": period, "note": note, "page": page}


def numbers(data: Data, indicators: dict[str, dict]) -> list[dict]:
    """The four big numbers, from the snapshot's indicators (as the tiles write them) and the stored series."""
    out = []
    gdp, quarter = _value(indicators.get("gdp"), "yoy"), _value(indicators.get("gdp"), "pop")
    if gdp:
        out.append(_number(_("GDP growth"), gdp["display"], gdp["value"], 1, "%",
                           _("{period}, on a year earlier").format(period=gdp["period"]),
                           _("{change} on the quarter").format(change=quarter["display"]) if quarter else "", "gdp.html"))
    regs = data.raw("afiliados") if "afiliados" in data.by_id else None
    year = _value(indicators.get("afiliados"), "diff_yoy")
    if regs is not None and not regs.dropna().empty:
        regs = regs.dropna()
        millions = float(regs.iloc[-1]) / 1000          # the register is kept in thousands
        out.append(_number(_("Social Security registrations"), f"{millions:.2f}", millions, 2, "",
                           period_label(regs.index[-1], "M"),
                           _("{change} on a year").format(change=year["display"]) if year else "", "labour.html",
                           unit=_("million")))
    for ind_id, label, decimals, page in (("cpi", "Inflation (CPI)", 1, "inflation.html"),
                                          ("unemployment_epa", "Unemployment rate", 2, "labour.html")):
        v = _value(indicators.get(ind_id), "level")
        if not v:
            continue
        before = v.get("year_ago")
        out.append(_number(_(label), v["display"], v["value"], decimals, "%", v["period"],
                           _("{value} a year earlier").format(value=fmt_value(before, "%", decimals))
                           if before is not None else "", page))
    return out


def _clip(v: float) -> float:
    return max(Y_BOTTOM, min(Y_TOP, v))


def _y(v: float) -> float:
    """Down the drawing, in % of its height."""
    return round((Y_TOP - _clip(v)) / (Y_TOP - Y_BOTTOM) * 100, 2)


def score_line(data: Data) -> dict | None:
    """The long line: both scores since 2013, as points in a 1000 × 100 box, with what goes over it in %."""
    scores = _scores(data)
    if scores is None:
        return None
    a, p = scores
    months = pd.date_range(min(a.index[0], p.index[0]), max(a.index[-1], p.index[-1]), freq="MS")
    if len(months) < 24:
        return None
    step = VIEW_W / (len(months) - 1)
    where = {m: k * step for k, m in enumerate(months)}

    def points(s: pd.Series) -> str:
        return " ".join(f"{where[m]:.1f},{_y(float(v)):.2f}" for m, v in s.items() if m in where)

    lines = []
    for key, s, name, hot in (("activity", a, _("Activity"), False), ("inflation", p, _("Inflation"), True)):
        z = float(s.iloc[-1])
        lines.append({"key": key, "name": name, "points": points(s), "x": round(where[s.index[-1]] / 10, 2),
                      "y": _y(z), "label_y": _y(z), "value": _signed(z), "words": _(analytics._describe(z, hot))})
    # keep the two end labels apart
    top, low = sorted(lines, key=lambda line: line["y"])
    if low["y"] - top["y"] < MIN_GAP:
        mid = (top["y"] + low["y"]) / 2
        top["label_y"], low["label_y"] = round(max(4, mid - MIN_GAP / 2), 2), round(min(96, mid + MIN_GAP / 2), 2)

    covid = [m for m in months if m.year in COVID]
    # every year on a laptop, every other on a tablet, every fourth on a phone (counted from the first)
    first = months[0].year
    years = [{"label": m.year, "x": round(where[m] / 10, 2), "every": 4 if (m.year - first) % 4 == 0 else
              2 if (m.year - first) % 2 == 0 else 1} for m in months if m.month == 1]
    end = months[-1]
    hover = [[i18n.month_year(m), None if pd.isna(a.get(m)) else round(float(a[m]), 2),
              None if pd.isna(p.get(m)) else round(float(p[m]), 2)] for m in months]
    return {
        "w": VIEW_W, "lines": lines,
        "band": {"top": _y(NORMAL), "bottom": _y(-NORMAL)}, "zero": _y(0),
        "covid": {"x": round(where[covid[0]], 1), "w": round(where[covid[-1]] - where[covid[0]], 1),
                  "left": round(where[covid[0]] / 10, 2), "width": round((where[covid[-1]] - where[covid[0]]) / 10, 2)}
        if covid else None,
        "years": years,
        "ticks": [{"label": "0" if t == 0 else (f"+{t}" if t > 0 else f"{MINUS}{-t}"), "y": _y(t)} for t in TICKS],
        "title": _("Activity and inflation against their history"),
        "subtitle": _("Macroscope's scores, monthly since {start}; the band is the normal range").format(start=months[0].year),
        "label": _("Line chart of Macroscope's activity and inflation scores, monthly from {start} to {end}. "
                   "In {end}: activity {activity}, inflation {inflation}.").format(
            start=i18n.month_year(months[0]), end=i18n.month_year(end), activity=lines[0]["value"],
            inflation=lines[1]["value"]),
        "hover": json.dumps({"months": hover, "names": [lines[0]["name"], lines[1]["name"]]}, ensure_ascii=False,
                            separators=(",", ":")),
        "source": _("Macroscope calculation from INE, Eurostat, Seguridad Social, Red Eléctrica"),
        "link": PAGE, "link_text": _("The full chart and the readings behind it"),
        "normal": _("Normal range"), "covid_label": _("Covid years"),
    }


# ---------------------------------------------------------------- L2: the cycle clock
CLOCK_LIMIT = 1.25      # the clock's fixed scale, each way; a month beyond it sits on the edge, drawn hollow
CLOCK_SMOOTH = 3        # months in the average the clock follows, so one month's noise doesn't send it round
CLOCK_STEP = 6          # momentum: the change in that average over this many months
CLOCK_TRAIL = 24        # months drawn
# (rising, above normal) -> the phase, as the four quarters of the clock name it
PHASES = {(True, True): "Expansion", (False, True): "Slowdown", (False, False): "Downturn", (True, False): "Recovery"}
PHASE_KEYS = {"Expansion": "expansion", "Slowdown": "slowdown", "Downturn": "downturn", "Recovery": "recovery"}
PHASE_WORDS = {"Expansion": "above normal and rising", "Slowdown": "above normal but falling",
               "Downturn": "below normal and falling", "Recovery": "below normal but rising"}


def phase(level: float, momentum: float) -> str:
    return PHASES[(momentum >= 0, level >= 0)]


def _pct(v: float, flip: bool = False) -> float:
    v = max(-CLOCK_LIMIT, min(CLOCK_LIMIT, v))
    return round(((CLOCK_LIMIT - v) if flip else (v + CLOCK_LIMIT)) / (2 * CLOCK_LIMIT) * 100, 2)


def cycle_clock(data: Data) -> dict | None:
    """The activity score's three-month average across (below or above normal) against its change over six months up
    (falling or rising): the past 24 months as a trail in a 100 × 100 box, older months fainter, and where it is now."""
    scores = _scores(data)
    if scores is None:
        return None
    level = scores[0].rolling(CLOCK_SMOOTH).mean()
    both = pd.DataFrame({"level": level, "momentum": level - level.shift(CLOCK_STEP)}).dropna()
    if len(both) < CLOCK_TRAIL:
        return None
    trail = both.tail(CLOCK_TRAIL)
    points = []
    for k, (month, row) in enumerate(trail.iterrows()):
        lv, mo = float(row["level"]), float(row["momentum"])
        name = phase(lv, mo)
        points.append({"month": i18n.month_year(month), "x": _pct(lv), "y": _pct(mo, flip=True),
                       "out": abs(lv) > CLOCK_LIMIT or abs(mo) > CLOCK_LIMIT, "phase": _(name), "key": PHASE_KEYS[name],
                       "level": _signed(lv), "momentum": _signed(mo),
                       "opacity": round(0.18 + 0.82 * k / (len(trail) - 1), 2)})
    now = points[-1]
    segments = [{"x1": a["x"], "y1": a["y"], "x2": b["x"], "y2": b["y"], "opacity": b["opacity"], "i": k}
                for k, (a, b) in enumerate(zip(points, points[1:]))]
    mo_now = float(trail["momentum"].iloc[-1])
    name = phase(float(trail["level"].iloc[-1]), mo_now)
    earlier = []
    for months_back, words in ((6, "Six months earlier"), (12, "A year earlier")):
        if months_back < len(points):
            p = points[-1 - months_back]
            earlier.append(_("{when} ({month}): {phase}").format(when=_(words), month=p["month"], phase=p["phase"].lower()))
    quadrants = [{"key": PHASE_KEYS[n], "name": _(n), "words": _(PHASE_WORDS[n]), "now": n == name}
                 for n in ("Recovery", "Expansion", "Downturn", "Slowdown")]       # in reading order, top left first
    return {
        "points": points, "segments": segments, "now": now, "phase": _(name), "key": PHASE_KEYS[name],
        "normal": {"x": _pct(-NORMAL), "w": round(_pct(NORMAL) - _pct(-NORMAL), 2)},
        "grid": [_pct(v) for v in (-1.0, -NORMAL, NORMAL, 1.0)],
        "label_side": "left" if now["x"] > 62 else "right",
        "title": _("The cycle clock"),
        "reading": _("{month}: {phase}. Activity is {words}: its three-month average is {level}, {change} over six "
                     "months.").format(month=now["month"], phase=_(name), words=_(PHASE_WORDS[name]), level=now["level"],
                                       change=(_("up {n}") if mo_now >= 0 else _("down {n}")).format(n=f"{abs(mo_now):.1f}")),
        "earlier": earlier,
        "quadrants": quadrants,
        "how": _("The activity score's three-month average across, and its change over six months up, for the past "
                 "24 months; a fixed scale (±{limit}), so the clock doesn't rescale from month to month, and a month "
                 "beyond it sits on the edge, hollow.").format(limit=CLOCK_LIMIT),
        "label": _("Cycle clock: the past 24 months of Macroscope's activity score, from {start} to {end}, ending in "
                   "{phase}.").format(start=points[0]["month"], end=now["month"], phase=_(name).lower()),
        "axis": {"left": _("Below normal"), "right": _("Above normal"), "up": _("Rising"), "down": _("Falling")},
        "hover": json.dumps([[p["month"], p["x"], p["y"], p["phase"], p["level"], p["momentum"]] for p in points],
                            ensure_ascii=False, separators=(",", ":")),
        "hover_words": json.dumps({"level": _("Three-month average"), "momentum": _("Over six months")},
                                  ensure_ascii=False, separators=(",", ":")),
    }


def hero(data: Data, indicators: dict[str, dict]) -> dict | None:
    """Everything the opening needs, or None when the scores can't be worked out (the page then opens as before)."""
    head = headline(data)
    if head is None:
        return None
    return {"headline": head, "numbers": numbers(data, indicators), "line": score_line(data), "clock": cycle_clock(data)}
