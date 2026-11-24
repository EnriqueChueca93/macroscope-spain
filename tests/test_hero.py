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
