"""Build the static site in site/ from templates/, static/ and the stored data.

Pages are rendered in Python (Jinja2), so the content is plain HTML. Data for the
charts is written as .js files (window.EP = ...) and loaded with <script> tags,
because browsers block fetch() of .json files on pages opened from disk (file://).
A .json copy of the snapshot is written alongside for anything that wants plain JSON.
"""

import json
import re
import shutil
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

import pandas as pd
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape

from . import __version__, analytics, budget, changes, disclaimer, ecbspeak, feed, fiscal, glance, hero, homepage, i18n, industries, peers, schedule, scoreboard, search, sectortables, stance, surprises, tools, tour, trade
from .i18n import _
from .charts import build_home_charts
from .config import GA_MEASUREMENT_ID, SITE_CONTACT, SITE_DIR, SITE_OWNER, SITE_URL, STATIC_DIR, TEMPLATES_DIR
from .pages import PAGES, block_indicator_ids, build_page, indicator_anchors
from .questions import four_questions
from .registry import Indicator
from .snapshot import build_snapshot
from .sources.base import MADRID, madrid_today
from .store import Store
from .tables import Data

# Section pages: title, one-line intro, and the batch that fills them in (see PLAN.md).
# What a filled page shows is defined in pages.py.
SECTION_PAGES = {
    "gdp": ("GDP", "What Spain produces, and who is spending: households, firms, government and the rest of the world.", 4),
    "labour": ("Labour market", "Jobs, unemployment and contracts by sector, from the Social Security register and the public employment service, INE's labour force survey (EPA), who works by age, sex, citizenship and education, the effect of an ageing population, worker flows, hours, vacancies and layoffs.", 4),
    "wages": ("Wages", "Pay and labour costs, how they compare with inflation, and pay by activity: a month, per hour, bonuses and growth.", 4),
    "inflation": ("Inflation", "Consumer prices on Spain's own index (IPC) and the harmonised index the ECB targets (IPCA), underlying inflation across the basket, and energy prices.", 4),
    "financial": ("Financial", "Spanish bond yields and the prima de riesgo, Euribor, the IBEX 35, the euro and commodities, and the IMF-style financial soundness indicators.", 5),
    "ecb": ("ECB", "Spain has no monetary policy of its own: the European Central Bank sets rates for the whole euro area. The IMF-style monetary table shows what that means for the Banco de España and Spanish banks.", 5),
    "fiscal": ("Fiscal", "Government deficit and debt, the IMF-style fiscal tables, and debt sustainability.", 6),
    "activity": ("Economic activity and external accounts", "Industry, retail, sentiment surveys, tourism, electricity demand, the external accounts and the IMF-style balance of payments and external debt tables; trade in goods and services has a page of its own.", 6),
    "housing": ("Housing", "House prices, affordability and rents, Spain against its comparators, building and households, sales, mortgages and credit, household wealth, and commercial property.", 6),
    "pensions": ("Pensions", "The Social Security's contributory pensions: how many and how much, by class, scheme and region, what they cost, new and ended pensions, and the maximum and minimum amounts; Spain against its comparators, the ageing population, the 2023 reform and what the official assessments say.", 29),
    "international": ("International", "Spain next to the euro area and ten comparators: France, Germany, Italy, the Netherlands, Portugal, Poland, the United Kingdom, the United States, Canada and Japan; growth, jobs, prices, public finances and the IMF's outlook.", 6),
    "regions": ("Regions", "The 17 autonomous communities: unemployment, house prices, inflation and income per head.", 6),
    "analysis": ("Analysis", "Macroscope's own readings: the economy against its history, data surprises, a GDP nowcast, what forecasters expect, the 10-year yield split in two, and Taylor rules.", 7),
}

NAV = ([("index.html", "Home")] + [(f"{s}.html", t) for s, (t, _, _) in SECTION_PAGES.items()]
       + [("sector-tables.html", "Sector tables"), ("tools.html", "Tools"), ("calendar.html", "Calendar"), ("data.html", "Data")])
