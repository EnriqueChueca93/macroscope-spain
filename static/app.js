// Macroscope Spain: theme toggle and charts.
// Pages are plain HTML; this script only adds the light/dark switch and draws the
// charts from window.EP.charts (written by `python -m econpulse build`).
(function () {
  "use strict";

  var root = document.documentElement;
  var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

  // The page's language (Batch 33a: the Spanish site is under es/), and its words for what this script writes.
  var LANG = root.lang === "es" ? "es" : "en";
  var ES = {
    "Time range": "Periodo", "All": "Todo", "All the data": "Todos los datos", "Item": "Concepto", "Change": "Variación",
    "Member": "Miembro", "Stance": "Orientación", "Latest": "Último", "Range over the year": "Rango en el año",
    "Lowest over the year": "Mínimo del año", "Highest over the year": "Máximo del año", "Date": "Fecha", "Period": "Periodo",
    "All points.": "Todos los puntos.", "Latest 12 periods.": "Últimos 12 periodos.", "Link copied": "Enlace copiado",
    "Copy this link:": "Copie este enlace:", "Page": "Página", "Section": "Sección", "Chart": "Gráfico", "Series": "Serie",
    "Loading the index…": "Cargando el índice…", "The search index could not be loaded.": "No se pudo cargar el índice de búsqueda.",
    "On this page": "En esta página", "Sections of this page": "Secciones de esta página", "Top": "Arriba",
    "Back to the top of the page": "Volver al principio de la página", "Reading": "Lectura", " to ": " a ",
    "Copy a link to the section": "Copiar un enlace a la sección", "Countries": "Países", "Security": "Valor", "Group": "Grupo", "Index": "Índice"
  };
  function t(s) { return LANG === "es" && ES[s] !== undefined ? ES[s] : s; }

  // A feature event for Google Analytics (static/consent.js): what was used, never what was typed. It does nothing
  // unless analytics is switched on and the visitor accepted its cookies.
  function track(name, params) { if (window.EPconsent) window.EPconsent.track(name, params); }

  // Switching language keeps the place on the page (a chart's anchor, an explorer's settings).
  Array.prototype.forEach.call(document.querySelectorAll(".lang-switch a"), function (a) {
    a.addEventListener("click", function () {
      if (location.hash && !a.hasAttribute("aria-current")) a.href = a.getAttribute("href").split("#")[0] + location.hash;
      if (!a.hasAttribute("aria-current")) track("language_switch", { to: a.getAttribute("hreflang") });
    });
  });

  function currentTheme() {
    return root.getAttribute("data-theme") || (darkQuery.matches ? "dark" : "light");
  }

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("ep-theme", next); } catch (e) { /* storage blocked: choice lasts this visit */ }
      drawAll();
    });
  }
  darkQuery.addEventListener("change", drawAll);

  // ---------------------------------------------------------------- forget my choices (About, Privacy)
  // Every choice the site remembers is in local storage under a key starting "ep-"; this clears them all.
  Array.prototype.forEach.call(document.querySelectorAll("[data-forget-choices]"), function (b) {
    b.addEventListener("click", function () {
      try {
        Object.keys(localStorage).forEach(function (k) { if (k.indexOf("ep-") === 0) localStorage.removeItem(k); });
      } catch (e) { /* storage blocked: nothing was kept */ }
      root.removeAttribute("data-theme");
      if (window.EPconsent) window.EPconsent.reset();   // the cookie answer went too: delete the cookies, ask again
      drawAll();
      var status = b.parentNode.querySelector(".forget-status");
      if (status) status.textContent = b.getAttribute("data-done") || "";
    });
  });

  // ---------------------------------------------------------------- tab dropdowns
  // Each tab's ▾ opens a list of the sections on that page. The lists live outside the scrolling
  // tab bar, so they are placed under their tab here. Hover opens them where there is a mouse.
  (function () {
    var open = null, timer = null, hover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    function place(item, menu) {
      var r = item.getBoundingClientRect(), w = menu.offsetWidth;
      menu.style.top = Math.round(r.bottom) + "px";
      menu.style.left = Math.round(Math.max(8, Math.min(r.left, window.innerWidth - w - 8))) + "px";
    }
    function close(focusCaret) {
      if (!open) return;
      open.menu.hidden = true;
      open.caret.setAttribute("aria-expanded", "false");
      if (focusCaret) open.caret.focus();
      open = null;
    }
    function show(item, focusFirst) {
      var caret = item.querySelector(".nav-caret"), menu = document.getElementById(item.getAttribute("data-menu"));
      if (!caret || !menu) return;
      if (open && open.menu === menu) return;
      close(false);
      menu.hidden = false;
      place(item, menu);
      caret.setAttribute("aria-expanded", "true");
      open = { item: item, caret: caret, menu: menu };
      if (focusFirst) { var first = menu.querySelector("a"); if (first) first.focus(); }
    }
    Array.prototype.forEach.call(document.querySelectorAll(".nav-item[data-menu^='menu']"), function (item) {
      var caret = item.querySelector(".nav-caret"), menu = document.getElementById(item.getAttribute("data-menu"));
      caret.addEventListener("click", function (e) {
        e.stopPropagation();
        if (open && open.item === item) close(false); else show(item, e.detail === 0);   // keyboard: focus the first link
      });
      if (hover) {
        [item, menu].forEach(function (el) {
          el.addEventListener("mouseenter", function () { clearTimeout(timer); timer = setTimeout(function () { show(item, false); }, 120); });
          el.addEventListener("mouseleave", function () { clearTimeout(timer); timer = setTimeout(function () { if (open && open.item === item) close(false); }, 250); });
        });
      }
      menu.addEventListener("keydown", function (e) {
        var links = Array.prototype.slice.call(menu.querySelectorAll("a")), i = links.indexOf(document.activeElement);
        if (e.key === "Escape") { e.preventDefault(); close(true); }
        else if (e.key === "ArrowDown") { e.preventDefault(); links[(i + 1) % links.length].focus(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); links[(i - 1 + links.length) % links.length].focus(); }
        else if (e.key === "Tab" && ((!e.shiftKey && i === links.length - 1) || (e.shiftKey && i === 0))) close(!e.shiftKey ? false : true);
      });
      menu.addEventListener("click", function (e) { if (e.target.closest("a")) close(false); });
    });
    document.addEventListener("click", function (e) { if (open && !open.menu.contains(e.target)) close(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(true); });
    window.addEventListener("resize", function () { close(false); });
    window.addEventListener("scroll", function () { if (open) place(open.item, open.menu); }, { passive: true });
    var bar = document.querySelector(".site-nav");
    if (bar) bar.addEventListener("scroll", function () { if (open) place(open.item, open.menu); }, { passive: true });
  })();

  // On phones the tab bar scrolls sideways: fade the edge where there are more tabs, and bring the
  // current page's tab into view.
  (function () {
    var bar = document.querySelector(".site-nav");
    if (!bar) return;
    function edges() {
      var scrollable = bar.scrollWidth > bar.clientWidth + 2;
      bar.classList.toggle("more-left", scrollable && bar.scrollLeft > 2);
      bar.classList.toggle("more-right", scrollable && bar.scrollLeft + bar.clientWidth < bar.scrollWidth - 2);
    }
    var current = bar.querySelector('[aria-current="page"]');
    if (current && bar.scrollWidth > bar.clientWidth + 2) {
      var item = current.closest(".nav-item") || current;
      if (item.offsetLeft + item.offsetWidth > bar.clientWidth) bar.scrollLeft = item.offsetLeft - 24;
    }
    edges();
    bar.addEventListener("scroll", edges, { passive: true });
    window.addEventListener("resize", edges);
  })();

  // ---------------------------------------------------------------- charts
  var specs = (window.EP && window.EP.charts) || [];
  var MONTHS = LANG === "es" ? ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
                               : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  // ---------------------------------------------------------------- chosen comparators (International page)
  // Charts flagged `pick` carry every country's series, tagged `country` (or `countries`, for a central
  // bank). The reader picks any number of comparators (Batch 34a): they are drawn beside Spain, which is in
  // text ink. Each country has its own colour and line style (econpulse/peers.py, COUNTRY_STYLE, on the
  // chips as data-slot and data-dash), the same whatever order it is picked in. Rankings flagged `pick`
  // colour the same countries and grey the others. The choice is remembered in this browser.
  var picker = document.getElementById("country-picker");
  var picked = [], pickStyle = {}, pickCodes = { Spain: "es" };
  var CSS_DASH = { solid: "solid", dash: "dashed", dot: "dotted" };

  function savePicks() {
    try { localStorage.setItem("ep-peers", JSON.stringify(picked)); } catch (e) { /* storage blocked: lasts this visit */ }
    track("countries_compared", { countries: picked.slice().sort().join(","), count: picked.length });
  }

  function togglePick(code) {
    var at = picked.indexOf(code);
    if (at >= 0) picked.splice(at, 1);
    else if (pickStyle[code]) picked.push(code);
  }

  function renderChips() {
    Array.prototype.forEach.call(document.querySelectorAll(".picker-chips .chip[data-country]"), function (b) {
      var code = b.getAttribute("data-country"), on = picked.indexOf(code) >= 0;
      b.setAttribute("aria-pressed", String(on));
      var swatch = b.querySelector(".chip-swatch");
      if (swatch) {   // a short stroke in the country's colour and line style; follows the theme
        swatch.style.borderTopColor = on ? "var(--series-" + pickStyle[code].slot + ")" : "";
        swatch.style.borderTopStyle = CSS_DASH[pickStyle[code].dash] || "solid";
      }
    });
    Array.prototype.forEach.call(document.querySelectorAll(".bar-countries-count"), function (n) {
      n.textContent = String(picked.length);
    });
  }

  if (picker) {
    Array.prototype.forEach.call(picker.querySelectorAll(".chip[data-country]"), function (b) {
      var code = b.getAttribute("data-country");
      pickCodes[b.textContent.trim()] = code;
      pickStyle[code] = { slot: +b.getAttribute("data-slot") || 1, dash: b.getAttribute("data-dash") || "solid" };
    });
    var savedPicks = null;
    try { savedPicks = JSON.parse(localStorage.getItem("ep-peers") || "null"); } catch (e) { /* no saved choice */ }
    (Array.isArray(savedPicks) ? savedPicks : (picker.getAttribute("data-default") || "").split(",")).forEach(function (c) {
      if (picker.querySelector('.chip[data-country="' + c + '"]') && picked.indexOf(c) < 0) togglePick(c);
    });
    renderChips();
  }

  function seriesCountries(s) { return s.countries || (s.country ? [s.country] : []); }

  // The series a `pick` chart shows: Spain's (in ink) and the chosen countries' (in their colours). Where none
  // of the chosen countries has a series (the spreads, for euro-area countries only), the chart's own
  // defaults are drawn in grey.
  function pickView(spec) {
    if (!picker) return spec;
    var isSpain = function (s) { return seriesCountries(s).indexOf("es") >= 0; };
    var chosen = function (s) { return seriesCountries(s).filter(function (c) { return picked.indexOf(c) >= 0; })[0]; };
    var series = spec.series.filter(function (s) { return isSpain(s) || chosen(s); }).map(function (s) {
      return Object.assign({}, s, isSpain(s) ? { color: "ink" } : { slot: pickStyle[chosen(s)].slot, dash: pickStyle[chosen(s)].dash });
    });
    if (series.every(isSpain) && spec.pick_default) {
      series = series.concat(spec.series.filter(function (s) {
        return !isSpain(s) && seriesCountries(s).some(function (c) { return spec.pick_default.indexOf(c) >= 0; });
      }).map(function (s) { return Object.assign({}, s, { color: "muted" }); }));
    }
    var rank = function (s) { return isSpain(s) ? -1 : picked.indexOf(chosen(s)) >= 0 ? picked.indexOf(chosen(s)) : 9; };
    series.sort(function (a, b) { return rank(a) - rank(b); });
    return Object.assign({}, spec, { series: series });
  }

  function token(name) {
    return getComputedStyle(root).getPropertyValue(name).trim();
  }

  // "%" and "k" attach to the number; other units ("pp", "€/MWh") follow after a space.
  function suffix(spec) {
    var u = spec.unit || "";
    return u === "%" || u === "k" ? u : (u ? " " + u : "");
  }

  function fmt(v, spec, signed) {
    var s = Math.abs(v).toLocaleString("en-GB", { minimumFractionDigits: spec.decimals, maximumFractionDigits: spec.decimals });
    var sign = v < 0 ? "−" : (signed && v > 0 ? "+" : "");
    return sign + s + suffix(spec);
  }

  function dateLabel(iso, freq) {
    var y = iso.slice(0, 4), m = parseInt(iso.slice(5, 7), 10);
    if (freq === "Q") return (LANG === "es" ? "T" : "Q") + (Math.floor((m - 1) / 3) + 1) + " " + y;
    if (freq === "D") return parseInt(iso.slice(8, 10), 10) + " " + MONTHS[m - 1] + " " + y;
    if (freq === "A") return y;
    return MONTHS[m - 1] + " " + y;
  }

  function hoverDate(spec) {
    if (spec.date_format) return spec.date_format;
    return spec.freq === "Q" ? "Q%q %Y" : spec.freq === "D" ? "%-d %b %Y" : spec.freq === "A" ? "%Y" : "%b %Y";
  }

  // Spanish month and day names on the charts' axes and in their hover labels; numbers keep the English format.
  if (LANG === "es" && window.Plotly && window.Plotly.register) {
    window.Plotly.register({ moduleType: "locale", name: "es", dictionary: {}, format: {
      days: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
      shortDays: ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
      months: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
               "noviembre", "diciembre"],
      shortMonths: ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
      date: "%d/%m/%Y", decimal: ".", thousands: "," } });
  }
  var CONFIG_BASE = {
    locale: LANG,
    displaylogo: false, responsive: true,
    modeBarButtonsToRemove: ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d",
      "resetScale2d", "toggleSpikelines", "hoverClosestCartesian", "hoverCompareCartesian"]
  };

  // Horizontal bars ranking regions or countries on one measure, largest first. One
  // colour (Spain, when listed among its peers, in text ink); a dotted reference line.
  function drawRanking(el, spec) {
    var s = spec.series[0];
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis");
    el.style.height = Math.max(220, s.x.length * 22 + 41 + Math.max(1, (spec.ref_lines || []).length) * 15) + "px";
    var format = ":." + spec.decimals + "f}" + suffix(spec);
    var traces = [{
      type: "bar", orientation: "h", x: s.y, y: s.x, showlegend: false,
      marker: { color: s.x.map(function (label) {
        if (label === spec.highlight) return ink;
        if (!spec.pick || !picker) return token("--series-1");
        var code = pickCodes[label];
        return picked.indexOf(code) >= 0 ? token("--series-" + pickStyle[code].slot) : token("--axis");
      }) },
      hovertemplate: "<b>%{x" + format + "</b>  %{y}<extra></extra>"
    }];
    var shapes = [], annotations = [];
    (spec.ref_lines || []).forEach(function (r, i) {
      shapes.push({ type: "line", yref: "paper", y0: 0, y1: 1, x0: r.y, x1: r.y, line: { color: ink2, width: 1, dash: r.dash || "dot" } });
      annotations.push({ x: r.y, xref: "x", y: 1, yref: "paper", yanchor: "bottom", yshift: i * 15, showarrow: false,
        text: r.label + " " + fmt(r.y, spec), font: { size: 11, color: ink2 } });
    });
    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 10, r: 18, t: annotations.length ? 9 + annotations.length * 15 : 8, b: 30 },
      hovermode: "closest", hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      yaxis: { type: "category", autorange: "reversed", automargin: true, fixedrange: true, ticks: "",
        tickfont: { color: ink2, size: 12 } },
      xaxis: { gridcolor: grid, zeroline: true, zerolinecolor: axis, fixedrange: true, tickfont: { color: muted },
        ticksuffix: suffix(spec), automargin: true },
      bargap: 0.3, barcornerradius: 3, shapes: shapes, annotations: annotations
    };
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    layout.height = parseInt(el.style.height, 10);   // the box's height: a chart drawn before keeps its old size otherwise
    window.Plotly.react(el, traces, layout, config);
  }

  // One measure against another over time (a Beveridge curve): a path of dated points,
  // the first and latest labelled.
  function drawXY(el, spec) {
    var s = spec.series[0], n = s.x.length;
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis"), color = token("--series-1");
    var unit = function (u) { return u === "%" || u === "k" ? u : (u ? " " + u : ""); };
    var hover = "<b>%{text}</b><br>" + spec.x_label + " %{x:.1f}" + unit(spec.x_unit) + "<br>" +
      spec.y_label + " %{y:.0f}" + unit(spec.y_unit) + "<extra></extra>";
    var traces = [
      { type: "scatter", mode: "lines+markers", x: s.x, y: s.y, text: s.text, hovertemplate: hover, showlegend: false,
        line: { color: color, width: 1.5 }, marker: { size: 6, color: color, line: { width: 1, color: surface } } },
      { type: "scatter", mode: "markers", x: [s.x[n - 1]], y: [s.y[n - 1]], hoverinfo: "skip", showlegend: false,
        marker: { size: 11, color: color, line: { width: 2, color: surface } } }
    ];
    var label = function (i, anchor) {
      return { x: s.x[i], y: s.y[i], text: s.text[i], showarrow: false, xanchor: anchor, xshift: anchor === "left" ? 9 : -9,
        font: { size: 11, color: ink2 } };
    };
    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 56, r: 18, t: 10, b: 44 }, hovermode: "closest", showlegend: false,
      hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      xaxis: { title: { text: spec.x_label + (spec.x_unit ? " (" + spec.x_unit + ")" : ""), font: { size: 12, color: ink2 } },
        gridcolor: grid, zeroline: false, linecolor: axis, fixedrange: true, tickfont: { color: muted } },
      yaxis: { title: { text: spec.y_label + (spec.y_unit ? " (" + spec.y_unit + ")" : ""), font: { size: 12, color: ink2 } },
        gridcolor: grid, zeroline: false, fixedrange: true, tickfont: { color: muted }, automargin: true },
      annotations: [label(0, "right"), label(n - 1, "left")]
    };
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    window.Plotly.react(el, traces, layout, config);
  }

  // A bubble scatter (Batch 34b, the State's bonds): one bubble per security, a date across, a value up and an
  // amount as the bubble's area; one colour per group, from the palette's first three slots (they stay apart
  // for every reader), with a surface ring so overlapping bubbles stay readable.
  function drawBubble(el, spec) {
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis");
    var biggest = Math.max.apply(null, spec.series.map(function (s) { return Math.max.apply(null, s.size); }));
    var widest = Math.max(16, Math.min(34, el.clientWidth / 18));   // the largest bubble: 34 px, less on a phone
    var sizeref = 2 * biggest / (widest * widest);
    var traces = spec.series.map(function (s, i) {
      var color = token("--series-" + (i + 1));
      return {
        type: "scatter", mode: "markers", name: s.name, x: s.x, y: s.y, text: s.text,
        customdata: s.size.map(function (v) { return [v]; }),
        marker: { size: s.size, sizemode: "area", sizeref: sizeref, sizemin: 3, color: color, opacity: 0.8,
                  line: { width: 1.5, color: surface } },
        hovertemplate: "<b>%{y:." + spec.decimals + "f}" + suffix(spec) + "</b>  %{text}<br>" + spec.x_title + " %{x|%d %b %Y} · " +
          spec.size_label + " %{customdata[0]:,.1f} " + (spec.size_unit || "") + "<extra>" + s.name + "</extra>"
      };
    });
    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 44, r: 18, t: 30, b: 30 }, hovermode: "closest", showlegend: true,
      legend: { orientation: "h", x: 0, xanchor: "left", y: 1.02, yanchor: "bottom", font: { size: 12, color: ink2 } },
      hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      xaxis: { type: "date", showgrid: false, showline: true, linecolor: axis, ticks: "", fixedrange: true,
        tickfont: { color: muted } },
      yaxis: { gridcolor: grid, zeroline: true, zerolinecolor: axis, fixedrange: true, tickfont: { color: muted },
        ticksuffix: suffix(spec), automargin: true, rangemode: "tozero" }
    };
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    window.Plotly.react(el, traces, layout, config);
  }

  // A heat map of tiles (Batch 34c, the Madrid exchange by sector): one tile per index, coloured on a diverging
  // scale by its move over the chosen period (rises blue, falls red, small moves grey; spec.bounds sets the steps),
  // with the period buttons above and a key below. Plain HTML, so the names and figures are text.
  function heatStep(v, bounds) {
    if (v === null || v === undefined) return "none";
    var n = bounds.filter(function (b) { return Math.abs(v) >= b; }).length;
    return n === 0 ? "mid" : (v > 0 ? "pos" : "neg") + n;
  }

  function drawTiles(el, spec) {
    var key = el.getAttribute("data-period") || spec.periods[0].key, bounds = spec.bounds[key];
    var make = function (tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text !== undefined) n.textContent = text;
      return n;
    };
    el.style.height = "auto";
    el.textContent = "";
    el.removeAttribute("role");      // the card marks charts as images; these tiles are text and buttons
    el.removeAttribute("aria-label");
    var periods = make("div", "tile-periods tool-controls");
    periods.setAttribute("role", "group");
    periods.setAttribute("aria-label", t("Period"));
    spec.periods.forEach(function (p) {
      var b = make("button", "tool-button", p.label);
      b.type = "button";
      b.setAttribute("data-tile-period", p.key);
      b.setAttribute("data-chart", spec.id);
      b.setAttribute("aria-pressed", String(p.key === key));
      periods.appendChild(b);
    });
    el.appendChild(periods);
    var grid = make("div", "heat-grid");
    spec.rows.forEach(function (r) {
      var v = r.values[key];
      var tile = make("div", "heat-tile heat-" + heatStep(v, bounds) + (r.index ? " heat-index" : ""));
      tile.appendChild(make("span", "heat-name", r.label));
      tile.appendChild(make("span", "heat-value", v === null || v === undefined ? "–" : fmt(v, spec, true)));
      grid.appendChild(tile);
    });
    el.appendChild(grid);
    var key_ = make("div", "heat-legend");
    var b = bounds, f = function (x) { return fmt(x, { decimals: x < 1 ? 2 : 0, unit: "" }); };
    [["neg3", "≤ −" + f(b[2]) + "%"], ["neg2", "−" + f(b[1]) + "%"], ["neg1", "−" + f(b[0]) + "%"], ["mid", "±" + f(b[0]) + "%"],
     ["pos1", "+" + f(b[0]) + "%"], ["pos2", "+" + f(b[1]) + "%"], ["pos3", "≥ +" + f(b[2]) + "%"]].forEach(function (s) {
      var item = make("span", "heat-key");
      item.appendChild(make("span", "heat-swatch heat-" + s[0]));
      item.appendChild(document.createTextNode(s[1]));
      key_.appendChild(item);
    });
    el.appendChild(key_);
  }

  // ---------------------------------------------------------------- the HICP basket (econpulse/basket.py)
  // One spec carries every item's annual rate and contribution by month since 2016 and its share of the basket
  // by year. The chart's state lives on its element: data-view (map | time), data-mode (growth | weight),
  // data-open (a category's code) and data-month (an index into spec.months; the latest when unset).
  function basketState(el, spec) {
    var k = parseInt(el.getAttribute("data-month"), 10), open = el.getAttribute("data-open") || "";
    if (!spec.cats.some(function (c) { return c[0] === open; })) open = "";
    return {
      view: el.getAttribute("data-view") === "time" ? "time" : "map",
      mode: el.getAttribute("data-mode") === "weight" ? "weight" : "growth",
      open: open, month: k >= 0 && k < spec.months.length ? k : spec.months.length - 1
    };
  }

  function basketYears(spec) { return Object.keys(spec.shares).sort(); }

  // A year's shares of the basket, % by item; while a year's weights aren't out, the latest year's before it.
  function basketShares(spec, year) {
    var years = basketYears(spec), before = years.filter(function (y) { return y <= year; });
    return spec.shares[before.length ? before[before.length - 1] : years[0]];
  }

  // Shades as on the heat maps: by the distance from the 2% target (spec.steps), or by share (spec.wsteps).
  function basketShade(spec, rate) {
    if (rate === null || rate === undefined) return "none";
    var gap = rate - spec.target;
    if (Math.abs(gap) < spec.steps[0]) return "mid";
    return (gap > 0 ? "hot" : "cool") + spec.steps.filter(function (s) { return Math.abs(gap) >= s; }).length;
  }

  function basketWeightShade(spec, share) {
    return 1 + spec.wsteps.filter(function (s) { return share >= s; }).length;
  }

  // Some items' contributions in month k, points; null when none has one.
  function basketSum(spec, idx, k) {
    var v = null;
    idx.forEach(function (i) {
      var c = spec.contribs[i][k];
      if (c !== null && c !== undefined) v = (v || 0) + c;
    });
    return v === null ? null : Math.round(v * 1000) / 1000;
  }

  // The map for month k: the categories, largest first, each with the items in that year's basket. A
  // category's contribution counts all its items, also any just out of the basket (they still add the rest of
  // last year's price change); its rate is the average of its items' rates, by weight.
  function basketMonth(spec, k) {
    var shares = basketShares(spec, spec.months[k].slice(0, 4)), by = {};
    var cats = spec.cats.map(function (c) {
      return (by[c[0]] = { code: c[0], name: c[1], full: c[2], weight: 0, idx: [], items: [], rated: 0, sum: 0 });
    });
    spec.items.forEach(function (it, i) {
      var g = by[it[0].slice(0, 4)], share = shares[i], rate = spec.rates[i][k], c = spec.contribs[i][k];
      if (!g) return;
      g.idx.push(i);
      if (!(share > 0)) return;
      if (rate === undefined) rate = null;
      g.weight += share;
      if (rate !== null) { g.rated += share; g.sum += share * rate; }
      g.items.push({ code: it[0], name: it[1], weight: share, rate: rate, contribution: c === undefined ? null : c,
                     shade: basketShade(spec, rate), wshade: basketWeightShade(spec, share) });
    });
    return cats.filter(function (g) { return g.items.length; }).map(function (g) {
      g.items.sort(function (a, b) { return b.weight - a.weight; });
      g.rate = g.rated ? Math.round(g.sum / g.rated * 10) / 10 : null;
      g.contribution = basketSum(spec, g.idx, k);
      g.shade = basketShade(spec, g.rate);
      return g;
    }).sort(function (a, b) { return b.weight - a.weight; });
  }

  // The parts stacked over time: the categories (or an open category's items) by their share of the latest
  // basket, the six largest and the rest together, muted. Colours follow this order, the same in both modes.
  function basketParts(spec, open) {
    var W = spec.words, years = basketYears(spec), shares = spec.shares[years[years.length - 1]], parts = [], by = {};
    spec.items.forEach(function (it, i) {
      if (open && it[0].slice(0, 4) !== open) return;
      var key = open ? it[0] : it[0].slice(0, 4);
      if (!by[key]) {
        var cat = !open && spec.cats.filter(function (c) { return c[0] === key; })[0];
        parts.push(by[key] = { name: open ? it[1] : (cat ? cat[1] : key), idx: [], share: 0 });
      }
      by[key].idx.push(i);
      by[key].share += shares[i] || 0;
    });
    parts.sort(function (a, b) { return b.share - a.share; });
    if (parts.length > 7) {
      var rest = { name: open ? W.rest_items : W.rest, idx: [] };
      parts.slice(6).forEach(function (p) { rest.idx = rest.idx.concat(p.idx); });
      parts = parts.slice(0, 6).concat([rest]);
    }
    if (parts.length === 7) parts[6].muted = true;
    return parts;
  }

  // The basket over time, as a spec for draw(): with Growth, each part's contribution to annual inflation month
  // by month, stacked, and the total as a line (the published headline rate, or the open category's sum); with
  // Weight, each part's share year by year, stacked to 100 (of the basket, or of the open category).
  function basketTime(spec, st) {
    var W = spec.words, parts = basketParts(spec, st.open), series = [];
    var cat = st.open && spec.cats.filter(function (c) { return c[0] === st.open; })[0];
    function style(p) { return p.muted ? "muted" : null; }
    // Items' names can be long ("Passenger transport by taxi and hired vehicle with driver"): the legend
    // cuts them at a word, the hover keeps them whole.
    function short(name) {
      if (name.length <= 30) return name;
      var cut = name.slice(0, 30), space = cut.lastIndexOf(" ");
      return (space > 12 ? cut.slice(0, space) : cut).replace(/[,;:]$/, "") + "…";
    }
    if (st.mode === "growth") {
      var x = spec.months.map(function (m) { return m + "-01"; }), all = [];
      parts.forEach(function (p) {
        all = all.concat(p.idx);
        series.push({ name: p.name, legend: short(p.name), kind: "bar", color: style(p), x: x,
                      y: spec.months.map(function (m, k) { return basketSum(spec, p.idx, k); }) });
      });
      series.push(cat ? { name: W.total_of.replace("{name}", cat[1]), kind: "line", color: "ink", x: x,
                          y: spec.months.map(function (m, k) { return basketSum(spec, all, k); }) }
                      : { name: W.headline, kind: "line", color: "ink", x: x, y: spec.headline, headline: true });
      return { id: spec.id, kind: "bar", stack: true, freq: "M", unit: W.pp, decimals: 2, signed: true,
               series: series, ref_lines: [] };
    }
    var years = basketYears(spec);
    function total(idx, y) { return idx.reduce(function (a, i) { return a + (spec.shares[y][i] || 0); }, 0); }
    var everything = [];
    parts.forEach(function (p) { everything = everything.concat(p.idx); });
    parts.forEach(function (p) {
      series.push({ name: p.name, legend: short(p.name), kind: "bar", color: style(p), x: years, y: years.map(function (y) {
        var whole = cat ? total(everything, y) : 100;
        return whole ? Math.round(total(p.idx, y) / whole * 10000) / 100 : null;
      }) });
    });
    return { id: spec.id, kind: "bar", stack: true, freq: "A", x_kind: "category", unit: "%", decimals: 1,
             series: series, ref_lines: [] };
  }

  // The basket's data table and CSV follow the chart: the month's items on the map, every period over time
  // (newest first). `raw` gives the CSV's plain dates and units in the headings.
  function basketTable(spec, raw) {
    var el = document.getElementById("chart-" + spec.id) || document.createElement("div");
    var W = spec.words, st = basketState(el, spec);
    if (st.view === "map") {
      var rows = [];
      basketMonth(spec, st.month).forEach(function (c) {
        c.items.forEach(function (n) { rows.push([c.full, n.name, n.weight, n.rate, n.contribution]); });
      });
      return { head: [W.category, W.item, W.weight_col, W.rate_col, W.contribution_col], rows: rows,
               formats: [null, null, [2, false], [1, true], [2, true]], note: W.month + ": " + spec.labels[st.month] };
    }
    var sub = basketTime(spec, st), growth = st.mode === "growth";
    return {
      head: [growth ? W.month : W.year].concat(sub.series.map(function (s) {
        return raw ? s.name + " (" + (s.headline || !growth ? "%" : W.pp) + ")" : s.name;
      })),
      rows: sub.series[0].x.map(function (x, i) {
        return [growth ? (raw ? spec.months[i] : spec.labels[i]) : x].concat(sub.series.map(function (s) { return s.y[i]; }));
      }).reverse(),
      formats: [null].concat(sub.series.map(function (s) { return [s.headline ? 1 : sub.decimals, growth]; }))
    };
  }

  function refreshBasketTable(spec) {
    var holder = document.querySelector('.chart-data[data-chart="' + spec.id + '"]');
    if (holder && holder.open) fillTable(spec, false);
  }

  // Rectangles whose areas are the values, as close to square as they can be (Bruls, Huizing and van Wijk's
  // squarified layout), in the order given (largest first), filling the box x, y, w, h.
  function squarify(values, x, y, w, h) {
    var total = values.reduce(function (a, v) { return a + v; }, 0), rects = [], i = 0;
    if (!(total > 0) || w <= 0 || h <= 0) return values.map(function () { return { x: x, y: y, w: 0, h: 0 }; });
    var scale = w * h / total;
    while (i < values.length) {
      var side = Math.min(w, h), row = [], sum = 0, hi = 0, lo = Infinity, best = Infinity;
      while (i < values.length) {
        var a = values[i] * scale, s = sum + a, mx = Math.max(hi, a), mn = Math.min(lo, a);
        var worst = Math.max(side * side * mx / (s * s), s * s / (side * side * mn));
        if (row.length && worst > best) break;
        row.push(a); sum = s; hi = mx; lo = mn; best = worst; i++;
      }
      var thick = sum / side, pos = 0;
      row.forEach(function (a) {
        var len = a / thick;
        rects.push(w >= h ? { x: x, y: y + pos, w: thick, h: len } : { x: x + pos, y: y, w: len, h: thick });
        pos += len;
      });
      if (w >= h) { x += thick; w -= thick; } else { y += thick; h -= thick; }
    }
    return rects;
  }

  function drawTreemap(el, spec) {
    var W = spec.words, st = basketState(el, spec), mode = st.mode, open = st.open;
    var categories = st.view === "map" ? basketMonth(spec, st.month) : null;
    var cat = categories && open && categories.filter(function (c) { return c.code === open; })[0];
    if (categories && !cat) open = "";
    var pct = { unit: "%", decimals: 2 }, rate = { unit: "%", decimals: 1 }, pts = { unit: "", decimals: 2 };
    function make(tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text !== undefined) n.textContent = text;
      return n;
    }
    function shareText(n) { return W.share.replace("{share}", fmt(n.weight, pct)); }
    function lines(n, parent) {        // the hover text: name, category, weight, rate, contribution
      var out = [n.full || n.name];
      if (parent) out.push(parent.name);
      out.push(shareText(n));
      out.push(n.rate === null || n.rate === undefined ? W.none : W.rate.replace("{rate}", fmt(n.rate, rate, true)));
      if (n.contribution !== null && n.contribution !== undefined && Math.abs(n.contribution) >= 0.005) {
        out.push((n.contribution > 0 ? W.adds : W.takes).replace("{pp}", fmt(Math.abs(n.contribution), pts)));
      }
      return out;
    }
    function label(n) { return mode === "weight" ? fmt(n.weight, pct) : (n.rate === null || n.rate === undefined ? "–" : fmt(n.rate, rate, true)); }
    function paint(node, n) { node.className += mode === "weight" ? " heat-" + (n.wshade || 1) : " gl-" + n.shade; }
    function buttons(name, attr, options, current) {     // a row of pressed / unpressed buttons
      var g = make("span", "tool-presets");
      g.setAttribute("role", "group");
      g.setAttribute("aria-label", name);
      options.forEach(function (o) {
        var b = make("button", "tool-button", o[1]);
        b.type = "button";
        b.setAttribute(attr, o[0]);
        b.setAttribute("data-chart", spec.id);
        b.setAttribute("aria-pressed", String(o[0] === current));
        g.appendChild(b);
      });
      return g;
    }
    function picker(name, pick, options, current) {      // a labelled drop-down (the month, the category)
      var l = make("label");
      l.appendChild(make("span", null, name));
      var s = make("select");
      s.setAttribute("data-tm-pick", pick);
      s.setAttribute("data-chart", spec.id);
      options.forEach(function (o) {
        var opt = make("option", null, o[1]);
        opt.value = o[0];
        if (String(o[0]) === String(current)) opt.selected = true;
        s.appendChild(opt);
      });
      l.appendChild(s);
      return l;
    }

    if (window.Plotly) Array.prototype.forEach.call(el.querySelectorAll(".js-plotly-plot"), function (p) { window.Plotly.purge(p); });
    el.style.height = "auto";
    el.textContent = "";
    el.removeAttribute("role");        // the card marks charts as images; this one is text and buttons
    el.removeAttribute("aria-label");
    var bar = make("div", "tm-bar tool-controls");
    bar.appendChild(buttons(W.view, "data-tm-view", [["map", W.map], ["time", W.time]], st.view));
    bar.appendChild(buttons(W.show, "data-tm-mode", [["growth", W.growth], ["weight", W.weight]], mode));
    if (categories) {
      var months = [];
      for (var k = spec.months.length - 1; k >= 0; k--) months.push([k, spec.labels[k]]);
      bar.appendChild(picker(W.month, "month", months, st.month));
    } else {
      var latest = basketYears(spec).pop(), size = {};
      spec.items.forEach(function (it, i) {
        var c = it[0].slice(0, 4);
        size[c] = (size[c] || 0) + (spec.shares[latest][i] || 0);
      });
      bar.appendChild(picker(W.category, "open", [["", W.all]].concat(spec.cats.slice().sort(function (a, b) {
        return (size[b[0]] || 0) - (size[a[0]] || 0);
      }).map(function (c) { return [c[0], c[1]]; })), open));
    }
    el.appendChild(bar);
    var subtitle = document.querySelector("#fig-" + spec.id + " .chart-subtitle");

    if (!categories) {                 // over time
      var c0 = open && spec.cats.filter(function (c) { return c[0] === open; })[0];
      var text = mode === "growth" ? (c0 ? W.subtitle_growth_open.replace("{name}", c0[1]) : W.subtitle_growth)
                                   : (c0 ? W.subtitle_weight_open.replace("{name}", c0[1]) : W.subtitle_weight);
      if (subtitle) subtitle.textContent = text;
      var holder = make("div", "tm-time");
      // On a phone the legend takes a line per part: the chart gets taller to keep its plot.
      holder.style.height = Math.round(Math.max(400, Math.min(480, el.clientWidth * 0.5)) + (el.clientWidth < 560 ? 140 : 0)) + "px";
      holder.setAttribute("role", "img");
      holder.setAttribute("aria-label", spec.title + ": " + text);
      el.appendChild(holder);
      el.appendChild(make("p", "note tm-detail", (mode === "growth" && !open && W.fit ? W.fit + " " : "") + W.hint_time));
      draw(basketTime(spec, st), holder);
      refreshBasketTable(spec);
      return;
    }

    if (subtitle) subtitle.textContent = W.subtitle_map.replace("{month}", spec.labels[st.month]);
    if (open) {
      var crumb = make("div", "tm-crumb");
      var back = make("button", "chart-link tm-back", W.back);
      back.type = "button";
      back.setAttribute("data-tm-open", "");
      back.setAttribute("data-chart", spec.id);
      crumb.appendChild(back);
      crumb.appendChild(make("span", "tm-crumb-name", cat.full));
      crumb.appendChild(make("span", "secondary", " · " + shareText(cat) + (cat.rate === null ? "" : " · " + W.rate.replace("{rate}", fmt(cat.rate, rate, true)))));
      el.appendChild(crumb);
    }

    var width = el.clientWidth, height = Math.round(Math.max(420, Math.min(560, width * 0.56)));
    var map = make("div", "tm-map");
    map.style.height = height + "px";
    var tip = make("div", "tm-tip");
    tip.hidden = true;
    var detail = make("p", "note tm-detail", open ? W.hint_open : W.hint);
    detail.setAttribute("aria-live", "polite");

    function place(node, r, gap) {        // whole pixels, so neighbours meet exactly; `gap` trims each side
      var l = Math.round(r.x), tp = Math.round(r.y);
      node.style.left = l + gap + "px";
      node.style.top = tp + gap + "px";
      node.style.width = Math.max(0, Math.round(r.x + r.w) - l - 2 * gap) + "px";
      node.style.height = Math.max(0, Math.round(r.y + r.h) - tp - 2 * gap) + "px";
    }
    function tile(n, r, parent, holder) {
      var node = make("div", "tm-tile");
      paint(node, n);
      place(node, r, 1);
      node._tm = { node: n, parent: parent };
      // A name where it has room (a long word in a narrow tile would be cut), else the figure alone.
      if (r.w >= 84 && r.h >= 36) {
        node.appendChild(make("span", "tm-name", n.name));
        node.appendChild(make("span", "tm-value", label(n)));
      } else if (r.w >= 52 && r.h >= 20) {
        node.appendChild(make("span", "tm-value", label(n)));
      }
      if (open) node.tabIndex = 0;
      node.setAttribute("aria-label", lines(n, parent).join(". "));
      holder.appendChild(node);
    }
    if (open) {
      var rects = squarify(cat.items.map(function (n) { return n.weight; }), 0, 0, width, height);
      cat.items.forEach(function (n, i) { tile(n, rects[i], cat, map); });
    } else {
      var blocks = squarify(categories.map(function (c) { return c.weight; }), 0, 0, width, height);
      categories.forEach(function (c, i) {
        var r = blocks[i], box = make("div", "tm-cat");
        place(box, r, 2);
        var bw = Math.max(0, Math.round(r.x + r.w) - Math.round(r.x) - 4), bh = Math.max(0, Math.round(r.y + r.h) - Math.round(r.y) - 4);
        var head = bw >= 56 && bh >= 44 ? 20 : 0;
        var open_ = make("button", "tm-head" + (head ? "" : " tm-head-hidden"));
        open_.type = "button";
        open_.setAttribute("data-tm-open", c.code);
        open_.setAttribute("data-chart", spec.id);
        open_.setAttribute("aria-label", W.open.replace("{name}", c.full) + ": " + lines(c).slice(1).join(", "));
        open_._tm = { node: c };
        if (head) {
          open_.appendChild(make("span", "tm-head-name", c.name));
          open_.appendChild(make("span", "tm-head-value", label(c)));
        }
        box.appendChild(open_);
        var inner = squarify(c.items.map(function (n) { return n.weight; }), 0, head, bw, bh - head);
        c.items.forEach(function (n, k) { tile(n, inner[k], c, box); });
        box._tm = { open: c.code };
        map.appendChild(box);
      });
    }

    function show(target, event) {
      var found = target && target.closest && target.closest(".tm-tile, .tm-head");
      if (!found || !found._tm) { tip.hidden = true; return; }
      tip.textContent = "";
      lines(found._tm.node, found._tm.parent).forEach(function (s, k) { tip.appendChild(make(k ? "span" : "strong", null, s)); });
      tip.hidden = false;
      var box = map.getBoundingClientRect(), at = found.getBoundingClientRect();
      var x = event && event.clientX !== undefined ? event.clientX - box.left : at.left - box.left + at.width / 2;
      var y = event && event.clientY !== undefined ? event.clientY - box.top : at.top - box.top + at.height / 2;
      var tw = tip.offsetWidth, th = tip.offsetHeight;
      tip.style.left = Math.max(0, Math.min(width - tw, x + 14 + tw > width ? x - tw - 14 : x + 14)) + "px";
      tip.style.top = Math.max(0, Math.min(height - th, y + 14 + th > height ? y - th - 14 : y + 14)) + "px";
      detail.textContent = lines(found._tm.node, found._tm.parent).join(" · ");
    }
    map.addEventListener("mousemove", function (e) { show(e.target, e); });
    map.addEventListener("mouseleave", function () { tip.hidden = true; });
    map.addEventListener("focusin", function (e) { show(e.target); });
    map.addEventListener("focusout", function () { tip.hidden = true; });
    map.addEventListener("click", function (e) {
      if (open) { show(e.target, e); return; }     // an item's figures
      var box = e.target.closest && e.target.closest(".tm-cat");   // the overview: open the category
      if (box && box._tm) { el.setAttribute("data-open", box._tm.open); drawTreemap(el, spec); scrollToMap(el); }
    });
    map.appendChild(tip);
    el.appendChild(map);
    el.appendChild(detail);

    var legend = make("div", "heat-legend tm-legend");
    legend.appendChild(make("span", null, mode === "weight" ? W.legend_weight_title : W.legend_growth_title));
    (mode === "weight" ? W.legend_weight : W.legend_growth).forEach(function (s) {
      var item = make("span", "heat-key");
      item.appendChild(make("span", "heat-swatch " + (mode === "weight" ? "heat-" + s[0] : "gl-" + s[0])));
      item.appendChild(document.createTextNode(s[1]));
      legend.appendChild(item);
    });
    el.appendChild(legend);
    refreshBasketTable(spec);
  }

  function scrollToMap(el) {
    var top = el.getBoundingClientRect().top;
    if (top < 0) el.scrollIntoView({ block: "start" });
  }

  // The switches (view, mode) and opening or closing a category; then the same control keeps the focus.
  document.addEventListener("click", function (event) {
    var b = event.target.closest && event.target.closest("[data-tm-view], [data-tm-mode], [data-tm-open]");
    if (!b) return;
    var el = document.getElementById("chart-" + b.getAttribute("data-chart")), spec = byId(b.getAttribute("data-chart"));
    if (!el || !spec) return;
    var attr = ["data-tm-view", "data-tm-mode", "data-tm-open"].filter(function (a) { return b.hasAttribute(a); })[0];
    var value = b.getAttribute(attr);
    el.setAttribute(attr.replace("tm-", ""), value);
    event.stopPropagation();
    drawTreemap(el, spec);
    if (attr === "data-tm-open") {
      scrollToMap(el);
      var first = el.querySelector(value ? ".tm-back" : ".tm-head");
      if (first) first.focus({ preventScroll: true });
    } else {
      var same = el.querySelector("[" + attr + '="' + value + '"]');
      if (same) same.focus({ preventScroll: true });
    }
  }, true);

  // The drop-downs: the map's month, the category over time.
  document.addEventListener("change", function (event) {
    var s = event.target.closest && event.target.closest("[data-tm-pick]");
    if (!s) return;
    var el = document.getElementById("chart-" + s.getAttribute("data-chart")), spec = byId(s.getAttribute("data-chart"));
    if (!el || !spec) return;
    var pick = s.getAttribute("data-tm-pick");
    el.setAttribute("data-" + pick, s.value);
    drawTreemap(el, spec);
    var again = el.querySelector('[data-tm-pick="' + pick + '"]');
    if (again) again.focus({ preventScroll: true });
  });

  document.addEventListener("click", function (event) {
    var b = event.target.closest && event.target.closest("[data-tile-period]");
    if (!b) return;
    var el = document.getElementById("chart-" + b.getAttribute("data-chart")), spec = byId(b.getAttribute("data-chart"));
    if (!el || !spec) return;
    el.setAttribute("data-period", b.getAttribute("data-tile-period"));
    drawTiles(el, spec);
  });

  // The rows of a bubble chart, every security: name, group, date, value, amount (for its table and CSV).
  function bubbleRows(spec) {
    var rows = [];
    spec.series.forEach(function (s) {
      s.x.forEach(function (x, i) { rows.push([s.text[i], s.name, x, s.y[i], s.size[i]]); });
    });
    return rows.sort(function (a, b) { return a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0; });
  }

  // A dot plot, one row per person (the ECB-speak standings): a heavy dot for the current
  // stance, small numbered dots for the latest readings (1 = most recent) and a band for the range.
  function drawDots(el, spec) {
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis");
    var blue = token("--series-1"), orange = token("--series-2");
    var rows = spec.rows;
    el.style.height = Math.max(220, rows.length * 30 + 70) + "px";
    var labels = rows.map(function (r) { return r.label; });
    var band = { x: [], y: [] }, recent = { x: [], y: [], text: [] };
    rows.forEach(function (r) {
      if (r.range) { band.x.push(r.range[0], r.range[1], null); band.y.push(r.label, r.label, null); }
      (r.recent || []).forEach(function (v, i) {
        if (v === null || v === undefined) return;
        recent.x.push(v); recent.y.push(r.label); recent.text.push(String(i + 1));
      });
    });
    var traces = [
      { type: "scatter", mode: "lines", x: band.x, y: band.y, hoverinfo: "skip", showlegend: false,
        line: { color: axis, width: 7 }, opacity: 0.6 },
      { type: "scatter", mode: "markers+text", x: recent.x, y: recent.y, text: recent.text, textposition: "top center",
        textfont: { size: 9, color: ink2 }, showlegend: false, marker: { size: 8, color: surface, line: { color: ink2, width: 1.5 } },
        hovertemplate: t("Reading") + " %{text}: <b>%{x:+." + spec.decimals + "f}</b><extra>%{y}</extra>" },
      { type: "scatter", mode: "markers", x: rows.map(function (r) { return r.stance; }), y: labels, showlegend: false,
        marker: { size: 13, color: rows.map(function (r) { return r.highlight ? orange : blue; }), line: { color: surface, width: 2 } },
        customdata: rows.map(function (r) { return r.sub || ""; }),
        hovertemplate: "<b>%{x:+." + spec.decimals + "f}</b> %{y}<br>%{customdata}<extra></extra>" }
    ];
    var lo = spec.x_range[0], hi = spec.x_range[1];
    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 10, r: 18, t: 8, b: 44 },
      hovermode: "closest", hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      yaxis: { type: "category", categoryorder: "array", categoryarray: labels, autorange: "reversed", automargin: true,
        fixedrange: true, ticks: "", tickfont: { color: ink2, size: 12 } },
      xaxis: { range: [lo, hi], gridcolor: grid, zeroline: true, zerolinecolor: ink2, zerolinewidth: 1, fixedrange: true,
        tickfont: { color: muted }, tickformat: "+d" },
      annotations: [
        { x: lo, xref: "x", y: 0, yref: "paper", yshift: -32, xanchor: "left", showarrow: false, text: "← " + (spec.left || "lower"), font: { size: 11, color: ink2 } },
        { x: hi, xref: "x", y: 0, yref: "paper", yshift: -32, xanchor: "right", showarrow: false, text: (spec.right || "higher") + " →", font: { size: 11, color: ink2 } }
      ]
    };
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    layout.height = parseInt(el.style.height, 10);   // the box's height: a chart drawn before keeps its old size otherwise
    window.Plotly.react(el, traces, layout, config);
  }

  // The same items in two years: a hollow dot for the earlier year, a filled one for the later, joined by a
  // thin bar, one row per item in the order given (a highlighted row's dot in text ink). The hover gives the
  // row's note (its change).
  function drawDumbbell(el, spec) {
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis"), blue = token("--series-1");
    var rows = spec.rows;
    el.style.height = Math.max(220, rows.length * 26 + 76) + "px";
    var labels = rows.map(function (r) { return r.label; });
    var link = { x: [], y: [] };
    rows.forEach(function (r) {
      if (r.a === null || r.a === undefined || r.b === null || r.b === undefined) return;
      link.x.push(r.a, r.b, null); link.y.push(r.label, r.label, null);
    });
    var format = ":." + spec.decimals + "f}" + suffix(spec);
    var traces = [
      { type: "scatter", mode: "lines", x: link.x, y: link.y, hoverinfo: "skip", showlegend: false,
        line: { color: axis, width: 3 } },
      { type: "scatter", mode: "markers", name: spec.a_name, x: rows.map(function (r) { return r.a; }), y: labels,
        marker: { size: 10, color: surface, line: { color: ink2, width: 2 } },
        hovertemplate: "<b>%{x" + format + "</b>  " + spec.a_name + "<extra>%{y}</extra>" },
      { type: "scatter", mode: "markers", name: spec.b_name, x: rows.map(function (r) { return r.b; }), y: labels,
        marker: { size: 11, color: rows.map(function (r) { return r.highlight ? ink : blue; }), line: { color: surface, width: 2 } },
        customdata: rows.map(function (r) { return r.note || ""; }),
        hovertemplate: "<b>%{x" + format + "</b>  " + spec.b_name + "<br>%{customdata}<extra>%{y}</extra>" }
    ];
    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 10, r: 18, t: 30, b: 30 }, showlegend: true,
      legend: { orientation: "h", x: 0, xanchor: "left", y: 1.0, yanchor: "bottom", font: { size: 12, color: ink2 } },
      hovermode: "closest", hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      yaxis: { type: "category", categoryorder: "array", categoryarray: labels, autorange: "reversed", automargin: true,
        fixedrange: true, ticks: "", tickfont: { color: ink2, size: 12 } },
      xaxis: { gridcolor: grid, zeroline: true, zerolinecolor: axis, fixedrange: true, tickfont: { color: muted },
        ticksuffix: suffix(spec), automargin: true }
    };
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    layout.height = parseInt(el.style.height, 10);   // the box's height: a chart drawn before keeps its old size otherwise
    window.Plotly.react(el, traces, layout, config);
  }

  // `into` draws the spec in another element (the basket's chart over time, inside its card).
  function draw(spec, into) {
    var el = into || document.getElementById("chart-" + spec.id);
    if (!el || !window.Plotly) return;
    if (spec.kind === "hbar") return drawRanking(el, spec);
    if (spec.kind === "dumbbell") return drawDumbbell(el, spec);
    if (spec.kind === "dots") return drawDots(el, spec);
    if (spec.kind === "xy") return drawXY(el, spec);
    if (spec.kind === "bubble") return drawBubble(el, spec);
    if (spec.kind === "tiles") return drawTiles(el, spec);
    if (spec.kind === "treemap") return drawTreemap(el, spec);
    if (spec.pick) spec = pickView(spec);
    // Fixed slot order, never cycled: a spec has at most six palette series (slots 4 to 6 come dashed, as some
    // of their colours sit close to the first three's). Slot 7 (violet) serves only a picked country's line.
    var colors = [1, 2, 3, 4, 5, 6, 7].map(function (n) { return token("--series-" + n); });
    var surface = token("--surface"), ink = token("--text"), ink2 = token("--text-2");
    var muted = token("--muted"), grid = token("--grid"), axis = token("--axis");
    var multi = spec.series.length > 1;
    // Curves (yields by maturity, rates by horizon) have a category axis instead of dates.
    var category = spec.x_kind === "category";
    // On narrow (phone-width) charts the legend names the lines; end labels would squeeze the plot.
    // With many lines (every comparator picked) the end labels would pile up: the legend names them instead.
    var endLabels = multi && el.clientWidth >= 480 && spec.series.length <= 6;
    var valueFormat = ":" + (spec.signed ? "+" : "") + "." + spec.decimals + "f}" + suffix(spec);

    // Dense bar charts (monthly bars over many years) drop the gaps and rounding, which would read as stripes.
    var dense = spec.series[0].x.length > 60;
    var traces = [];
    var annotations = [];
    var slot = 0;
    spec.series.forEach(function (s) {
      // A total drawn in text colour takes no palette slot; a series can share a slot (a fan chart's bounds).
      var color = s.color === "ink" ? ink : s.color === "muted" ? muted : s.slot ? colors[s.slot - 1] : colors[slot++];
      var kind = s.kind || spec.kind;
      // Value leads, name follows; the colored key comes from Plotly's swatch.
      var template = "<b>%{y" + valueFormat + "</b>  " + s.name + "<extra></extra>";
      if (kind === "bar") {
        traces.push({
          type: "bar", x: s.x, y: s.y, name: s.legend || s.name, hovertemplate: template,
          // Stacked segments are separated by a thin gap in the surface colour; dense stacks get a hairline in
          // their own colour instead, which closes the seams the background would show between narrow bars.
          marker: { color: color, line: { color: dense ? color : surface, width: spec.stack ? (dense ? 1 : 1.5) : 0 } }
        });
        return;
      }
      traces.push({
        type: "scatter", mode: category ? "lines+markers" : "lines", x: s.x, y: s.y, name: s.legend || s.name,
        line: { color: color, width: 2, shape: s.shape || "linear", dash: s.dash || "solid" }, hovertemplate: template,
        // A curve has few points: mark each one (with a surface ring), as on a line with sparse data.
        marker: { size: 7, color: color, line: { width: 1.5, color: surface } }
      });
      // End dot with a surface ring, and a direct label in text ink.
      var lastX = s.x[s.x.length - 1], lastY = s.y[s.y.length - 1];
      traces.push({
        type: "scatter", mode: "markers", x: [lastX], y: [lastY], showlegend: false, hoverinfo: "skip",
        marker: { size: 9, color: color, line: { width: 2, color: surface } }
      });
      if (endLabels) {
        // In the right margin (paper x = 1), so the label doesn't stretch the date axis.
        annotations.push({
          x: 1, xref: "paper", y: lastY, yref: "y", text: s.name + " " + fmt(lastY, spec, spec.signed),
          showarrow: false, xanchor: "left", xshift: 8, font: { size: 12, color: ink2 }
        });
      }
    });

    var shapes = (spec.ref_lines || []).map(function (r) {
      // Labelled in the right margin with the series end labels, clear of the lines.
      annotations.push({
        x: 1, xref: "paper", y: r.y, yref: "y", text: r.label, showarrow: false,
        xanchor: "left", xshift: 8, font: { size: 11, color: ink2 }
      });
      return { type: "line", xref: "paper", x0: 0, x1: 1, y0: r.y, y1: r.y, line: { color: axis, width: 1 } };
    });
    // Shaded periods (recessions), behind the data, in a light wash of the muted ink so they read in both themes.
    (spec.bands || []).forEach(function (b) {
      shapes.push({ type: "rect", xref: "x", yref: "paper", x0: b.x0, x1: b.x1, y0: 0, y1: 1, layer: "below",
        fillcolor: muted, opacity: 0.14, line: { width: 0 } });
    });
    // Shapes don't count towards the axis range: an invisible point keeps each reference line in view.
    (spec.ref_lines || []).forEach(function (r) {
      traces.push({ type: "scatter", mode: "markers", x: [spec.series[0].x[0]], y: [r.y], marker: { opacity: 0 },
        hoverinfo: "skip", showlegend: false });
    });

    var layout = {
      paper_bgcolor: surface, plot_bgcolor: surface,
      font: { family: token("--sans") || "system-ui, sans-serif", size: 12, color: ink2 },
      margin: { l: 44, r: labelMargin(annotations), t: multi ? 30 : 10, b: 30 },
      showlegend: multi,
      legend: { orientation: "h", x: 0, xanchor: "left", y: 1.02, yanchor: "bottom", font: { size: 12, color: ink2 } },
      hovermode: "x unified",
      hoverlabel: { bgcolor: surface, bordercolor: grid, font: { color: ink, size: 12 } },
      xaxis: category ? {
        type: "category", showgrid: false, showline: true, linecolor: axis, ticks: "", fixedrange: true,
        tickfont: { color: muted }, showspikes: true, spikemode: "across", spikethickness: 1,
        spikecolor: axis, spikedash: "solid"
      } : {
        type: "date", showgrid: false, showline: true, linecolor: axis, ticks: "", fixedrange: true,
        hoverformat: hoverDate(spec),
        tickfont: { color: muted }, showspikes: true, spikemode: "across", spikethickness: 1,
        spikecolor: axis, spikedash: "solid", spikesnap: "cursor"
      },
      yaxis: {
        // The zero line shows whenever zero is in range (growth rates, monthly changes).
        gridcolor: grid, gridwidth: 1, zeroline: true, zerolinecolor: axis, zerolinewidth: 1,
        fixedrange: true, tickfont: { color: muted }, ticksuffix: suffix(spec), automargin: true
      },
      barmode: spec.stack ? "relative" : "group",
      bargap: dense ? 0 : 0.3, barcornerradius: dense ? 0 : 4,
      annotations: annotations, shapes: shapes
    };
    // A chosen time window (5 or 10 years...) narrows the date axis and fits the vertical axis to it.
    var win = category ? null : rangeWindow(spec);
    if (win) {
      layout.xaxis.range = win.x;
      layout.yaxis.range = win.y;
    } else {
      layout.xaxis.autorange = true;
      layout.yaxis.autorange = true;
    }
    var config = Object.assign({ toImageButtonOptions: { filename: "macroscope-" + spec.id, scale: 2 } }, CONFIG_BASE);
    window.Plotly.react(el, traces, layout, config).then(function () { spreadLabels(el); });
  }

  // ---------------------------------------------------------------- time ranges
  // Long time series get buttons for the last few years. The choice is kept per chart for the visit and
  // survives redraws (theme, resize, a tool's new settings).
  var ranges = {};
  var DAY = 86400000;

  function isoDate(t) { return new Date(t).toISOString().slice(0, 10); }
  function parseIso(s) { return Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10) || 1); }
  function yearsBack(s, years) { return isoDate(Date.UTC(+s.slice(0, 4) - years, +s.slice(5, 7) - 1, +s.slice(8, 10) || 1)); }

  function dateSpan(spec) {
    var first = null, last = null;
    spec.series.forEach(function (s) {
      if (!s.x.length) return;
      if (first === null || s.x[0] < first) first = s.x[0];
      if (last === null || s.x[s.x.length - 1] > last) last = s.x[s.x.length - 1];
    });
    return first === null ? null : { first: first, last: last, years: (parseIso(last) - parseIso(first)) / (365.25 * DAY) };
  }

  // The windows worth offering: a window must be clearly shorter than the data. Annual charts are short,
  // and often end in projections, so they keep their whole span.
  function rangeOptions(spec) {
    if (spec.x_kind === "category" || ["hbar", "xy", "dots", "dumbbell", "bubble", "tiles", "treemap"].indexOf(spec.kind) >= 0 || spec.freq === "A" ||
        !spec.series || !spec.series.length) return [];
    var span = dateSpan(spec);
    if (!span) return [];
    return (spec.freq === "D" ? [1, 5] : [5, 10]).filter(function (y) { return span.years > y * 1.25; });
  }

  function rangeWindow(spec) {
    var years = ranges[spec.id];
    var span = years && dateSpan(spec);
    if (!span) return null;
    var cutoff = yearsBack(span.last, years);
    var lo = Infinity, hi = -Infinity, first = null, bars = false, up = {}, down = {};
    spec.series.forEach(function (s) {
      var bar = (s.kind || spec.kind) === "bar";
      s.x.forEach(function (x, i) {
        var v = s.y[i];
        if (x <= cutoff || v === null || v === undefined) return;
        if (first === null || x < first) first = x;
        if (bar) {
          bars = true;
          if (spec.stack) {   // stacked bars: the visible range is set by each date's positive and negative totals
            if (v >= 0) up[x] = (up[x] || 0) + v; else down[x] = (down[x] || 0) + v;
            return;
          }
        }
        lo = Math.min(lo, v); hi = Math.max(hi, v);
      });
    });
    Object.keys(up).forEach(function (k) { hi = Math.max(hi, up[k]); lo = Math.min(lo, 0); });
    Object.keys(down).forEach(function (k) { lo = Math.min(lo, down[k]); hi = Math.max(hi, 0); });
    if (bars) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
    if (!isFinite(lo) || first === null) return null;
    var pad = (hi - lo) * 0.06 || Math.abs(hi) * 0.1 || 1;
    // Room at the edges: half a period for bars, and enough for the end dots of lines.
    var start = parseIso(first), end = parseIso(span.last);
    var room = Math.max(bars ? ({ D: 1, M: 16, Q: 46, A: 183 }[spec.freq] || 16) * DAY : 0, (end - start) * 0.015);
    return {
      x: [isoDate(start - room), isoDate(end + room)],
      y: [bars && lo === 0 ? 0 : lo - pad, bars && hi === 0 ? 0 : hi + pad]
    };
  }

  function addRangeButtons(spec) {
    var fig = document.getElementById("fig-" + spec.id), options = rangeOptions(spec);
    if (!fig || !options.length || fig.querySelector(".range-buttons")) return;
    var caption = fig.querySelector("figcaption");
    if (!caption) return;
    var group = document.createElement("div");
    group.className = "range-buttons";
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", t("Time range"));
    options.concat([0]).forEach(function (years) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = years ? years + (LANG === "es" ? "A" : "Y") : t("All");
      b.setAttribute("data-years", years);
      b.setAttribute("aria-label", years ? (LANG === "es" ? "Últimos " + years + (years === 1 ? " año" : " años")
                                                         : "Last " + years + (years === 1 ? " year" : " years")) : t("All the data"));
      b.setAttribute("aria-pressed", String((ranges[spec.id] || 0) === years));
      group.appendChild(b);
    });
    caption.classList.add("has-range");
    caption.appendChild(group);
  }

  document.addEventListener("click", function (event) {
    var b = event.target.closest && event.target.closest(".range-buttons button");
    if (!b) return;
    var fig = b.closest(".chart-card"), spec = fig && byId(fig.id.slice("fig-".length));
    if (!spec) return;
    ranges[spec.id] = +b.getAttribute("data-years") || null;
    Array.prototype.forEach.call(b.parentNode.querySelectorAll("button"), function (other) {
      other.setAttribute("aria-pressed", String(other === b));
    });
    drawSpec(spec);
  });

  // Right margin wide enough for the longest end label (about 6.5px a character at 12px).
  function labelMargin(annotations) {
    var longest = 0;
    annotations.forEach(function (a) { longest = Math.max(longest, a.text.length); });
    return longest ? Math.min(180, Math.round(longest * 6.5) + 18) : 14;
  }

  // End labels of lines that finish close together would overlap: push them apart
  // vertically (at least 15px) once Plotly has laid out the axis.
  function spreadLabels(el) {
    try {
      var ya = el._fullLayout.yaxis, height = el._fullLayout._size.h;
      var notes = el.layout.annotations || [];
      if (notes.length < 2) return;
      var items = notes.map(function (a, i) { return { i: i, px: ya.l2p(a.y), orig: ya.l2p(a.y) }; });
      items.sort(function (a, b) { return a.px - b.px; });
      for (var k = 1; k < items.length; k++) {
        if (items[k].px - items[k - 1].px < 15) items[k].px = items[k - 1].px + 15;
      }
      var overflow = items[items.length - 1].px - height;
      var update = {};
      items.forEach(function (it) {
        var px = overflow > 0 ? it.px - overflow : it.px;
        update["annotations[" + it.i + "].yshift"] = it.orig - px;  // yshift is upwards
      });
      window.Plotly.relayout(el, update);
    } catch (e) { /* labels stay where they are */ }
  }

  // A plain table under each chart, so every value is readable without hovering. Time series show
  // their latest 12 dates, or every date once asked (`all`).
  function fillTable(spec, all) {
    var holder = document.querySelector('.chart-data[data-chart="' + spec.id + '"]');
    if (!holder) return;
    if (all === undefined && holder.querySelector("table")) return;
    if (spec.pick) spec = pickView(spec);
    Array.prototype.forEach.call(holder.querySelectorAll("table, .note"), function (el) { holder.removeChild(el); });
    var table = document.createElement("table");
    var category = spec.x_kind === "category";
    var head = table.createTHead().insertRow();
    if (spec.kind === "xy") return fillXYTable(spec, holder, table, head);
    if (spec.kind === "tiles") {
      [t("Index")].concat(spec.periods.map(function (p) { return p.label; })).forEach(function (h) {
        var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
      });
      var tt = table.createTBody();
      spec.rows.forEach(function (r) {
        var tr = tt.insertRow();
        tr.insertCell().textContent = r.label;
        spec.periods.forEach(function (p) {
          var v = r.values[p.key];
          tr.insertCell().textContent = v === null || v === undefined ? "–" : fmt(v, spec, true);
        });
      });
      holder.appendChild(table);
      return;
    }
    if (spec.kind === "treemap") {
      var bt = basketTable(spec);
      bt.head.forEach(function (h) {
        var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
      });
      var mb = table.createTBody();
      bt.rows.forEach(function (r) {
        var tr = mb.insertRow();
        r.forEach(function (v, j) {
          var f = bt.formats[j];
          tr.insertCell().textContent = !f ? v : v === null || v === undefined ? "–" : fmt(v, { unit: "", decimals: f[0] }, f[1]);
        });
      });
      holder.appendChild(table);
      if (bt.note) {
        var bn = document.createElement("p");
        bn.className = "note";
        bn.textContent = bt.note;
        holder.appendChild(bn);
      }
      return;
    }
    if (spec.kind === "bubble") {
      [t("Security"), t("Group"), spec.x_title, spec.y_label, spec.size_label].forEach(function (h) {
        var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
      });
      var bb = table.createTBody();
      bubbleRows(spec).forEach(function (r) {
        var tr = bb.insertRow();
        tr.insertCell().textContent = r[0];
        tr.insertCell().textContent = r[1];
        tr.insertCell().textContent = dateLabel(r[2], "D");
        tr.insertCell().textContent = fmt(r[3], spec);
        tr.insertCell().textContent = r[4].toLocaleString("en-GB", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) +
          (spec.size_unit ? " " + spec.size_unit : "");
      });
      holder.appendChild(table);
      return;
    }
    if (spec.kind === "dumbbell") {
      [spec.x_title || t("Item"), spec.a_name, spec.b_name, t("Change")].forEach(function (h) {
        var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
      });
      var rb = table.createTBody();
      spec.rows.forEach(function (r) {
        var tr = rb.insertRow();
        tr.insertCell().textContent = r.label;
        tr.insertCell().textContent = r.a === null || r.a === undefined ? "–" : fmt(r.a, spec);
        tr.insertCell().textContent = r.b === null || r.b === undefined ? "–" : fmt(r.b, spec);
        tr.insertCell().textContent = r.note || "–";
      });
      holder.appendChild(table);
      return;
    }
    if (spec.kind === "dots") {
      ["Member", "Stance", "Latest", "Range over the year"].map(t).forEach(function (h) {
        var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
      });
      var tb = table.createTBody();
      spec.rows.forEach(function (r) {
        var tr = tb.insertRow();
        tr.insertCell().textContent = r.label;
        tr.insertCell().textContent = fmt(r.stance, spec, true);
        tr.insertCell().textContent = (r.recent || []).filter(function (v) { return v !== null; }).map(function (v) { return fmt(v, spec, true); }).join(", ");
        tr.insertCell().textContent = r.range ? fmt(r.range[0], spec, true) + t(" to ") + fmt(r.range[1], spec, true) : "–";
      });
      holder.appendChild(table);
      return;
    }
    [spec.x_title || t("Date")].concat(spec.series.map(function (s) { return s.name; })).forEach(function (h) {
      var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
    });
    // Curves: every point in order. Time series: every date any series has (they can
    // differ in frequency), newest first.
    var seen = {}, dates = [];
    spec.series.forEach(function (s) {
      s.x.forEach(function (d) { if (!seen[d]) { seen[d] = true; dates.push(d); } });
    });
    var total = dates.length;
    if (!category) dates = dates.sort().reverse().slice(0, all ? total : 12);
    var maps = spec.series.map(function (s) {
      var m = {};
      s.x.forEach(function (x, i) { m[x] = s.y[i]; });
      return m;
    });
    var body = table.createTBody();
    dates.forEach(function (d) {
      var row = body.insertRow();
      row.insertCell().textContent = category ? d : dateLabel(d, spec.freq);
      maps.forEach(function (m) {
        row.insertCell().textContent = d in m && m[d] !== null ? fmt(m[d], spec, spec.signed) : "–";
      });
    });
    var caption = document.createElement("p");
    caption.className = "note";
    if (category || total <= 12) {
      caption.textContent = category ? t("All points.") : (LANG === "es" ? "Las " + total + " fechas." : "All " + total + " dates.");
    } else {
      caption.textContent = LANG === "es"
        ? (all ? "Las " + total + " fechas, de la más reciente a la más antigua. " : "Las últimas 12 de " + total + " fechas. ")
        : (all ? "All " + total + " dates, newest first. " : "Latest 12 of " + total + " dates. ");
      var more = document.createElement("button");
      more.type = "button";
      more.className = "chart-link table-all";
      more.textContent = LANG === "es" ? (all ? "Ver las últimas 12" : "Ver las " + total)
                                       : (all ? "Show the latest 12" : "Show all " + total);
      more.addEventListener("click", function () { fillTable(spec, !all); });
      caption.appendChild(more);
    }
    holder.appendChild(table);
    holder.appendChild(caption);
  }

  function fillXYTable(spec, holder, table, head) {
    [spec.x_title, spec.x_label, spec.y_label].forEach(function (h) {
      var th = document.createElement("th"); th.scope = "col"; th.textContent = h; head.appendChild(th);
    });
    var s = spec.series[0], body = table.createTBody();
    for (var i = s.x.length - 1; i >= Math.max(0, s.x.length - 12); i--) {
      var row = body.insertRow();
      row.insertCell().textContent = s.text[i];
      row.insertCell().textContent = s.x[i].toFixed(1) + (spec.x_unit === "%" ? "%" : "");
      row.insertCell().textContent = s.y[i].toFixed(0) + (spec.y_unit === "k" ? "k" : "");
    }
    var caption = document.createElement("p");
    caption.className = "note";
    caption.textContent = t("Latest 12 periods.");
    holder.appendChild(table);
    holder.appendChild(caption);
  }

  document.addEventListener("click", function (event) {
    var chip = event.target.closest && event.target.closest(".picker-chips .chip");
    if (!chip || !picker) return;
    var all = chip.getAttribute("data-pick");
    if (all === "all") picked = Object.keys(pickStyle);
    else if (all === "none") picked = [];
    else togglePick(chip.getAttribute("data-country"));
    savePicks();
    renderChips();
    drawAll();
    Array.prototype.forEach.call(document.querySelectorAll(".chart-data[open]"), function (holder) {
      var spec = byId(holder.getAttribute("data-chart"));
      if (spec && spec.pick) fillTable(spec, false);
    });
  });

  // ---------------------------------------------------------------- drawing as charts come into view
  // A page can carry 30 charts or more: each is drawn when it nears the screen, and a theme switch or
  // a resize redraws only those already drawn. Rankings and dot plots get their height first, so
  // drawing them later doesn't move the page.
  var drawn = {};

  function byId(id) {
    for (var i = 0; i < specs.length; i++) if (specs[i].id === id) return specs[i];
    return null;
  }

  function presize(spec) {
    var el = document.getElementById("chart-" + spec.id);
    if (!el) return;
    if (spec.kind === "hbar") el.style.height = Math.max(220, spec.series[0].x.length * 22 + 41 + Math.max(1, (spec.ref_lines || []).length) * 15) + "px";
    if (spec.kind === "dumbbell") el.style.height = Math.max(220, spec.rows.length * 26 + 76) + "px";
    if (spec.kind === "dots") el.style.height = Math.max(220, spec.rows.length * 30 + 70) + "px";
  }

  function drawSpec(spec) {
    drawn[spec.id] = true;
    draw(spec);
  }

  function drawAll() {
    specs.forEach(function (s) { if (drawn[s.id]) draw(s); });
  }

  function drawEverything() {
    specs.forEach(function (s) { if (!drawn[s.id]) drawSpec(s); });
  }

  var observer = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      var spec = byId(entry.target.id.slice("chart-".length));
      if (spec) drawSpec(spec);
    });
  }, { rootMargin: "400px 0px" }) : null;

  // ---------------------------------------------------------------- CSV download
  // Every value a chart carries (not just what the data table shows), one row per date or item.
  function csvCell(v) {
    var s = v === null || v === undefined ? "" : String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function csvRows(spec) {
    var unit = spec.unit ? " (" + spec.unit + ")" : "";
    if (spec.kind === "hbar") {
      var bars = spec.series[0];
      return [[spec.x_title || t("Item"), bars.name + unit]].concat(bars.x.map(function (x, i) { return [x, bars.y[i]]; }));
    }
    if (spec.kind === "xy") {
      var path = spec.series[0];
      return [[spec.x_title || t("Period"), spec.x_label, spec.y_label]].concat(
        path.x.map(function (x, i) { return [path.text[i], x, path.y[i]]; }));
    }
    if (spec.kind === "tiles") {
      return [[t("Index")].concat(spec.periods.map(function (p) { return p.label + unit; }))].concat(spec.rows.map(function (r) {
        return [r.label].concat(spec.periods.map(function (p) { return r.values[p.key] === null ? "" : r.values[p.key]; }));
      }));
    }
    if (spec.kind === "treemap") {
      var bc = basketTable(spec, true);
      return [bc.head].concat(bc.rows.map(function (r) {
        return r.map(function (v) { return v === null || v === undefined ? "" : v; });
      }));
    }
    if (spec.kind === "bubble") {
      return [[t("Security"), t("Group"), spec.x_title, spec.y_label + unit,
               spec.size_label + (spec.size_unit ? " (" + spec.size_unit + ")" : "")]].concat(bubbleRows(spec));
    }
    if (spec.kind === "dumbbell") {
      return [[spec.x_title || t("Item"), spec.a_name + unit, spec.b_name + unit]].concat(spec.rows.map(function (r) { return [r.label, r.a, r.b]; }));
    }
    if (spec.kind === "dots") {
      return [["Member", "Stance", "Lowest over the year", "Highest over the year"].map(t)].concat(spec.rows.map(function (r) {
        return [r.label, r.stance, r.range ? r.range[0] : "", r.range ? r.range[1] : ""];
      }));
    }
    var keys = [], seen = {}, maps = spec.series.map(function (s) {
      var m = {};
      s.x.forEach(function (x, i) { m[x] = s.y[i]; if (!seen[x]) { seen[x] = true; keys.push(x); } });
      return m;
    });
    if (spec.x_kind !== "category") keys.sort();
    return [[spec.x_title || t("Date")].concat(spec.series.map(function (s) { return s.name + unit; }))].concat(
      keys.map(function (k) { return [k].concat(maps.map(function (m) { return k in m ? m[k] : ""; })); }));
  }

  function downloadCsv(spec) {
    // A byte-order mark so spreadsheet programs read "€" and accents correctly.
    var text = "﻿" + csvRows(spec).map(function (r) { return r.map(csvCell).join(","); }).join("\r\n") + "\r\n";
    var url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
    var a = document.createElement("a");
    a.href = url; a.download = "macroscope-" + spec.id + ".csv";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  // ---------------------------------------------------------------- chart links
  // "Copy link" puts this page's address with the chart's anchor (#fig-<id>) on the clipboard.
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text; area.setAttribute("readonly", ""); area.style.position = "fixed"; area.style.opacity = "0";
      document.body.appendChild(area); area.select();
      try { document.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
      document.body.removeChild(area);
    });
  }
  document.addEventListener("click", function (event) {
    var xlsx = event.target.closest && event.target.closest('a[href$=".xlsx"]');
    if (xlsx) track("excel_download", { file_name: xlsx.getAttribute("href").split("/").pop() });
    var csv = event.target.closest && event.target.closest(".chart-csv");
    if (csv) {
      var spec = byId(csv.getAttribute("data-chart"));
      if (spec) { downloadCsv(spec); track("chart_csv_download", { chart: spec.id }); }
      return;
    }
    var button = event.target.closest && event.target.closest(".chart-link[data-figure]");
    if (!button) return;
    var url = location.href.split(/[?#]/)[0] + "#" + button.getAttribute("data-figure");
    var label = button.textContent;
    function show(text) {
      button.textContent = text;
      setTimeout(function () { button.textContent = label; }, 2000);
    }
    copyText(url).then(function () { show(t("Link copied")); }, function () { window.prompt(t("Copy this link:"), url); });
  });

  // A chart's data table is filled the first time it is opened.
  document.addEventListener("toggle", function (event) {
    var holder = event.target;
    if (!holder.classList || !holder.classList.contains("chart-data") || !holder.open) return;
    var spec = byId(holder.getAttribute("data-chart"));
    if (spec) fillTable(spec);
  }, true);

  // A chart with no data has nothing to download.
  function csvButton(id) { return document.querySelector('.chart-csv[data-chart="' + id + '"]'); }
  Array.prototype.forEach.call(document.querySelectorAll(".chart-csv"), function (b) {
    b.hidden = !byId(b.getAttribute("data-chart"));
  });

  specs.forEach(function (spec) {
    presize(spec);
    addRangeButtons(spec);
    var el = document.getElementById("chart-" + spec.id);
    if (!el) return;
    if (observer) observer.observe(el); else drawSpec(spec);
  });
  window.addEventListener("beforeprint", drawEverything);
  // Bring a linked chart (#fig-<id>) into view once the rankings above it have their height.
  if (location.hash.indexOf("#fig-") === 0) {
    var linked = document.getElementById(location.hash.slice(1));
    if (linked) linked.scrollIntoView();
  }

  // For pages that build charts in the browser (the tools): draw a spec now, and again
  // whenever the theme or the window size changes, like the charts written by the build.
  window.EP = window.EP || {};
  window.EP.render = function (spec) {
    var b = csvButton(spec.id);
    if (b) b.hidden = false;
    addRangeButtons(spec);
    for (var i = 0; i < specs.length; i++) {
      if (specs[i].id === spec.id) { specs[i] = spec; drawSpec(spec); return; }
    }
    specs.push(spec);
    drawSpec(spec);
  };
  window.EP.fmt = fmt;

  // ---------------------------------------------------------------- section links and back to top
  // A "#" after each section heading links to it (and copies the link).
  Array.prototype.forEach.call(document.querySelectorAll("main h2[id]"), function (h) {
    var a = document.createElement("a");
    a.className = "anchor";
    a.href = "#" + h.id;
    a.setAttribute("aria-label", t("Copy a link to the section") + " " + (h.firstChild ? h.firstChild.textContent : h.textContent).trim());
    a.textContent = "#";
    a.addEventListener("click", function (event) {
      event.preventDefault();
      history.replaceState(null, "", "#" + h.id);
      h.scrollIntoView();
      copyText(location.href).then(function () {
        a.classList.add("copied");
        setTimeout(function () { a.classList.remove("copied"); }, 1800);
      }, function () { /* the address bar has the link */ });
    });
    h.appendChild(a);
  });

  // ---------------------------------------------------------------- site search
  // The button (or "/" or Ctrl+K) opens a panel over the page. The index (data/search.js: every page,
  // section, chart and series) loads the first time; matching ignores case and accents, and every word
  // typed must appear in the title, the place or the Spanish name.
  (function () {
    var opener = document.getElementById("search-open"), panel = document.getElementById("search-panel");
    if (!opener || !panel) return;
    var input = document.getElementById("search-input"), list = document.getElementById("search-results");
    var hint = panel.querySelector(".search-hint");
    var KINDS = ["Page", "Section", "Chart", "Series"].map(t), BONUS = [5, 4, 2, 0];
    var index = null, loading = false, results = [], active = -1;

    function norm(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }

    function prepare() {
      index = (window.EP.search || []).map(function (e) {
        return { kind: e[0], title: e[1], context: e[2], href: e[3], t: norm(e[1]), all: norm(e[1] + " " + e[2] + " " + e[4]) };
      });
    }

    function load(then) {
      if (index) return then();
      if (window.EP && window.EP.search) { prepare(); return then(); }
      if (loading) return;
      loading = true;
      hint.textContent = t("Loading the index…");
      var script = document.createElement("script");
      script.src = opener.getAttribute("data-index");
      script.onload = function () { prepare(); then(); };
      script.onerror = function () { loading = false; hint.textContent = t("The search index could not be loaded."); };
      document.head.appendChild(script);
    }

    function wordStart(text, at) { return at === 0 || /[\s(,·/-]/.test(text.charAt(at - 1)); }

    function score(e, words, q) {
      var s = BONUS[e.kind] - e.title.length / 60;
      for (var i = 0; i < words.length; i++) {
        var at = e.all.indexOf(words[i]);
        if (at < 0) return -1;
        var inTitle = e.t.indexOf(words[i]);
        s += inTitle >= 0 ? (wordStart(e.t, inTitle) ? 6 : 3) : (wordStart(e.all, at) ? 2 : 1);
      }
      var whole = e.t.indexOf(q);
      return s + (whole === 0 ? 8 : whole > 0 ? 3 : 0);
    }

    function matches(words, q) {
      var found = [];
      index.forEach(function (e) { var s = score(e, words, q); if (s >= 0) found.push({ e: e, s: s }); });
      found.sort(function (a, b) { return b.s - a.s; });
      return found.slice(0, 20).map(function (f) { return f.e; });
    }

    function search() {
      var q = norm(input.value).trim();
      results = [];
      if (q) {
        var words = q.split(/\s+/);
        results = matches(words, q);
        // Nothing? Try the stems of the longer words ("electricidad" finds "eléctrica" and "electricity").
        if (!results.length && words.some(function (w) { return w.length >= 6; })) {
          results = matches(words.map(function (w) { return w.length >= 6 ? w.slice(0, Math.max(5, Math.ceil(w.length * 0.67))) : w; }), q);
        }
      }
      list.innerHTML = "";
      results.forEach(function (e, i) {
        var li = document.createElement("li"), a = document.createElement("a");
        li.id = "search-opt-" + i;
        li.setAttribute("role", "option");
        a.href = e.href;
        a.tabIndex = -1;
        var title = document.createElement("span"), where = document.createElement("span");
        title.className = "search-title"; title.textContent = e.title;
        where.className = "search-context"; where.textContent = KINDS[e.kind] + (e.kind ? " · " + e.context : "");
        a.appendChild(title); a.appendChild(where); li.appendChild(a); list.appendChild(li);
      });
      setActive(results.length ? 0 : -1);
      input.setAttribute("aria-expanded", String(results.length > 0));
      hint.textContent = LANG === "es"
        ? (!q ? "Todas las series, gráficos y secciones del sitio. Pruebe «paro», «precios de vivienda» o «exportaciones a China»."
              : results.length ? "" : "Nada coincide con «" + input.value.trim() + "».")
        : (!q ? "Every series, chart and section on the site. Try “paro”, “house prices” or “exports to China”."
              : results.length ? "" : "Nothing matches “" + input.value.trim() + "”.");
    }

    function setActive(i) {
      active = i;
      Array.prototype.forEach.call(list.children, function (li, k) { li.setAttribute("aria-selected", String(k === i)); });
      if (i >= 0) {
        input.setAttribute("aria-activedescendant", "search-opt-" + i);
        list.children[i].scrollIntoView({ block: "nearest" });
      } else {
        input.removeAttribute("aria-activedescendant");
      }
    }

    // Which kind of result people pick (page, section, chart or series), never what they typed.
    function chosen(a) {
      var i = Array.prototype.indexOf.call(list.children, a && a.parentNode);
      if (i >= 0 && results[i]) track("search_used", { result_kind: ["page", "section", "chart", "series"][results[i].kind] });
    }

    function show() {
      if (!panel.hidden) return input.focus();
      panel.hidden = false;
      document.body.classList.add("search-on");
      input.focus();
      input.select();
      load(search);
    }

    function hide(refocus) {
      if (!panel.hidden && input.value.trim() && !results.length) track("search_no_results", {});   // never the words
      panel.hidden = true;
      document.body.classList.remove("search-on");
      if (refocus) opener.focus();
    }

    opener.addEventListener("click", show);
    panel.addEventListener("click", function (e) {
      if (e.target === panel) hide(true);
      else if (e.target.closest("a")) { chosen(e.target.closest("a")); hide(false); }   // a result on this page only moves the page
    });
    input.addEventListener("input", function () { if (index) search(); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (results.length) setActive((active + (e.key === "ArrowDown" ? 1 : -1) + results.length) % results.length);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (active >= 0) { chosen(list.children[active].querySelector("a")); hide(false); location.href = results[active].href; }
      } else if (e.key === "Escape") {
        e.preventDefault();
        hide(true);
      } else if (e.key === "Tab") {
        e.preventDefault();                             // the input is the panel's only control
      }
    });
    document.addEventListener("keydown", function (e) {
      var el = document.activeElement, typing = el && (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName) || el.isContentEditable);
      if ((e.key === "/" && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) ||
          ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K"))) {
        e.preventDefault();
        show();
      }
    });
  })();

  // ---------------------------------------------------------------- where you are on a long page
  // Once the list of sections at the top scrolls away, a slim bar names the section you are reading;
  // it opens the list. The current section is also marked in the list at the top.
  (function () {
    var nav = document.querySelector("nav.on-page");
    if (!nav || document.querySelector(".sector-controls")) return;   // Sector tables keep their own sticky bar
    var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]')).filter(function (a) {
      return document.getElementById(a.getAttribute("href").slice(1));
    });
    if (links.length < 3) return;
    var heads = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var bar = document.createElement("div");
    bar.className = "section-bar";
    bar.hidden = true;
    bar.innerHTML = '<div class="wrap section-bar-inner"><button type="button" class="section-bar-toggle" aria-expanded="false">' +
      '<span class="section-bar-label">' + t("On this page") + '</span><strong></strong><svg viewBox="0 0 10 6" width="10" height="6" ' +
      'aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>' +
      '<nav class="section-bar-menu" aria-label="' + t("Sections of this page") + '" hidden></nav></div>';
    var toggle = bar.querySelector("button"), current = bar.querySelector("strong"), menu = bar.querySelector("nav");
    // On a page with the country chooser, the bar also carries it: "Countries (n)", which opens every chip,
    // wrapped, none cut off (a row of chips ran off the edge before Batch 34a).
    var countries = null, countriesToggle = null, barChips = null;
    if (picker) {
      countries = document.createElement("div");
      countries.className = "bar-countries";
      countries.innerHTML = '<button type="button" class="bar-countries-toggle" aria-expanded="false">' + t("Countries") +
        ' <span class="bar-countries-count"></span><svg viewBox="0 0 10 6" width="10" height="6" aria-hidden="true">' +
        '<path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>';
      barChips = picker.querySelector(".picker-chips").cloneNode(true);
      barChips.classList.add("bar-chips");
      barChips.hidden = true;
      countries.appendChild(barChips);
      bar.querySelector(".section-bar-inner").appendChild(countries);
      countriesToggle = countries.querySelector("button");
    }
    function setCountries(open) {
      if (!countries) return;
      barChips.hidden = !open;
      countriesToggle.setAttribute("aria-expanded", String(open));
    }
    if (countries) {
      countriesToggle.addEventListener("click", function () { setMenu(false); setCountries(barChips.hidden); });
      document.addEventListener("click", function (e) { if (!countries.contains(e.target)) setCountries(false); });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !barChips.hidden) { setCountries(false); countriesToggle.focus(); }
      });
    }
    var copies = links.map(function (a) {
      var m = document.createElement("a");
      m.href = a.getAttribute("href");
      m.textContent = a.textContent;
      if (a.classList.contains("has-new")) { m.className = "has-new"; m.title = a.title; }
      menu.appendChild(m);
      return m;
    });
    document.body.appendChild(bar);
    if (countries) renderChips();      // the copies' state and the count, now they are in the page

    function setMenu(open) {
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    }
    toggle.addEventListener("click", function () { setCountries(false); setMenu(menu.hidden); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("click", function (e) { if (!bar.contains(e.target)) setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !menu.hidden) { setMenu(false); toggle.focus(); }
    });

    var pending = false;
    function update() {
      pending = false;
      var past = nav.getBoundingClientRect().bottom < 0;
      bar.hidden = !past;
      if (!past) { setMenu(false); setCountries(false); }
      var at = -1;
      for (var i = 0; i < heads.length; i++) if (heads[i].getBoundingClientRect().top < 90) at = i;
      [links, copies].forEach(function (group) {
        group.forEach(function (a, i) {
          a.classList.toggle("is-current", i === at);
          if (i === at) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current");
        });
      });
      current.textContent = links[Math.max(at, 0)].textContent;
    }
    window.addEventListener("scroll", function () {
      if (!pending) { pending = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update);
    update();
  })();

  (function () {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "to-top";
    button.hidden = true;
    button.innerHTML = '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M6 10V2M2 6l4-4 4 4" ' +
      'fill="none" stroke="currentColor" stroke-width="1.6"/></svg>' + t("Top");
    button.setAttribute("aria-label", t("Back to the top of the page"));
    document.body.appendChild(button);
    var still = window.matchMedia("(prefers-reduced-motion: reduce)");
    button.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: still.matches ? "auto" : "smooth" });
      var skip = document.querySelector(".brand");
      if (skip) skip.focus({ preventScroll: true });
    });
    function check() { button.hidden = window.scrollY < window.innerHeight * 1.5; }
    window.addEventListener("scroll", check, { passive: true });
    check();
  })();

  // The home page's heat map opens on its newest months when it is too wide for the screen (phones).
  function newestMonths() {
    Array.prototype.forEach.call(document.querySelectorAll(".glance-scroll"), function (box) {
      box.scrollLeft = box.scrollWidth;
    });
  }
  newestMonths();
  window.addEventListener("load", newestMonths);      // again once fonts and styles have settled the widths

  // ---------------------------------------------------------------- since your last visit (home page)
  // Off until the reader turns it on: a choice, like the theme, so it needs no consent. Once on, local storage
  // keeps, under "ep-visits", when the page was last seen and when its data were built (data-build). Views less
  // than 30 minutes apart are one visit; the tiles and cards whose figures came in (data-changed) after the data
  // seen on the visit before are marked. Nothing leaves the browser.
  (function () {
    var bar = document.getElementById("since-visit");
    if (!bar) return;
    var KEY = "ep-visits", GAP = 30 * 60 * 1000;
    var text = bar.querySelector(".since-text"), button = bar.querySelector(".since-toggle");
    var offText = text.textContent, build = Date.parse(bar.getAttribute("data-build"));
    function attr(name) { return bar.getAttribute("data-" + name) || ""; }
    function load() {      // {saved: the stored visits, or null}, or null when storage is blocked
      try { return { saved: JSON.parse(localStorage.getItem(KEY) || "null") }; } catch (e) { return null; }
    }
    function save(v) {
      try { localStorage.setItem(KEY, JSON.stringify(v)); return true; } catch (e) { return false; }
    }
    function when(ms) {
      return new Date(ms).toLocaleString(LANG === "es" ? "es-ES" : "en-GB",
        { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
    }
    function count(n, kind) { return n === 1 ? attr(kind + "-one") : attr(kind + "-many").replace("{n}", n); }
    function unmark() {
      Array.prototype.forEach.call(document.querySelectorAll(".badge-unseen"), function (b) { b.parentNode.removeChild(b); });
      Array.prototype.forEach.call(document.querySelectorAll(".is-unseen"), function (el) { el.classList.remove("is-unseen"); });
    }
    function mark(since) {
      var tiles = 0, cards = 0;
      Array.prototype.forEach.call(document.querySelectorAll("[data-changed]"), function (el) {
        if (!(Date.parse(el.getAttribute("data-changed")) > since)) return;
        var badge = document.createElement("span");
        badge.className = "badge badge-unseen";
        badge.textContent = attr("badge");
        el.classList.add("is-unseen");
        if (el.classList.contains("tile")) {
          var slot = el.querySelector(".tile-badges");
          if (!slot) { slot = document.createElement("span"); slot.className = "tile-badges"; el.appendChild(slot); }
          slot.insertBefore(badge, slot.firstChild);
          tiles++;
        } else {
          var head = el.querySelector(".latest-when") || el;
          head.appendChild(document.createTextNode(" "));
          head.appendChild(badge);
          cards++;
        }
      });
      return [tiles, cards];
    }
    function show(v) {
      unmark();
      button.textContent = attr(v ? "turn-off" : "turn-on");
      if (!v) { text.textContent = offText; return; }
      if (!v.prev) { text.textContent = attr("first"); return; }
      var n = mark(v.prev.build), parts = [];
      if (n[0]) parts.push(count(n[0], "tile"));
      if (n[1]) parts.push(count(n[1], "card"));
      text.textContent = (parts.length ? attr("some").replace("{what}", parts.join(" " + attr("and") + " ")) : attr("none"))
        .replace("{when}", when(v.prev.at));
    }

    var stored = load();
    if (!stored) return;                                  // storage blocked: the line stays hidden
    var visits = stored.saved && stored.saved.last ? stored.saved : null, now = Date.now();
    if (visits) {
      if (now - visits.last.at > GAP) visits.prev = visits.last;   // a new visit: mark what came after the last one
      visits.last = { at: now, build: build };
      save(visits);
    }
    show(visits);
    bar.hidden = false;
    button.addEventListener("click", function () {
      var current = load();
      if (current && current.saved && current.saved.last) {
        try { localStorage.removeItem(KEY); } catch (e) { /* nothing was kept */ }
        show(null);
      } else {
        var first = { last: { at: Date.now(), build: build } };
        if (save(first)) show(first);
      }
    });
  })();

  // ---------------------------------------------------------------- the home page's opening (batch L1)
  // Each [data-reveal] block gets "is-in" the first time it comes into view, which draws the long line in (CSS);
  // the big numbers in it count up from zero; and the long line names both scores of the month under the pointer.
  (function () {
    var blocks = document.querySelectorAll("[data-reveal]");
    if (!blocks.length) return;
    var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function withCommas(s) {
      var parts = s.split(".");
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      return parts.join(".");
    }
    function countUp(el) {
      var target = parseFloat(el.getAttribute("data-count")), decimals = +el.getAttribute("data-decimals") || 0,
        suffix = el.getAttribute("data-suffix") || "", final = el.textContent, began = null, ms = 1400;
      if (isNaN(target) || still) return;
      function frame(now) {
        if (began === null) began = now;
        var t = Math.min(1, (now - began) / ms), v = target * (1 - Math.pow(1 - t, 3));
        el.textContent = t < 1 ? (v < 0 ? "\u2212" : "") + withCommas(Math.abs(v).toFixed(decimals)) + suffix : final;
        if (t < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
    function reveal(block) {
      if (block.classList.contains("is-in")) return;
      block.classList.add("is-in");
      Array.prototype.forEach.call(block.querySelectorAll("[data-count]"), countUp);
    }
    if ("IntersectionObserver" in window) {
      var seen = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { seen.unobserve(e.target); reveal(e.target); } });
      }, { threshold: 0.2 });
      Array.prototype.forEach.call(blocks, function (b) { seen.observe(b); });
    } else {
      Array.prototype.forEach.call(blocks, reveal);
    }

    // The long line's hover: a line down the chart at the nearest month, with both scores.
    Array.prototype.forEach.call(document.querySelectorAll(".hero-line[data-hover]"), function (fig) {
      var data;
      try { data = JSON.parse(fig.getAttribute("data-hover")); } catch (e) { return; }
      var area = fig.querySelector(".hl-area"), cross = fig.querySelector(".hl-cross"), tip = fig.querySelector(".hl-tip");
      var months = data.months, n = months.length;
      if (!area || !cross || !tip || n < 2) return;
      var colours = ["var(--series-1)", "var(--series-2)"];
      function signed(v) {
        if (v === null || v === undefined) return "\u2013";
        var r = Math.round(v * 10) / 10;
        return (r > 0 ? "+" : r < 0 ? "\u2212" : "") + Math.abs(r).toFixed(1);
      }
      function show(event) {
        var box = area.getBoundingClientRect();
        var k = Math.max(0, Math.min(n - 1, Math.round((event.clientX - box.left) / box.width * (n - 1))));
        var row = months[k], at = k / (n - 1);
        cross.style.left = (at * 100) + "%";
        tip.textContent = "";
        var head = document.createElement("b");
        head.textContent = row[0];
        tip.appendChild(head);
        [1, 2].forEach(function (j) {
          tip.appendChild(document.createElement("br"));
          var key = document.createElement("i");
          key.style.background = colours[j - 1];
          tip.appendChild(key);
          tip.appendChild(document.createTextNode(data.names[j - 1] + " " + signed(row[j])));
        });
        tip.classList.toggle("flip", at > 0.62);
        cross.hidden = false;
      }
      area.addEventListener("pointermove", show);
      area.addEventListener("pointerdown", show);
      area.addEventListener("pointerleave", function () { cross.hidden = true; });
    });
    // The clock's hover: the month nearest the pointer (within 28 px), ringed, with its phase and both readings.
    Array.prototype.forEach.call(document.querySelectorAll(".hero-clock[data-hover]"), function (fig) {
      var pts, words;
      try { pts = JSON.parse(fig.getAttribute("data-hover")); words = JSON.parse(fig.getAttribute("data-words")); } catch (e) { return; }
      var area = fig.querySelector(".hc-area"), ring = fig.querySelector(".hc-ring"), tip = fig.querySelector(".hc-tip");
      if (!area || !ring || !tip || !pts.length) return;
      function hide() { ring.hidden = true; tip.hidden = true; }
      function show(event) {
        var box = area.getBoundingClientRect(), best = null, nearest = 28 * 28;
        pts.forEach(function (p) {           // [month, x %, y %, phase, level, momentum], oldest first: ties go to the newer
          var dx = box.left + p[1] / 100 * box.width - event.clientX, dy = box.top + p[2] / 100 * box.height - event.clientY;
          if (dx * dx + dy * dy <= nearest) { nearest = dx * dx + dy * dy; best = p; }
        });
        if (!best) { hide(); return; }
        ring.style.left = tip.style.left = best[1] + "%";
        ring.style.top = tip.style.top = best[2] + "%";
        tip.textContent = "";
        var head = document.createElement("b");
        head.textContent = best[0] + " \u00b7 " + best[3];
        tip.appendChild(head);
        [[words.level, best[4]], [words.momentum, best[5]]].forEach(function (row) {
          tip.appendChild(document.createElement("br"));
          tip.appendChild(document.createTextNode(row[0] + " " + row[1]));
        });
        tip.classList.toggle("flip", best[1] > 55);
        ring.hidden = tip.hidden = false;
      }
      area.addEventListener("pointermove", show);
      area.addEventListener("pointerdown", show);
      area.addEventListener("pointerleave", hide);
    });
    // The map of Spain: the switch shows another measure (each tile carries all four: "text|shade|title"), and the
    // line under the map names the community under the pointer or keyboard focus.
    Array.prototype.forEach.call(document.querySelectorAll(".hero-map"), function (fig) {
      var tiles = fig.querySelectorAll(".rm-tile"), detail = fig.querySelector(".rm-detail"), hint = detail ? detail.textContent : "";
      var note = fig.querySelector(".rm-note"), spain = fig.querySelector(".rm-spain");
      function part(tile, key, i) { return (tile.getAttribute("data-" + key) || "").split("|")[i] || ""; }
      Array.prototype.forEach.call(fig.querySelectorAll("[data-rm]"), function (button) {
        button.addEventListener("click", function () {
          var key = button.getAttribute("data-rm");
          fig.setAttribute("data-measure", key);
          Array.prototype.forEach.call(fig.querySelectorAll("[data-rm]"), function (b) { b.setAttribute("aria-pressed", String(b === button)); });
          Array.prototype.forEach.call(tiles, function (tile) {
            tile.className = "rm-tile gl-" + part(tile, key, 1);
            tile.querySelector(".rm-v").textContent = part(tile, key, 0);
            tile.title = part(tile, key, 2);
            tile.setAttribute("aria-label", tile.title);
            void tile.offsetWidth;                      // restart the little pulse that marks the change
            tile.classList.add("swap");
          });
          if (note) note.textContent = button.getAttribute("data-note");
          if (spain) spain.textContent = button.getAttribute("data-legend");
          if (detail) detail.textContent = hint;
        });
      });
      Array.prototype.forEach.call(tiles, function (tile) {
        function say() { if (detail) detail.textContent = tile.title; }
        tile.addEventListener("pointerenter", say);
        tile.addEventListener("focus", say);
      });
      fig.querySelector(".rm-grid").addEventListener("pointerleave", function () { if (detail) detail.textContent = hint; });
    });
  })();

  // Redraw after a resize settles: whether end labels fit depends on the chart's width.
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(drawAll, 250);
  });
})();
