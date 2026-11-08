"""Chart specifications: what each chart shows, built from the store in Python.

The browser (static/app.js) turns a spec into a Plotly chart using the page's
theme colors, so a spec carries data and wording only, never colors.

Spec fields: id, title, subtitle, kind ("line" | "bar"), unit, decimals,
date_format (d3 format for the hover date), series [{name, x, y, kind?, color?, shape?}],
ref_lines [{y, label}], stack (stacked bars), signed (show + on rises), freq
(the finest frequency among the series), x_kind ("category" for curves), x_title,
source, sources, link.

`source` names the publishers ("INE; Eurostat"); `sources` (source_links) links each to the page with the
chart's data: [{name, url}] when the source has one page in the chart, [{name, links: [{label, url}], more}]
when it has several (labelled by series; `more` past MAX_LINKS), or [{name}] with none (a calculation).

In a definition each series is (indicator id, transform, name) with an optional
fourth item of options: {"kind": "line"} to draw one series differently from the
chart, {"color": "ink"} for a total drawn in text colour rather than a palette slot,
{"shape": "hv"} for a step line (policy rates change in steps), {"scale": 0.001} to
change units (thousands to millions), {"rebase": "2007-01-01"} for an index = 100 then.

A curve definition ("curve": True) draws one line per date across maturities
instead: "lines" [{"at", "name", "points"}], where points are (indicator id, label)
and "at" is latest, month (a month earlier), yearend or year (a year earlier).

An XY definition ("kind": "xy") plots one measure against another over time, e.g. a
Beveridge curve: "x" and "y" are (indicator id, transform, axis label, unit) and each
point is labelled with its period.

A ranking definition ("kind": "hbar") draws horizontal bars, one per item (region,
country), sorted by the latest value: "items" [(indicator id, label[, transform])], a
default "transform", "ref_from" [(indicator id, label[, transform])] for a reference
line (the Spanish average) and
"highlight" (a label drawn in text colour).
"""

from collections import Counter

import pandas as pd

from . import i18n, transforms
from .registry import Indicator
from .snapshot import period_label
from .sources import CALCULATED_FROM, SOURCE_NAMES, derived
from .store import Store

HOME_CHARTS = [
    {
        "id": "inflation",
        "title": "Inflation",
        "subtitle": "Harmonised index (HICP), % change on a year earlier",
        "kind": "line", "unit": "%", "decimals": 1, "start": "2019-01-01",
        "series": [("hicp", "level", "HICP"), ("hicp_core", "level", "Core HICP")],
        "ref_lines": [{"y": 2, "label": "2% target"}],
        "link": "inflation.html",
    },
    {
        "id": "yields",
        "title": "10-year government bond yields",
        "subtitle": "%, daily; the gap between the lines is the prima de riesgo",
        "kind": "line", "unit": "%", "decimals": 2, "start": "2022-01-01", "date_format": "%-d %b %Y",
        "series": [("es_10y", "level", "Spain"), ("de_10y", "level", "Germany")],
        "link": "financial.html",
    },
    {
        "id": "registrations",
        "title": "Social Security registrations",
        "subtitle": "Monthly change, thousands, seasonally adjusted by Macroscope",
        "kind": "bar", "signed": True, "unit": "k", "decimals": 1, "start": "2022-01-01",
        "series": [("afiliados", "sa_diff", "Monthly change")],
        "link": "labour.html",
    },
]


FREQ_ORDER = "DMQA"


def source_names(ind: Indicator, by_id: dict[str, Indicator]) -> list[str]:
    """Who publishes the data behind an indicator; a calculation credits its inputs' sources too."""
    if ind.source in CALCULATED_FROM:
        return [CALCULATED_FROM[ind.source], SOURCE_NAMES["derived"]]
    if not ind.is_derived:
        return [ind.source_name]
    names = [n for dep in derived.inputs_of(ind.params) if dep in by_id for n in source_names(by_id[dep], by_id)]
    return list(dict.fromkeys(names + [ind.source_name]))


MAX_LINKS = 4      # a source's pages named under a chart; the rest are listed under "Show data"