# The Budget explorer opened on the autonomous communities (all of them together, and side by side).
COMMUNITIES_EXPLORER = ("budget-explorer.html#level=regions", "Budget explorer: the autonomous communities")
# What each tab's dropdown lists besides the sections of a section page (anchors or other pages).
NAV_EXTRA = {
    "index.html": [("#latest", "Latest releases"), ("#glance", "The economy at a glance"), ("#key-indicators", "Key indicators"),
                   ("#hero-title", "The economy today"), ("#tour", "Inside Macroscope"),
                   ("#chart-of-the-week", "Chart of the week"), ("#readings", "Macroscope readings"), ("#peers", "Spain and its peers"),
                   ("#outlook", "What forecasters expect"), ("#whats-new", "What's new"),
                   ("#four-questions", "The economy in four questions"), ("#charts", "Charts")],
    "tools.html": [("#trend", "Economy vs pre-COVID trend"), ("#taylor", "Taylor rule"), ("#rates", "Interest rate decomposer"),
                   ("fiscal-explorer.html", "Fiscal Explorer"), ("budget-explorer.html", "Budget explorer"),
                   COMMUNITIES_EXPLORER, ("ecb-speak.html", "ECB-speak"),
                   ("stance.html", "Global central bank stance")],
    "calendar.html": [("#release-map", "Release map"), ("#recent", "Released in the past week"),
                      ("#upcoming", "The next two months")],
    "sector-tables.html": [(f"#{section_id}", title) for section_id, title, *_ in sectortables.PAGE],
}
# Pages a section tab's dropdown lists after that page's own sections.
NAV_SUBPAGES = {"labour.html": [("industry-detail.html", "Every industry")],
                "fiscal.html": [("budget-explorer.html", "Budget explorer")],
                "activity.html": [("trade.html", "Trade in goods and services")],
                "regions.html": [COMMUNITIES_EXPLORER]}


def nav_items(section_pages: dict, updated: set[str] = frozenset()) -> list[dict]:
    """The tabs, each with the sections its dropdown links to (`new` for those in `updated`, a set of
    "page.html#section" with figures from the past week)."""
    items = []
    for href, label in NAV:
        section = href.removesuffix(".html")
        if section in section_pages:
            children = [(f"#{b['id']}", b["title"]) for b in section_pages[section]["blocks"]] + NAV_SUBPAGES.get(href, [])
        else:
            children = NAV_EXTRA.get(href, [])
        items.append({"href": href, "label": _(label), "id": section,
                      "children": [{"href": (link := c if not c.startswith("#") else href + c), "title": _(t),
                                    "new": link in updated} for c, t in children]})
    return items


def write_data_js(path: Path, name: str, data) -> None:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f"window.EP = window.EP || {{}};\nwindow.EP.{name} = {payload};\n", encoding="utf-8")


def _madrid_time(iso: str | None, zone: bool = True) -> str:
    """"2 Nov 2026, 18:42 Madrid time" (without the zone: "2 Nov 2026, 18:42")."""
    if not iso:
        return _("never")
    t = datetime.fromisoformat(iso).astimezone(MADRID)
    return f"{i18n.day_month_year(t)}, {t:%H:%M}" + (f" {_('Madrid time')}" if zone else "")


def _source_summary(items: list[dict]) -> list[dict]:
    rows: dict[str, dict] = {}
    for item in items:
        row = rows.setdefault(item["source"], {"source": item["source"], "total": 0, "ok": 0, "problems": 0,
                                               "fetched_at": None})
        row["total"] += 1
        if item["status"] == "ok" and not item["out_of_date"]:
            row["ok"] += 1
        else:
            row["problems"] += 1
        if item["fetched_at"] and (row["fetched_at"] is None or item["fetched_at"] > row["fetched_at"]):
            row["fetched_at"] = item["fetched_at"]
    for row in rows.values():
        row["fetched"] = _madrid_time(row["fetched_at"], zone=False)
    return sorted(rows.values(), key=lambda r: -r["total"])


