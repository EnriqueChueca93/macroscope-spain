"""The economy at a glance on the home page: the heat map and the records (econpulse/glance.py)."""

import numpy as np
import pandas as pd

from econpulse import glance, i18n
from econpulse.registry import Indicator
from econpulse.store import Store
from econpulse.tables import Data


def ind(**kw):
    base = dict(label=kw["id"], label_es=kw["id"], section="inflation", source="fake", key=kw["id"], freq="M", unit="%")
    return Indicator(**{**base, **kw})


def test_shade_steps_and_compact_numbers():
    assert [glance.shade(z) for z in (0.2, -0.49, 0.5, 1.0, 2.5, -0.7, -1.5, -3.0)] == \
        ["mid", "mid", "hot1", "hot2", "hot3", "cool1", "cool2", "cool3"]
    assert glance.shade(None) == glance.shade(float("nan")) == "none"
    assert [glance._compact(v) for v in (4.94, -0.44, -0.04, 105.2, 1234.0)] == ["4.9", "−0.4", "0.0", "105", "1,234"]


def _data(tmp_path):
    store = Store(tmp_path / "data")
    months = pd.date_range("2013-01-01", "2026-10-01", freq="MS")
    rng = np.random.default_rng(1)
    hicp = pd.Series(2 + rng.normal(0, 0.5, len(months)), index=months)
    hicp.iloc[-1] = 6.0                                         # far above its normal
    store.save_series("hicp", hicp)
    store.save_series("hicp_core", hicp.iloc[:-1])              # October not out yet
    quarters = pd.date_range("2013-01-01", "2026-07-01", freq="QS")
    store.save_series("gdp", pd.Series(100 * 1.005 ** np.arange(len(quarters)), index=quarters))
    regs = pd.Series(np.linspace(16000, 22600, len(months)), index=months)
    store.save_series("afiliados", regs)
    inds = [ind(id="hicp", label="HICP inflation"), ind(id="hicp_core", label="Core HICP inflation"),
            ind(id="gdp", freq="Q", unit="index", section="gdp"),
            ind(id="afiliados", unit="thousands", decimals=1, section="labour", label="Registrations", tile=1)]
    return Data(inds, store)


def test_heatmap_rows_cells_and_quarters(tmp_path):
    hm = glance.heatmap(_data(tmp_path))
    assert hm["through"] == "Oct 2026" and len(hm["months"]) == 12
    assert hm["months"][0]["year"] == 2025 and hm["months"][2] == {**hm["months"][2], "mon": "Jan", "year": 2026}
    inflation = next(b for b in hm["blocks"] if b["id"] == "inflation")
    hicp, core = inflation["rows"][:2]
    assert hicp["cells"][-1]["shade"] == "hot3" and hicp["cells"][-1]["text"] == "6.0"
    assert hicp["cells"][-1]["title"].startswith("HICP inflation, Oct 2026: 6.0%; score +3.0, hotter than normal")
    assert core["cells"][-1] == {**core["cells"][-1], "shade": "none", "text": ""} and "not out yet" in core["cells"][-1]["title"]
    assert inflation["overall"]["label"] == "Inflation, overall score" and inflation["overall"]["cells"][-1]["text"].startswith("+")
    activity = next(b for b in hm["blocks"] if b["id"] == "activity")
    gdp = next(r for r in activity["rows"] if r["label"] == "Real GDP, q/q")
    # Nov 2025 to Oct 2026: two months of Q4 2025, three quarters, one month of Q4 2026 (not out yet)
    assert [c["span"] for c in gdp["cells"]] == [2, 3, 3, 3, 1] and sum(c["span"] for c in gdp["cells"]) == 12
    assert gdp["cells"][-1]["shade"] == "none" and gdp["cells"][-2]["text"] == "0.5"
    with i18n.using("es"):
        es = glance.heatmap(_data(tmp_path))
        assert es["through"] == "oct 2026"
        assert next(b for b in es["blocks"] if b["id"] == "inflation")["overall"]["label"] == "Inflación, puntuación global"


def test_every_row_links_to_a_page():
    # A calculated row (the month's average electricity demand) links to its input's page, not to "None"
    from econpulse.analytics import ACTIVITY, INFLATION
    from econpulse.charts import source_page
    from econpulse.registry import load_registry
    by_id = {i.id: i for i in load_registry()}
    assert by_id["electricity_demand_monthly"].source_url() is None
    assert source_page(by_id["electricity_demand_monthly"], by_id) == "https://www.ree.es/es/datos/demanda"
    assert source_page(by_id["cpi"], by_id) == by_id["cpi"].source_url()
    assert all(source_page(by_id[c.id], by_id) for c in ACTIVITY + INFLATION)


def test_records_need_two_years_and_count_people_in_millions(tmp_path):
    data = _data(tmp_path)
    tiles = [{"id": "afiliados", "headline": {"transform": "level"}}]
    out = glance.records(data, tiles)
    regs = next(r for r in out if r["id"] == "afiliados")
    assert regs["value"] == "22.60 million" and regs["up"] and regs["when"] == "Oct 2026"
    assert regs["text"] == "The highest in the series, which starts in 2013"
    tiles.append({"id": "hicp", "headline": {"transform": "level"}})
    months = pd.date_range("2013-01-01", "2026-10-01", freq="MS")

    def hicp_record(peak):
        hicp = pd.Series(2.0, index=months)
        hicp[peak], hicp.iloc[-1] = 3.0, 2.8
        data.store.save_series("hicp", hicp)
        return next((r for r in glance.records(data, tiles) if r["id"] == "hicp"), None)

    assert hicp_record("2025-08-01") is None             # the highest in 14 months only: not a record
    found = hicp_record("2023-08-01")
    assert found["text"] == "The highest since Aug 2023" and found["value"] == "2.8%"
    assert [r["id"] for r in glance.records(data, tiles)] == ["afiliados", "hicp"]    # the longest reach first


def test_the_home_page_shows_the_map_and_the_records(tmp_path):
    from econpulse.build import build_site
    data = _data(tmp_path)
    data.store.save_catalog({i: {"status": "ok", "fetched_at": "2026-11-04T12:00:00+00:00"} for i in data.by_id})
    build_site(list(data.by_id.values()), data.store, site_dir=tmp_path / "site", languages=("en",))
    html = (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
    section = html.split('id="glance"')[1].split("</section>")[0]
    assert section.count('<tr class="gl-overall">') == 2 and 'class="gl gl-hot3"' in section
    assert 'colspan="3"' in section and 'class="gl gl-none"' in section
    assert '<a class="record-label" href="labour.html' in section and "22.60 million" in section
    assert 'href="index.html#glance"' in html             # in the Home tab's menu