def _pages(label: str, label_es: str | None, ind: Indicator, by_id: dict[str, Indicator]) -> list[tuple]:
    """(source name, label, Spanish label, url) for each publisher's page behind one indicator; a calculation
    points to its inputs' pages, labelled with their names."""
    if ind.source in CALCULATED_FROM or not ind.is_derived:
        return [(CALCULATED_FROM.get(ind.source) or ind.source_name, label, label_es, ind.source_url())]
    return [page for dep in derived.inputs_of(ind.params) if dep in by_id
            for page in _pages(by_id[dep].label, by_id[dep].label_es, by_id[dep], by_id)]


def source_page(ind: Indicator, by_id: dict[str, Indicator]) -> str | None:
    """The publisher's page behind one indicator: its own, or for a calculation its first input's."""
    return next((page[3] for page in _pages(ind.label, ind.label_es, ind, by_id) if page[3]), None)


def source_links(items: list[tuple[str, Indicator]], by_id: dict[str, Indicator]) -> list[dict]:
    """A chart's sources, each linked to its own page (see the module's docstring). `items` are
    (the series' name in the chart, its indicator). In the order of _sources, the calculation credit last."""
    calc = SOURCE_NAMES.get("derived", "derived")
    groups: dict[str, dict[str, tuple]] = {}
    for label, ind in items:
        for name in source_names(ind, by_id):
            groups.setdefault(name, {})
        for name, page_label, label_es, url in _pages(label, None, ind, by_id):
            if url:
                groups.setdefault(name, {}).setdefault(url, (page_label, label_es))
    out = []
    for name, pages in groups.items():
        if name == calc:
            continue
        if len(pages) == 1:
            out.append({"name": name, "url": next(iter(pages))})
        elif pages:
            links = [{"label": lab, "label_es": es, "url": url} for url, (lab, es) in pages.items()]
            out.append({"name": name, "links": links[:MAX_LINKS], "more": links[MAX_LINKS:]})
        else:
            out.append({"name": name})
    return out + ([{"name": calc}] if calc in groups else [])


def _sources(inds: list[Indicator], by_id: dict[str, Indicator]) -> str:
    names = [n for ind in inds for n in source_names(ind, by_id)]
    calc = SOURCE_NAMES.get("derived", "derived")
    # The calculation credit goes last, once.
    return "; ".join(i18n._(n) for n in [n for n in dict.fromkeys(names) if n != calc] + ([calc] if calc in names else []))


_TEXT_KEYS = ("title", "subtitle", "x_title", "x_label", "y_label", "a_name", "b_name", "left", "right", "size_label")


def localise(spec: dict) -> dict:
    """A chart spec's words in the language being written (Batch 33b): titles, axis and series names,
    reference lines, the rows of a dot or dumbbell chart, and category labels the catalogue knows.
    Numbers and dates are left as they are. A spec is put into a language once (`lang` marks it)."""
    if spec.get("lang") == i18n.lang():
        return spec
    spec["lang"] = i18n.lang()
    if i18n.lang() == "en":
        return spec
    for key in _TEXT_KEYS:
        if spec.get(key):
            spec[key] = i18n._(spec[key])
    if spec.get("unit"):                          # bp → pb, % of GDP → % del PIB, € bn → mm €; symbols stay
        spec["unit"] = i18n.maybe(spec["unit"])
    if spec.get("size_unit"):
        spec["size_unit"] = i18n.maybe(spec["size_unit"])
    if spec.get("highlight"):                     # a ranking's highlighted bar, named like its category labels
        spec["highlight"] = i18n.maybe(spec["highlight"])
    for s in spec.get("series", []):
        if s.get("name"):
            s["name"] = i18n.maybe(s["name"]) if s.get("country") else i18n._(s["name"])
        if spec.get("x_kind") == "category":
            s["x"] = [i18n.maybe(x) for x in s["x"]]
    for s in spec.get("sources", []):
        s["name"] = i18n._(s["name"])
        for link in s.get("links", []) + s.get("more", []):
            link["label"] = link.pop("label_es", None) or i18n.maybe(link["label"])
    for key in ("ref_lines", "rows"):
        if spec.get(key):
            spec[key] = [{**r, "label": i18n.maybe(r["label"]) if key == "rows" else i18n._(r["label"])}
                         if r.get("label") else r for r in spec[key]]
    return spec