def web_analytics(ga_id: str | None = GA_MEASUREMENT_ID, owner: str | None = SITE_OWNER,
                  contact: str | None = SITE_CONTACT) -> dict | None:
    """Google Analytics for the templates: the banner, static/consent.js and the privacy notice. None, so no banner and
    no analytics, until the measurement ID, the site's owner and a contact are all set in config.py."""
    if not (ga_id and owner and contact):
        return None
    if not re.fullmatch(r"G-[A-Z0-9]{4,16}", ga_id):
        raise ValueError(f"GA_MEASUREMENT_ID should look like G-XXXXXXXXXX, not {ga_id!r}")
    if not contact.startswith(("https://", "mailto:")):
        raise ValueError("SITE_CONTACT should be a link: https://... or mailto:...")
    label = contact.removeprefix("mailto:") if contact.startswith("mailto:") else contact.removeprefix("https://").rstrip("/")
    return {"id": ga_id, "path": urlparse(SITE_URL).path or "/", "owner": owner, "contact": contact, "contact_label": label}


def _copy_assets(site_dir: Path) -> None:
    # static/ holds Plotly's basic bundle (line, bar and pie charts, all the site draws), so the site works
    # offline with no CDN; it replaced the full bundle in Batch U4. Remove a full one left by older builds.
    shutil.copytree(STATIC_DIR, site_dir / "assets", dirs_exist_ok=True)
    (site_dir / "assets" / "plotly.min.js").unlink(missing_ok=True)


def build_site(indicators: list[Indicator], store: Store | None = None, site_dir: Path = SITE_DIR,
               languages: tuple[str, ...] = i18n.LANGUAGES) -> Path:
    """The site in English at site_dir, and in Spanish under site_dir/es (they share site_dir/assets)."""
    store = store or Store()
    _copy_assets(site_dir)
    i18n.missing.clear()
    index = None
    for lang in languages:
        with i18n.using(lang):
            page = _build_language(indicators, store, site_dir, lang)
        index = index or page
    return index


def _counterpart(filename: str, lang: str) -> str:
    """The same page in the other language, from this one."""
    return f"es/{filename}" if lang == "en" else f"../{filename}"


