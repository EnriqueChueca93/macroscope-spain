"""The home page's opening (batch L1, econpulse/hero.py): the headline, the big numbers and the long line."""

import json

import numpy as np
import pandas as pd

from econpulse import hero, i18n
from econpulse.build import build_site
from econpulse.registry import Indicator, load_registry
from econpulse.store import Store
from econpulse.tables import Data

N = 166         # Jan 2013 to Oct 2026


def months(values, start="2013-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="MS"), dtype=float)


def ending(z):
    return months(np.r_[np.zeros(N - 1), z])


def fake_scores(monkeypatch, activity, inflation):
    monkeypatch.setattr(hero, "_scores", lambda data: (activity, inflation))


def test_the_headline_puts_both_scores_in_words(monkeypatch):
    fake_scores(monkeypatch, ending(0.19), ending(1.42))
    h = hero.headline(None)
    assert h["text"] == ("Spain's economy is running close to its normal pace, while prices are rising much faster "
                         "than normal.")
    assert h["sub"].startswith("Macroscope's scores for Oct 2026: activity +0.2, inflation +1.4, where zero is normal")
    assert h["link"] == "analysis.html#composites"
    cases = {(0.7, 0.6): "Spain's economy is running above its normal pace, and prices are rising faster than normal.",
             (-1.2, -0.7): "Spain's economy is running well below its normal pace, and inflation is running below normal.",
             (-0.3, 0.2): "Spain's economy is running close to its normal pace, and inflation is close to normal.",
             (1.5, -1.1): "Spain's economy is running well above its normal pace, while inflation is running well below normal."}
    for (a, p), text in cases.items():
        fake_scores(monkeypatch, ending(a), ending(p))
        assert hero.headline(None)["text"] == text
    fake_scores(monkeypatch, ending(0.19), ending(1.42))
    with i18n.using("es"):
        es = hero.headline(None)
    assert es["text"] == ("La economía española avanza cerca de su ritmo normal, mientras que los precios suben mucho "
                          "más deprisa de lo normal.")
    assert es["sub"].startswith("Puntuaciones de Macroscope en oct 2026: actividad +0.2, inflación +1.4")


def test_the_line_is_drawn_on_a_fixed_scale(monkeypatch):
    a = months(np.linspace(-1, 1, N))
    p = months(np.linspace(0, 1.4, N))
    p[pd.Timestamp("2022-08-01")] = 9.0                       # off the scale: drawn at the top edge
    fake_scores(monkeypatch, a, p)
    line = hero.score_line(None)
    points = line["lines"][0]["points"].split()
    assert len(points) == N and points[0] == "0.0,63.64" and points[-1] == "1000.0,27.27"   # −1 and +1 on +2.5 to −3
    assert min(float(q.split(",")[1]) for q in line["lines"][1]["points"].split()) == 0.0
    assert line["band"] == {"top": 36.36, "bottom": 54.55} and line["zero"] == 45.45
    # the Covid years, 2020 and 2021: months 84 to 107 of 166
    assert line["covid"]["left"] == 50.91 and line["covid"]["width"] == 13.94
    # the end labels, 7 points apart where they end, are pushed 26 apart around their middle
    ends = {x["key"]: x for x in line["lines"]}
    assert ends["activity"]["y"] == 27.27 and ends["inflation"]["y"] == 20.0
    assert abs(ends["inflation"]["label_y"] - 10.64) < 0.02 and abs(ends["activity"]["label_y"] - 36.64) < 0.02
    assert ends["inflation"]["value"] == "+1.4" and ends["inflation"]["words"] == "hotter than normal"
    years = {y["label"]: y["every"] for y in line["years"]}
    assert len(years) == 14 and (years[2013], years[2014], years[2015], years[2017]) == (4, 1, 2, 4)
    hover = json.loads(line["hover"])
    assert hover["names"] == ["Activity", "Inflation"] and hover["months"][-1] == ["Oct 2026", 1.0, 1.4]
    assert line["ticks"][2] == {"label": "−2", "y": 81.82}


def test_the_big_numbers_are_the_tiles_figures(tmp_path):
    store = Store(tmp_path / "data")
    store.save_series("afiliados", months(np.linspace(21800.0, 22620.4, 22), start="2025-01-01"))
    snapshot = {
        "gdp": {"values": [{"transform": "pop", "display": "0.6%", "value": 0.63, "period": "Q3 2026"},
                           {"transform": "yoy", "display": "2.7%", "value": 2.663, "period": "Q3 2026"}]},
        "afiliados": {"values": [{"transform": "diff_yoy", "display": "+784.6k", "value": 784.6, "period": "Oct 2026"}]},
        "cpi": {"values": [{"transform": "level", "display": "4.9%", "value": 4.9, "period": "Oct 2026", "year_ago": 3.1}]},
        "unemployment_epa": {"values": [{"transform": "level", "display": "10.18%", "value": 10.18, "period": "Q3 2026",
                                         "year_ago": 10.45}]},
    }
    got = hero.numbers(Data(load_registry(), store), snapshot)
    assert [(n["label"], n["display"], n["unit"], n["period"], n["note"], n["page"]) for n in got] == [
        ("GDP growth", "2.7%", "", "Q3 2026, on a year earlier", "0.6% on the quarter", "gdp.html"),
        ("Social Security registrations", "22.62", "million", "Oct 2026", "+784.6k on a year", "labour.html"),
        ("Inflation (CPI)", "4.9%", "", "Oct 2026", "3.1% a year earlier", "inflation.html"),
        ("Unemployment rate", "10.18%", "", "Q3 2026", "10.45% a year earlier", "labour.html")]
    # what the script counts up to, ending on the text as written
    assert [(n["value"], n["decimals"], n["suffix"]) for n in got] == [(2.7, 1, "%"), (22.62, 2, ""), (4.9, 1, "%"),
                                                                       (10.18, 2, "%")]
    with i18n.using("es"):
        es = hero.numbers(Data(load_registry(), store), snapshot)
    assert es[1]["unit"] == "millones" and es[2]["label"] == "Inflación (IPC)" and es[3]["note"] == "10.45% un año antes"


def _site(tmp_path):
    store = Store(tmp_path / "data")
    idx = pd.date_range("2025-01-01", periods=21, freq="MS")
    store.save_series("es", pd.Series(np.linspace(4.0, 4.2, 21), index=idx))
    store.save_catalog({"es": {"status": "ok", "fetched_at": "2026-10-30T12:00:00+00:00", "last_date": "2026-09-01"}})
    inds = [Indicator(id="es", label="Spain 10-year yield", label_es="es", section="financial", source="fake", key="es",
                      freq="M", unit="%", change_unit="bp", decimals=2, tile=1)]
    build_site(inds, store, site_dir=tmp_path / "site")
    site = tmp_path / "site"
    return (site / "index.html").read_text(encoding="utf-8"), (site / "es" / "index.html").read_text(encoding="utf-8")


def test_the_page_opens_with_the_hero(tmp_path, monkeypatch):
    fake_scores(monkeypatch, ending(0.19), ending(1.42))
    en, es = _site(tmp_path)
    assert '<h1 class="hero-title" id="hero-title">Spain&#39;s economy is running close to its normal pace' in en
    assert en.count('class="hl-line hl-') == 2 and 'class="hero-line" data-reveal data-hover="' in en
    assert '<p class="lede">' not in en
    assert "La economía española avanza cerca de su ritmo normal" in es and "Rango normal" in es


def test_without_the_scores_the_page_opens_as_before(tmp_path):
    en, _es = _site(tmp_path)          # no data behind the scores
    assert '<p class="lede">A running read on the health of the Spanish economy.</p>' in en
    assert 'class="hero"' not in en


# ---------------------------------------------------------------- L2: the cycle clock

def test_the_four_phases():
    assert [hero.phase(lv, mo) for lv, mo in ((0.2, 0.4), (0.2, -0.1), (-0.3, -0.2), (-0.3, 0.1), (0.0, 0.0))] == \
        ["Expansion", "Slowdown", "Downturn", "Recovery", "Expansion"]


def test_the_clock_follows_the_three_month_average_and_its_change(monkeypatch):
    step = 2 / (N - 1)
    a = months(np.linspace(-1, 1, N))                    # rising steadily to +1
    fake_scores(monkeypatch, a, ending(1.0))
    c = hero.cycle_clock(None)
    assert len(c["points"]) == 24 and len(c["segments"]) == 23
    assert c["points"][0]["month"] == "Nov 2024" and c["points"][0]["opacity"] == 0.18 and c["now"]["opacity"] == 1.0
    level, momentum = 1 - step, 6 * step                   # the last three months' average, and its rise over six
    assert c["now"]["x"] == round((level + 1.25) / 2.5 * 100, 2) and c["now"]["y"] == round((1.25 - momentum) / 2.5 * 100, 2)
    assert c["key"] == "expansion" and c["phase"] == "Expansion" and c["label_side"] == "left"   # near the right edge
    assert c["reading"] == ("Oct 2026: Expansion. Activity is above normal and rising: its three-month average is "
                            "+1.0, up 0.1 over six months.")
    assert c["earlier"] == ["Six months earlier (Apr 2026): expansion", "A year earlier (Oct 2025): expansion"]
    assert [q["key"] for q in c["quadrants"]] == ["recovery", "expansion", "downturn", "slowdown"]
    assert [q["now"] for q in c["quadrants"]] == [False, True, False, False]
    assert c["normal"] == {"x": 30.0, "w": 40.0} and c["grid"] == [10.0, 30.0, 70.0, 90.0]
    assert json.loads(c["hover"])[-1][:4] == ["Oct 2026", c["now"]["x"], c["now"]["y"], "Expansion"]
    # a month beyond the fixed scale sits on the edge, hollow
    a[a.index[-3:]] = 3.0
    c = hero.cycle_clock(None)
    assert c["now"]["out"] and c["now"]["x"] == 100.0 and c["now"]["y"] == 0.0
    # falling from above normal: a slowdown, and the reading says "down"
    fake_scores(monkeypatch, months(np.r_[np.zeros(N - 12), np.linspace(0.2, 1.2, 6), np.linspace(1.0, 0.4, 6)]), ending(1.0))
    c = hero.cycle_clock(None)
    assert c["phase"] == "Slowdown" and c["reading"].endswith("its three-month average is +0.5, down 0.5 over six months.")
    with i18n.using("es"):
        es = hero.cycle_clock(None)
    assert es["phase"] == "Desaceleración" and es["reading"].startswith("oct 2026: Desaceleración. La actividad está por "
                                                                           "encima de lo normal pero bajando")
    assert "y ha bajado 0." in es["reading"] and es["axis"]["up"] == "Subiendo"


def test_the_page_has_the_clock(tmp_path, monkeypatch):
    fake_scores(monkeypatch, months(np.linspace(-1, 1, N)), ending(1.42))
    en, es = _site(tmp_path)
    assert 'class="hero-clock" data-reveal' in en and en.count('class="hc-seg"') == 23
    assert 'class="hc-q hc-q-expansion is-now"' in en and '<span class="hc-label hc-label-left"' in en
    assert "El reloj del ciclo" in es and "Expansión" in es


# ---------------------------------------------------------------- L3: the map of Spain

def regional_store(tmp_path):
    store = Store(tmp_path / "data")
    quarters = pd.date_range("2024-01-01", "2026-07-01", freq="QS")
    store.save_series("unemployment_epa", pd.Series(10.0, index=quarters))
    rates = {slug: 10.0 for slug in hero.TILES} | {"andalucia": 15.0, "baleares": 4.6, "madrid": 9.5, "galicia": 11.2}
    for slug, rate in rates.items():
        store.save_series(f"unemployment_{slug}", pd.Series(rate, index=quarters))
    return store


def test_the_map_shades_each_community_by_its_gap_to_spain(tmp_path):
    m = hero.region_map(Data(load_registry(), regional_store(tmp_path)))
    assert [x["key"] for x in m["measures"]] == ["unemp"]            # the other measures have no data here
    assert m["measures"][0]["legend"] == "Spain: 10.00% (Q3 2026)" and (m["cols"], m["rows"]) == (6, 5)
    tiles = {t["code"]: t for t in m["tiles"]}
    assert len(tiles) == 17 and (tiles["GA"]["col"], tiles["GA"]["row"]) == (1, 1) and (tiles["CN"]["col"], tiles["CN"]["row"]) == (1, 5)
    shades = {code: t["by"]["unemp"]["shade"] for code, t in tiles.items()}
    assert (shades["AN"], shades["IB"], shades["MD"], shades["GA"], shades["CT"]) == ("hot3", "cool3", "mid", "hot1", "mid")
    assert tiles["AN"]["by"]["unemp"]["text"] == "15.0"
    assert tiles["AN"]["by"]["unemp"]["title"] == "Andalucía, Q3 2026: 15.0%, 5.0 points above Spain"
    assert tiles["CT"]["by"]["unemp"]["title"] == "Cataluña, Q3 2026: 10.0%, the same as Spain"
    with i18n.using("es"):
        es = hero.region_map(Data(load_registry(), regional_store(tmp_path)))
    an = next(t for t in es["tiles"] if t["code"] == "AN")
    assert an["by"]["unemp"]["title"] == "Andalucía, T3 2026: 15.0%, 5.0 puntos por encima de España"
    assert es["title"] == "Las regiones" and es["measures"][0]["legend"] == "España: 10.00% (T3 2026)"