def build_chart(definition: dict, by_id: dict[str, Indicator], store: Store) -> dict | None:
    """One chart spec, or None if none of its series has data."""
    start = pd.Timestamp(definition["start"])
    series, sources, freqs, named = [], [], [], []
    for ind_id, transform, name, *options in definition["series"]:
        raw = store.load_series(ind_id)
        if raw is None:
            continue
        ind = by_id[ind_id]
        try:
            s = transforms.apply(transform, raw, ind.freq)
        except ValueError:  # e.g. too little history to seasonally adjust
            continue
        opts = dict(options[0]) if options else {}
        if "rebase" in opts:
            base = s.asof(pd.Timestamp(opts.pop("rebase")))
            if pd.isna(base) or base == 0:
                continue
            s = s / base * 100
        s = s * opts.pop("scale", 1)
        freq = ind.freq
        if opts.pop("month_end", False):          # a daily rate as its value at the end of each month
            s, freq = s.resample("MS").last().dropna(), "M"
        s = s[s.index >= start].round(4)
        if s.empty:
            continue
        series.append({"name": name, "x": [d.strftime("%Y-%m-%d") for d in s.index], "y": s.tolist(), **opts})
        sources.append(ind)
        named.append((name, ind))
        freqs.append(freq)
    if not series:
        return None
    spec = {k: v for k, v in definition.items() if k not in ("series", "start")}
    spec["series"] = series
    spec["freq"] = min(freqs, key=FREQ_ORDER.index)
    spec["source"] = _sources(sources, by_id)
    spec["sources"] = source_links(named, by_id)
    return localise(spec)


def build_home_charts(indicators: list[Indicator], store: Store) -> list[dict]:
    by_id = {i.id: i for i in indicators}
    charts = (build_chart(c, by_id, store) for c in HOME_CHARTS)
    return [c for c in charts if c]


def _day(d: pd.Timestamp) -> str:
    return i18n.day_month_year(d)


def build_curve(definition: dict, by_id: dict[str, Indicator], store: Store) -> dict | None:
    """A curve chart (x = maturity or horizon), or None without enough data.

    Every line is read at the same dates, set by the latest date all its points share.
    """
    loaded = {}
    for line in definition["lines"]:
        for ind_id, _ in line["points"]:
            s = store.load_series(ind_id)
            if s is not None and not s.dropna().empty:
                loaded[ind_id] = s.dropna().sort_index()
    if len(loaded) < 2:
        return None
    latest = min(s.index[-1] for s in loaded.values())
    dates = {
        "latest": latest,
        "month": latest - pd.DateOffset(months=1),
        "yearend": pd.Timestamp(latest.year, 1, 1) - pd.Timedelta(days=1),
        "year": latest - pd.DateOffset(years=1),
    }
    series = []
    for line in definition["lines"]:
        date = dates[line["at"]]
        x, y = [], []
        for ind_id, label in line["points"]:
            v = loaded[ind_id].asof(date) if ind_id in loaded else None
            if v is not None and not pd.isna(v):
                x.append(label)
                y.append(round(float(v), 4))
        if len(y) >= 2:
            name = i18n._(line["name"]).format(date=_day(date), prev_year=latest.year - 1)
            series.append({"name": name, "x": [i18n.maybe(m) for m in x], "y": y})
    if not series:
        return None
    ref_lines = list(definition.get("ref_lines", []))
    for ind_id, label in definition.get("ref_from", []):
        s = store.load_series(ind_id)
        if s is not None and not s.dropna().empty:
            v = float(s.dropna().asof(latest))
            ref_lines.append({"y": round(v, 4), "label": f"{i18n._(label)} {v:.{definition['decimals']}f}%"})
    ids = {i for line in definition["lines"] for i, _ in line["points"] if i in loaded}
    spec = {k: v for k, v in definition.items() if k not in ("lines", "curve", "ref_from", "ref_lines")}
    spec.update(kind="line", x_kind="category", x_title=definition.get("x_title", "Maturity"), freq=None,
                ref_lines=list(definition.get("ref_lines", [])), source=_sources([by_id[i] for i in sorted(ids)], by_id),
                sources=source_links([(label, by_id[i]) for line in definition["lines"]
                                      for i, label in line["points"] if i in loaded], by_id))
    localise(spec)                  # before the series and reference lines, whose names carry dates and figures
    spec.update(series=series, ref_lines=spec["ref_lines"] + ref_lines[len(definition.get("ref_lines", [])):])
    return spec