def _build_language(indicators: list[Indicator], store: Store, site_root: Path, lang: str) -> Path:
    site_dir = site_root if lang == "en" else site_root / lang
    root = "" if lang == "en" else "../"          # where assets/, the feed and the workbook are, from a page
    snapshot = build_snapshot(indicators, store)
    items = snapshot["indicators"]
    by_id = {i["id"]: i for i in items}
    charts = build_home_charts(indicators, store)
    snapshot["questions"] = four_questions(indicators, store)
    readings_data = Data(indicators, store)
    snapshot["readings"] = analytics.home_facts(readings_data) + surprises.surprise_facts(readings_data)

    data_dir = site_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    write_data_js(data_dir / "snapshot.js", "snapshot", snapshot)
    write_data_js(data_dir / "charts.js", "charts", charts)
    (data_dir / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")

    # The build stamp goes on every asset URL so browsers never show a cached, older snapshot.
    build_id = "".join(ch for ch in snapshot["generated_at"] if ch.isdigit())[:14]
    # A page with much prose has a Spanish template of its own (templates/es/); the rest mark text with _().
    loaders = [FileSystemLoader(TEMPLATES_DIR / lang)] if lang != "en" else []
    env = Environment(loader=ChoiceLoader(loaders + [FileSystemLoader(TEMPLATES_DIR)]), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.i18n"])
    env.install_gettext_callables(gettext=_, ngettext=i18n.ngettext, newstyle=True)
    section_pages = {s: build_page(s, indicators, store) for s in SECTION_PAGES}   # the navigation lists their sections
    # Sections with figures from the past week get an "updated" mark, also in the tabs' dropdowns.
    today = pd.Timestamp(madrid_today())
    events = schedule.releases(store, today)
    fresh = changes.fresh_series(store, by_id, events, today)
    labels = {i["id"]: i["label"] for i in items}
    updated = set()
    for section, page in section_pages.items():
        definitions = {b["id"]: b for b in PAGES.get(section, [])}
        for block in page["blocks"]:
            block["updated"] = changes.updated_mark(block_indicator_ids(definitions[block["id"]]), fresh, labels)
            if block["updated"]:
                updated.add(f"{section}.html#{block['id']}")
    trade_parts: dict[str, list[str]] = {}
    for ind_id in fresh:
        if (part := trade.indicator_section(ind_id)):
            trade_parts.setdefault(part, []).append(ind_id)
    trade_updated = {part: changes.updated_mark(ids, fresh, labels) for part, ids in trade_parts.items()}
    updated |= {f"trade.html#{part}" for part in trade_updated} | ({"trade.html"} if trade_updated else set())
    # Links to a release go to the section that shows its figures.
    anchors = _search_anchors(section_pages, items)

    def section_link(ids: list[str], page: str) -> str:
        return next((anchors[i][0] for i in ids if i in anchors), page)

    coming = schedule.coming_up(store)
    for entry in coming["today_items"] + coming["items"]:
        entry["page"] = section_link(entry["ids"], entry["page"])
    common = {
        "version": __version__,
        "build_id": build_id,
        "built": _madrid_time(snapshot["generated_at"]),
        "as_of": _madrid_time(snapshot["data_as_of"], zone=False),
        "sources": list(dict.fromkeys(_(i.source_name) for i in indicators if not i.is_derived)),
        "lang": lang,
        "root": root,
        "brand": f"Macroscope {_('Spain')}",
        "site_url": SITE_URL,
        "nav": nav_items(section_pages, updated),
        "coming_up": coming,
        "ga": web_analytics(),
        "disclaimer": disclaimer.context(SITE_OWNER, SITE_CONTACT),
    }

    def render(template: str, filename: str, **context) -> Path:
        path = site_dir / filename
        active = context.pop("active", filename)   # a tool page highlights "Tools" in the navigation
        counterpart = context.pop("counterpart", _counterpart(filename, lang))
        html = env.get_template(template).render(**common, active=active, page_file=filename,
                                                 counterpart=counterpart, **context)
        path.write_text(html, encoding="utf-8")
        return path

    recent = changes.recent_releases(store, by_id, events, today)
    for r in recent:
        r["page"] = section_link(r["ids"], r["page"])
    registry = {i.id: i for i in indicators}
    # When the site last got new or revised figures for each series: "Since your last visit" marks the tiles and
    # cards whose figures came in after the data the reader last saw.
    changed = homepage.changed_times(store)
    # The home page opens with the past fortnight's releases (which take the place of its list of the past week's).
    latest = homepage.latest_releases(store, by_id, registry, events, today, changed=changed)
    for card in latest:
        card["page"] = section_link(card["ids"], card["page"])
    tiles = [homepage.tile_extras(store, by_id[t], registry[t], fresh, changed) for t in snapshot["tiles"]]
    week = homepage.chart_of_the_week(store, by_id, registry, events, today)
    if week:
        week["spec"]["link"] = section_link(week["ids"], week["spec"]["link"])
        # Drawn from the home page's charts file, but kept out of the search index: it changes every week.
        write_data_js(data_dir / "charts.js", "charts", charts + [week["spec"]])
    at_a_glance = {"heatmap": glance.heatmap(readings_data), "records": glance.records(readings_data, tiles)}
    for record in at_a_glance["records"]:
        record["page"] = section_link([record["id"]], record["page"])
    whats_new = changes.latest_notes(store)
    for note in whats_new["notes"]:
        note["page"] = section_link([note["id"]], note["page"])
        note["text"] = changes.note_text(note, registry.get(note["id"]))
    for key in ("at", "updated_at", "started_at"):
        whats_new[key] = _madrid_time(whats_new[key], zone=False) if whats_new[key] else None
    snap_by_id = {i["id"]: i for i in snapshot["indicators"]}
    opening = hero.hero(readings_data, snap_by_id)
    # The tour (batches L4-L5): a chapter per area, linking to the first sections of its page.
    tour_links = {s: [(f"{s}.html#{b['id']}", _(b["title"])) for b in section_pages[s]["blocks"]] for s in section_pages}
    chapters = tour.chapters(readings_data, snap_by_id, SECTION_PAGES, tour_links)
    index = render("index.html", "index.html", tiles=tiles, latest=latest, week=week, built_at=snapshot["generated_at"], glance=at_a_glance,
                   hero=opening, chapters=chapters,
                   peers=scoreboard.peer_table(readings_data), outlook=scoreboard.outlook(readings_data),
                   questions=snapshot["questions"], charts=charts, readings=snapshot["readings"],
                   whats_new=whats_new)
    page_charts = [("index.html", _("Home"), charts)]      # (page, title, charts), for the site search
    for section, (title, intro, batch) in SECTION_PAGES.items():
        title, intro = _(title), _(intro)
        page = section_pages[section]
        page_charts.append((f"{section}.html", title, page["charts"]))
        charts_file = None
        if page["charts"]:
            charts_file = f"data/charts-{section}.js"
            write_data_js(site_dir / charts_file, "charts", page["charts"])
        render("section.html", f"{section}.html", page={"title": title, "intro": intro, "batch": batch},
               blocks=page["blocks"], charts_file=charts_file, picker=peers.picker() if section in ("international", "housing", "pensions") else None,
               items=[i for i in items if i["section"] == section], subpages=NAV_SUBPAGES.get(f"{section}.html", []),
               note=disclaimer.page_note(section))
    groups = [{"id": s, "title": _(t), "items": [i for i in items if i["section"] == s]} for s, (t, *_rest) in SECTION_PAGES.items()]
    attention = [i for i in items if i["status"] != "ok" or i["out_of_date"]]
    # The Excel workbook is in English only: the Spanish pages link to the English one.
    workbook = (sectortables.write_workbook(readings_data, data_dir / sectortables.WORKBOOK, built=common["built"]) if lang == "en"
                else (site_root / "data" / sectortables.WORKBOOK).exists())
    detail = industries.page(readings_data)
    if detail["charts"]:
        write_data_js(data_dir / "charts-industries.js", "charts", detail["charts"])
    render("industry-detail.html", "industry-detail.html", active="labour.html", table=detail["table"],
           sections=detail["sections"], moves=detail["moves"],
           charts_file="data/charts-industries.js" if detail["charts"] else None)
    page_charts.append(("industry-detail.html", _("Every industry"), detail["charts"]))
    goods = trade.page(readings_data)
    page_charts.append(("trade.html", _("Trade"), goods["charts"]))
    if goods["charts"]:
        write_data_js(data_dir / "charts-trade.js", "charts", goods["charts"])
    render("trade.html", "trade.html", active="activity.html", facts=goods["facts"], table=goods["table"], overview=goods["overview"],
           rankings=goods["rankings"], extras=goods["extras"], sections=goods["sections"], chapters=goods["chapters"], page_nav=trade.PAGE,
           updated=trade_updated,
           charts_file="data/charts-trade.js" if goods["charts"] else None)
    sector = sectortables.page(readings_data)
    page_charts.append(("sector-tables.html", _("Sector tables"), sector["charts"]))
    if sector["charts"]:
        write_data_js(data_dir / "charts-sectortables.js", "charts", sector["charts"])
    render("sector-tables.html", "sector-tables.html", sections=sector["sections"],
           charts_file="data/charts-sectortables.js" if sector["charts"] else None,
           workbook=f"{root}data/{sectortables.WORKBOOK}" if workbook else None)
    render("data.html", "data.html", source_summary=_source_summary(items), groups=[g for g in groups if g["items"]],
           attention=attention, total=len(items), workbook=f"{root}data/{sectortables.WORKBOOK}" if workbook else None,
           sector_tables=[(f"{t.section}.html#{t.block}", sectortables.table_title(t)) for t in sectortables.TABLES])
    days = schedule.window(store, today)
    for day in days:
        for e in day["events"]:
            e["page"] = section_link(e.get("ids", []), e["page"])
    ahead = schedule.window(store, today, before=0, after=schedule.MAP_AHEAD)
    for day in ahead:
        for e in day["events"]:
            e["page"] = section_link(e.get("ids", []), e["page"])
    months = schedule.month_grids(ahead, today)
    render("calendar.html", "calendar.html", days=days, recent=recent, months=months, today_iso=f"{today:%Y-%m-%d}",
           weekday_heads=[_(w) for w in ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")],
           map_open=schedule.first_open(months, datetime.now(MADRID)), calendar_page=schedule.INE_CALENDAR_PAGE)
    counts = {}
    for i in items:
        counts[i["source"]] = counts.get(i["source"], 0) + 1
    render("about.html", "about.html", total=len(items), source_counts=sorted(counts.items(), key=lambda kv: -kv[1]))
    if lang == "en":                  # GitHub Pages serves the root's 404 page for any address
        render("404.html", "404.html", active="", site_path=urlparse(SITE_URL).path or "/", counterpart="es/index.html")
    # The feed in each language (Batch 33d): site/feed.xml and site/es/feed.xml.
    (site_dir / feed.FEED_FILE).write_text(feed.build_feed(store, registry=registry), encoding="utf-8", newline="\n")
    write_data_js(data_dir / "tools.js", "tools", tools.tools_data(Data(indicators, store)))
    render("tools.html", "tools.html", taylor_defaults={"r_star": analytics.R_STAR}, note=disclaimer.page_note("tools"))
    fx = fiscal.explorer_data(Data(indicators, store))
    if fx:
        write_data_js(data_dir / "fiscal.js", "fiscal", fx)
    render("fiscal-explorer.html", "fiscal-explorer.html", active="tools.html", fx=fx,
           s1_check=fx["s1_check"] if fx else None, past_groups=fiscal.past_groups(fx["history"]) if fx else [])
    bx = budget.explorer_data(store, Data(indicators, store))
    if bx:
        write_data_js(data_dir / "budget.js", "budget", bx)
        bx = dict(bx, fetched_day=budget.fetched_day(bx), provisional_note=budget.provisional_note(bx))
    render("budget-explorer.html", "budget-explorer.html", active="fiscal.html", bx=bx)
    speak = ecbspeak.page(store)
    if speak:
        write_data_js(data_dir / "charts-ecbspeak.js", "charts", speak["charts"])
        with open(data_dir / "charts-ecbspeak.js", "a", encoding="utf-8") as f:
            f.write("window.EP.speakRelative = " + json.dumps(speak["relative"], ensure_ascii=False, separators=(",", ":")) + ";\n")
    render("ecb-speak.html", "ecb-speak.html", active="tools.html", p=speak, charts=speak["charts"] if speak else [],
           charts_file="data/charts-ecbspeak.js" if speak else None, ecb_page=ecbspeak.ECB_SPEECHES,
           bis_page=ecbspeak.BIS_ARCHIVE_PAGE)
    stance_charts = stance.charts(store)
    if stance_charts:
        write_data_js(data_dir / "charts-stance.js", "charts", stance_charts)
    render("stance.html", "stance.html", active="tools.html", s=stance.page(store), charts=stance_charts,
           charts_file="data/charts-stance.js" if stance_charts else None,
           econvitals_page=stance.PAGE, econvitals_terms=stance.TERMS)
    page_charts += [("ecb-speak.html", _("ECB-speak"), speak["charts"] if speak else []),
                    ("stance.html", _("Central bank stance"), stance_charts or [])]
    # Trade is no longer a tab of its own (it sits under Economic activity), but its sections stay searchable.
    trade_tab = {"href": "trade.html", "label": _("Trade"), "children": [{"href": f"trade.html#{s}", "title": _(t)} for s, t in trade.PAGE]}
    write_data_js(data_dir / "search.js", "search",
                  search.build_index(common["nav"] + [trade_tab], page_charts, items, anchors))
    return index


def _search_anchors(section_pages: dict, items: list[dict]) -> dict[str, tuple[str, str]]:
    """Indicator id -> (where the site shows it, that page's title), for the site search."""
    titles = {f"{s}.html": _(t) for s, (t, *_rest) in SECTION_PAGES.items()}
    home = {item["id"]: item["section"] for item in items}
    anchors = {i: (href, titles[href.split("#")[0]]) for i, href in indicator_anchors(section_pages, home).items()}
    for item in items:
        ind_id = item["id"]
        if ind_id in anchors:
            continue
        if (part := trade.indicator_section(ind_id)):
            anchors[ind_id] = (f"trade.html#{part}", _("Trade"))
        elif ind_id.startswith("ind_"):
            anchors[ind_id] = (f"industry-detail.html#fig-{ind_id.replace('_', '-')}", _("Every industry"))
    return anchors
