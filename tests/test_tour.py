"""The tour of the site on the home page (batches L4 and L5, econpulse/tour.py): the chart toolkit and chapters."""

import numpy as np
import pandas as pd

from econpulse import i18n, tour
from econpulse.build import SECTION_PAGES
from econpulse.registry import load_registry
from econpulse.store import Store
from econpulse.tables import Data


def monthly(values, start="2019-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="MS"), dtype=float)


def test_squarify_fills_the_box_with_near_squares():
    rects = tour.squarify([50, 25, 15, 10], 0, 0, 160, 100)
    assert len(rects) == 4
    assert abs(sum(w * h for _x, _y, w, h in rects) - 160 * 100) < 1e-6
    for (x, y, w, h), v in zip(rects, [50, 25, 15, 10]):
        assert abs(w * h - v / 100 * 16000) < 1e-6 and 0 <= x and x + w <= 160 + 1e-9 and y + h <= 100 + 1e-9
    assert max(max(w / h, h / w) for _x, _y, w, h in rects) < 3


def test_lines_are_drawn_on_round_ticks_with_labels_kept_apart():
    a, b = monthly(np.linspace(1.0, 3.0, 24)), monthly(np.linspace(1.0, 2.9, 24))
    c = tour.line_chart([{"name": "A", "s": a, "slot": 1}, {"name": "B", "s": b, "slot": 2, "dashed": True}], "%", 1)
    assert c["kind"] == "lines" and [ln["dashed"] for ln in c["lines"]] == [False, True]
    first, last = c["lines"][0]["points"].split()[0], c["lines"][0]["points"].split()[-1]
    assert first.startswith("0.0,") and last.startswith("1000.0,")
    assert [t["label"] for t in c["ticks"]] == ["1%", "2%", "3%"]
    ends = sorted(c["ends"], key=lambda e: e["label_y"])
    assert ends[1]["label_y"] - ends[0]["label_y"] >= tour.END_GAP - 1e-9    # 3.0 and 2.9 end close together
    assert [e["text"] for e in c["ends"]] == ["3.0%", "2.9%"] or [e["text"] for e in c["ends"]] == ["2.9%", "3.0%"]
    years = [y["label"] for y in c["years"]]
    assert years == [2019, 2020] and c["years"][-1]["wide"] and c["years"][-1]["narrow"]
    # a rate that moves in steps draws flat lines between its moves
    s = tour.line_chart([{"name": "R", "s": monthly([2.0, 2.0, 2.25]), "slot": 1, "step": True}], "%", 2)
    assert len(s["lines"][0]["points"].split()) == 5


def test_year_labels_thin_out_but_always_name_the_last_year():
    c = tour.line_chart([{"name": "A", "s": monthly(np.arange(19 * 12.0), start="2008-01-01"), "slot": 1}], "", 0)
    wide = [y["label"] for y in c["years"] if y["wide"]]
    narrow = [y["label"] for y in c["years"] if y["narrow"]]
    assert wide[-1] == narrow[-1] == 2026 and len(wide) <= tour.LABELS_WIDE and len(narrow) <= tour.LABELS_NARROW


def test_stacked_bars_go_up_and_down_from_zero():
    periods = list(pd.date_range("2025-01-01", periods=4, freq="QS"))
    c = tour.bar_chart(periods, [{"name": "Home", "values": [2.0, 3.0, 1.0, 2.0], "slot": 1},
                                 {"name": "Abroad", "values": [-1.0, 0.5, -0.5, None], "slot": 2}],
                       "Q", "pp", 1, line={"name": "Total", "values": [1.0, 3.5, 0.5, 2.0]})
    assert len(c["rects"]) == 7 and sum(r["neg"] for r in c["rects"]) == 2
    zero = c["zero"]
    home = [r for r in c["rects"] if r["slot"] == 1]
    assert all(abs(r["y"] + r["h"] - zero) < 0.02 for r in home)            # they stand on the zero line
    abroad_neg = [r for r in c["rects"] if r["neg"]]
    assert all(abs(r["y"] - zero) < 0.02 for r in abroad_neg)               # and hang from it
    assert c["rects"][0]["title"] == "Home, Q1 2025: +2.0 pp"
    assert len(c["line"].split()) == 4 and [y["label"] for y in c["years"]] == [2025]


def test_a_chapter_is_written_from_the_data(tmp_path):
    store = Store(tmp_path / "data")
    store.save_series("afiliados", monthly(np.r_[np.linspace(19000.0, 22000.0, 94), 22624.2], start="2018-12-01"))
    store.save_series("ecb_deposit_rate", pd.Series([2.0, 2.0, 2.25, 2.5],
                                                    index=pd.to_datetime(["2025-06-11", "2026-01-05", "2026-06-17", "2026-09-16"])))
    store.save_series("hicp_euro_area", monthly(np.linspace(2.0, 4.0, 94)))
    data = Data(load_registry(), store)
    snap = {"afiliados": {"values": [{"transform": "diff_yoy", "display": "+784.6k"}]}}
    links = {"labour": [("labour.html#a", "A"), ("labour.html#b", "B")]}
    got = tour.chapters(data, snap, SECTION_PAGES, links)
    assert [c["id"] for c in got] == ["labour", "ecb"]          # the others have no data here and are left out
    labour, ecb = got
    assert labour["n"] == "01" and labour["area"] == "Labour market" and labour["page"] == "labour.html"
    assert labour["big"] == "22.62" and labour["big_unit"] == "million" and labour["links"] == links["labour"]
    assert labour["sentence"] == "Social Security registrations reached a record in Oct 2026, +784.6k on a year earlier."
    assert labour["explore"] == "Explore Labour market" and labour["chart"]["kind"] == "lines"
    assert ecb["n"] == "02" and ecb["big"] == "2.50%" and ecb["sentence"] == "Raised by 0.25 points on 16 Sep 2026."
    with i18n.using("es"):
        es = tour.chapters(data, snap, SECTION_PAGES, links)
    assert es[0]["sentence"].startswith("La afiliación a la Seguridad Social marcó un récord en oct 2026")
    assert es[1]["sentence"] == "Subido 0.25 puntos el 16 sept 2026." or es[1]["sentence"].startswith("Subido 0.25 puntos el 16 ")