def build_ranking(definition: dict, by_id: dict[str, Indicator], store: Store) -> dict | None:
    """A horizontal bar chart ranking items on their latest value, or None with fewer than two."""
    default = definition.get("transform", "level")

    def latest(ind_id, transform=default):
        raw = store.load_series(ind_id)
        if raw is None:
            return None
        try:
            s = transforms.apply(transform, raw, by_id[ind_id].freq).dropna()
        except ValueError:
            return None
        return None if s.empty else (round(float(s.iloc[-1]), 4), s.index[-1])

    rows = [(label, *point, by_id[i]) for i, label, *transform in definition["items"] if (point := latest(i, *transform))]
    if len(rows) < 2:
        return None
    rows.sort(key=lambda r: r[1], reverse=True)
    # Items can lag (a region's data a quarter behind): the subtitle names the most common period.
    (date, freq), _ = Counter((r[2], r[3].freq) for r in rows).most_common(1)[0]
    ref_lines = []
    for ind_id, label, *transform in definition.get("ref_from", []):
        point = latest(ind_id, *transform) if ind_id in by_id else None
        if point:
            ref_lines.append({"y": point[0], "label": label})
    sources = _sources([r[3] for r in rows], by_id)
    spec = {k: v for k, v in definition.items() if k not in ("items", "transform", "ref_from", "start")}
    spec.update(kind="hbar", x_kind="category", x_title=definition.get("x_title", "Region"),
                series=[{"name": definition.get("name", definition["title"]),
                         "x": [r[0] for r in rows], "y": [r[1] for r in rows]}],
                ref_lines=ref_lines, freq=None, source=sources, sources=source_links([(r[0], r[3]) for r in rows], by_id))
    localise(spec)
    spec["subtitle"] = f"{spec['subtitle']} · {period_label(date, freq)}"
    return spec


def build_xy(definition: dict, by_id: dict[str, Indicator], store: Store) -> dict | None:
    """One measure against another, period by period (both on the same frequency)."""
    start = pd.Timestamp(definition["start"])
    parts = []
    for ind_id, transform, _, _ in (definition["x"], definition["y"]):
        raw = store.load_series(ind_id)
        if raw is None:
            return None
        try:
            parts.append(transforms.apply(transform, raw, by_id[ind_id].freq))
        except ValueError:
            return None
    both = pd.DataFrame({"x": parts[0], "y": parts[1]}).dropna()
    both = both[both.index >= start].round(4)
    if len(both) < 2:
        return None
    freq = by_id[definition["x"][0]].freq
    inds = [by_id[definition["x"][0]], by_id[definition["y"][0]]]
    spec = {k: v for k, v in definition.items() if k not in ("x", "y", "start")}
    spec.update(kind="xy", x_label=definition["x"][2], x_unit=definition["x"][3], y_label=definition["y"][2],
                y_unit=definition["y"][3], freq=freq, x_kind="xy", x_title="Period",
                series=[{"name": definition["title"], "x": both["x"].tolist(), "y": both["y"].tolist(),
                         "text": [period_label(d, freq) for d in both.index]}],
                ref_lines=[], source=_sources(inds, by_id),
                sources=source_links([(definition["x"][2], inds[0]), (definition["y"][2], inds[1])], by_id))
    return localise(spec)
