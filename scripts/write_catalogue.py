"""Write econpulse/locale/es.yaml, the Spanish for the site, from the translations below (Batch 33a on).

Keys are the English exactly as the code and templates write it; a key that no longer matches stays in English
on the Spanish site (a build lists what is left: see econpulse/i18n.py). Run from the project folder:

    python scripts/write_catalogue.py
"""

from pathlib import Path

import yaml

ES: dict[str, str] = {}


def add(pairs: dict[str, str]) -> None:
    for en, es in pairs.items():
        assert en not in ES or ES[en] == es, f"two Spanish texts for {en!r}"
        ES[en] = es


# ---------------------------------------------------------------- the frame: header, menus, footer, search
add({
    "A running read on the health of the Spanish economy.": "Una lectura continua del estado de la economía española.",
    "Skip to content": "Ir al contenido",
    "Spain": "España",
    "Data as of %(when)s": "Datos a %(when)s",
    "Search the site (press / or Ctrl+K)": "Buscar en el sitio (pulse / o Ctrl+K)",
    "Search": "Buscar",
    "About": "Acerca de",
    "Language": "Idioma",
    "Switch between light and dark theme": "Cambiar entre tema claro y oscuro",
    "Sections": "Secciones",
    "Sections of %(page)s": "Secciones de %(page)s",
    "Updated in the past week": "Actualizado en la última semana",
    "Release calendar": "Calendario de publicaciones",
    "Today": "Hoy",
    "Coming up": "Próximamente",
    "Calendar": "Calendario",
    "Data from %(sources)s.": "Datos de %(sources)s.",
    "Figures are as published by each source unless marked": "Las cifras son las que publica cada fuente salvo las marcadas como",
    "seasonally adjusted by Macroscope": "desestacionalizado por Macroscope",
    "SA": "desest.",
    "or labelled as a Macroscope calculation.": "o las señaladas como cálculo de Macroscope.",
    "built %(when)s": "generado el %(when)s",
    "About and methods": "Acerca del sitio y métodos",
    "Data and freshness": "Datos y actualidad",
    "RSS feed": "Canal RSS",
    "Privacy and cookies": "Privacidad y cookies",
    # the cookie banner and its footer button (templates/base.html, static/consent.js), shown when analytics is on
    "Cookies": "Cookies",
    "Cookies.": "Cookies.",
    "Macroscope Spain would like to use Google Analytics cookies, which are third-party cookies, to count visits and see which pages and tools are used. They are not used for advertising. Do you accept them?":
        "Macroscope España quiere usar cookies de Google Analytics, que son cookies de terceros, para contar las visitas "
        "y ver qué páginas y herramientas se usan. No se usan para publicidad. ¿Las acepta?",
    "Cookie policy": "Política de cookies",
    "Reject": "Rechazar",
    "Accept": "Aceptar",
    "You accepted these cookies.": "Ha aceptado estas cookies.",
    "You rejected these cookies.": "Ha rechazado estas cookies.",
    "Cookie settings": "Configuración de cookies",
    "Search the site": "Buscar en el sitio",
    "Search series, charts and sections, in English or Spanish": "Busque series, gráficos y secciones, en español o en inglés",
    "Results": "Resultados",
    "never": "nunca",
    "Madrid time": "hora de Madrid",
})

# Tabs and their dropdowns
add({
    "Home": "Inicio",
    "GDP": "PIB",
    "Labour market": "Mercado laboral",
    "Wages": "Salarios",
    "Inflation": "Inflación",
    "Financial": "Financiero",
    "ECB": "BCE",
    "Fiscal": "Fiscal",
    "Economic activity and external accounts": "Actividad económica y sector exterior",
    "Housing": "Vivienda",
    "Pensions": "Pensiones",
    "International": "Internacional",
    "Regions": "Regiones",
    "Analysis": "Análisis",
    "Sector tables": "Tablas sectoriales",
    "Tools": "Herramientas",
    "Data": "Datos",
    "Key indicators": "Indicadores clave",
    "Macroscope readings": "Lecturas de Macroscope",
    "What's new": "Novedades",
    "The economy in four questions": "La economía en cuatro preguntas",
    "Charts": "Gráficos",
    "Economy vs pre-COVID trend": "La economía frente a su tendencia previa a la COVID",
    "Taylor rule": "Regla de Taylor",
    "Interest rate decomposer": "Descomposición de los tipos de interés",
    "Fiscal Explorer": "Explorador fiscal",
    "Budget explorer": "Explorador presupuestario",
    "Budget explorer: the autonomous communities": "Explorador presupuestario: las comunidades autónomas",
    "ECB-speak": "ECB-speak",
    "Global central bank stance": "Orientación de los bancos centrales",
    "Central bank stance": "Orientación de los bancos centrales",
    "Release map": "Mapa de publicaciones",
    "Released in the past week": "Publicado en la última semana",
    "The next two months": "Los próximos dos meses",
    "Real sector": "Sector real",
    "Government operations": "Operaciones de las Administraciones públicas",
    "Debt sustainability": "Sostenibilidad de la deuda",
    "Financial soundness": "Solidez financiera",
    "Balance of payments": "Balanza de pagos",
    "External debt": "Deuda externa",
    "Monetary and credit": "Indicadores monetarios y crediticios",
    "Every industry": "Todas las actividades",
    "Trade in goods and services": "Comercio de bienes y servicios",
    "Trade": "Comercio",
})

# The sections of each page, as listed in the dropdowns (the pages themselves follow in Batches 33b and 33c)
add({
    "Affordability": "Accesibilidad",
    "Against other countries": "Frente a otros países",
    "An ageing population": "Una población que envejece",
    "Bond yields and the prima de riesgo": "Rentabilidad de los bonos y prima de riesgo",
    "Building and households": "Construcción y hogares",
    "Business and consumer surveys": "Encuestas a empresas y consumidores",
    "By region": "Por comunidad autónoma",
    "By scheme": "Por régimen",
    "Collective dismissals and temporary layoffs": "Despidos colectivos y ERTE",
    "Commercial property": "Inmuebles comerciales",
    "Consumer prices (IPC)": "Precios de consumo (IPC)",
    "Contracts and the labour reform": "Contratos y reforma laboral",
    "Data surprises": "Sorpresas en los datos",
    "Deficit and debt": "Déficit y deuda",
    "Energy and expectations": "Energía y expectativas",
    "Euribor and mortgages": "Euríbor e hipotecas",
    "External accounts": "Sector exterior",
    "Financial stress and banks": "Tensión financiera y bancos",
    "GDP and its components": "El PIB y sus componentes",
    "GDP nowcast (placeholder)": "Estimación adelantada del PIB (provisional)",
    "Growth": "Crecimiento",
    "Harmonised prices (IPCA) and the euro area": "Precios armonizados (IPCA) y la zona del euro",
    "Hours worked": "Horas trabajadas",
    "House prices": "Precios de la vivienda",
    "Household finances and wealth": "Finanzas y riqueza de los hogares",
    "IMF-style external accounts": "Sector exterior al estilo del FMI",
    "IMF-style financial soundness indicators": "Indicadores de solidez financiera al estilo del FMI",
    "IMF-style government operations": "Operaciones de las AA. PP. al estilo del FMI",
    "IMF-style main indicators": "Principales indicadores al estilo del FMI",
    "IMF-style monetary and credit indicators": "Indicadores monetarios y crediticios al estilo del FMI",
    "Industry, shops and electricity": "Industria, comercio y electricidad",
    "Jobs": "Empleo",
    "Jobs by sector": "Empleo por sectores",
    "Labour force survey (EPA)": "Encuesta de Población Activa (EPA)",
    "Markets": "Mercados",
    "Maximum and minimum pensions": "Pensiones máximas y mínimas",
    "Mortgages and credit": "Hipotecas y crédito",
    "New and ended pensions": "Altas y bajas de pensiones",
    "Participation and an ageing population": "Actividad y envejecimiento de la población",
    "Pay and productivity": "Salarios y productividad",
    "Pay by activity": "Salarios por actividad",
    "Pay growth": "Crecimiento salarial",
    "Pay growth by activity": "Crecimiento salarial por actividad",
    "Pensions today": "Las pensiones hoy",
    "Policy rates": "Tipos oficiales",
    "Prices and interest rates": "Precios y tipos de interés",
    "Productivity and labour costs": "Productividad y costes laborales",
    "Public finances": "Finanzas públicas",
    "Rents and renting": "Alquileres",
    "Sales": "Compraventas",
    "Slack and vacancies": "Holgura y vacantes",
    "Social Security registrations": "Afiliación a la Seguridad Social",
    "Spain and its comparators": "España y sus comparables",
    "Taylor rules: the euro area and Spain": "Reglas de Taylor: la zona del euro y España",
    "The 2023 reform": "La reforma de 2023",
    "The IMF's outlook": "Las perspectivas del FMI",
    "The autonomous communities": "Las comunidades autónomas",
    "The current account": "La balanza por cuenta corriente",
    "The economy against its history": "La economía frente a su historia",
    "Tourism": "Turismo",
    "Underlying inflation": "Inflación subyacente",
    "Unemployment by sector": "Paro por sectores",
    "Vacancies by activity": "Vacantes por actividad",
    "What forecasters expect": "Qué esperan los analistas",
    "What markets expect": "Qué esperan los mercados",
    "What moves the 10-year yield": "Qué mueve el bono a 10 años",
    "What the official assessments say": "Qué dicen las evaluaciones oficiales",
    "Who works: age, sex, citizenship and education": "Quién trabaja: edad, sexo, nacionalidad y estudios",
    "Worker flows: finding and losing jobs": "Flujos laborales: encontrar y perder empleo",
    # The Trade page's sections
    "Exports, imports and the balance": "Exportaciones, importaciones y saldo",
    "Trade by product group": "Comercio por grupos de productos",
    "Rankings by product": "Clasificaciones por producto",
    "Trade by partner": "Comercio por socio",
    "Trade in services": "Comercio de servicios",
    "Export and import prices": "Precios de exportación e importación",
    "Food and drink": "Alimentos y bebidas",
    "Energy and materials": "Energía y materias primas",
    "Chemicals and plastics": "Química y plásticos",
    "Manufactures": "Manufacturas",
    "About the data": "Sobre los datos",
})

# ---------------------------------------------------------------- page titles and descriptions
add({
    "Page not found": "Página no encontrada",
    "The page you asked for is not on Macroscope Spain.": "La página que busca no está en Macroscope España.",
    "That page doesn't exist, or it has moved. Every page on the site is below.":
        "Esa página no existe o se ha movido. Debajo están todas las páginas del sitio.",
    "Data and sources": "Datos y fuentes",
    "Every series on Macroscope Spain, where it comes from, its latest value and whether it is up to date.":
        "Todas las series de Macroscope España: de dónde proceden, su último valor y si están al día.",
    "When the figures on Macroscope Spain are published: the release calendar of INE, the Banco de España, Eurostat and the other sources, in Madrid time.":
        "Cuándo se publican las cifras de Macroscope España: el calendario de publicaciones del INE, el Banco de España, Eurostat y las demás fuentes, en hora de Madrid.",
})

# ---------------------------------------------------------------- shared pieces of the pages (templates/macros.html)
add({
    "flash estimate": "avance",
    "stale: last update failed": "desfasada: falló la última actualización",
    "no data": "sin datos",
    "not updating": "sin actualizar",
    "Indicator": "Indicador",
    "Latest": "Último",
    "Change": "Variación",
    "Period": "Periodo",
    "Source": "Fuente",
    "Status": "Estado",
    "ok": "correcto",
    "New figures: %(what)s": "Nuevas cifras: %(what)s",
    "Updated %(day)s": "Actualizado el %(day)s",
    "Source: %(source)s": "Fuente: %(source)s",
    "Download the data of the chart %(title)s as a CSV file": "Descargar los datos del gráfico %(title)s en un archivo CSV",
    "Copy a link to the chart %(title)s": "Copiar un enlace al gráfico %(title)s",
    "Copy link": "Copiar enlace",
    "More": "Más",
    "Show data": "Ver los datos",
    "Source:": "Fuente:",
    "and %(n)s more, under Show data": "y %(n)s más, en «Ver los datos»",
    "On this page": "En esta página",
})

# ---------------------------------------------------------------- the home page
add({
    "Each tile links to its source. Hover for the official Spanish name.":
        "Cada recuadro enlaza con su fuente. Pase el cursor por encima para ver el nombre en inglés.",
    "Each tile links to its source, and its line shows the past few years. Hover for the official Spanish name.":
        "Cada recuadro enlaza con su fuente, y su línea muestra los últimos años. Pase el cursor por encima para ver "
        "el nombre en inglés.",
    # The latest releases and the sparklines (econpulse/homepage.py)
    "Latest releases": "Últimas publicaciones",
    "Releases of the past two weeks, newest first. Each line shows the past few years: hover over it for the range.":
        "Publicaciones de las dos últimas semanas, de la más reciente a la más antigua. Cada línea muestra los últimos "
        "años: pase el cursor por encima para ver el rango.",
    "The highest since {period}": "El dato más alto desde {period}",
    "The lowest since {period}": "El dato más bajo desde {period}",
    "The highest in the series, which starts in {year}": "El dato más alto de la serie, que empieza en {year}",
    "The lowest in the series, which starts in {year}": "El dato más bajo de la serie, que empieza en {year}",
    "After {value} in {period}": "Tras {value} en {period}",
    "Past year": "Último año",
    "Past {n} years": "Últimos {n} años",
    "{span}: low {low} ({low_when}), high {high} ({high_when})":
        "{span}: mínimo {low} ({low_when}), máximo {high} ({high_when})",
    "New · {day}": "Nuevo · {day}",
    # The economy at a glance (econpulse/glance.py)
    "The economy at a glance": "La economía de un vistazo",
    "The past twelve months against normal": "Los últimos doce meses frente a lo normal",
    "Activity and inflation readings by month, to %(month)s, shaded by how far each is from its normal since 2013":
        "Datos de actividad e inflación por meses, hasta %(month)s, sombreados según lo lejos que está cada uno de lo "
        "normal desde 2013",
    "Reading": "Dato",
    "Activity, overall score": "Actividad, puntuación global",
    "Inflation, overall score": "Inflación, puntuación global",
    "{label}, {period}: not out yet": "{label}, {period}: aún no publicado",
    "{label}, {period}: {value}; score {score}, {describe}": "{label}, {period}: {value}; puntuación {score}, {describe}",
    "{label}, {period}: {score}, {describe}": "{label}, {period}: {score}, {describe}",
    "Score against normal:": "Puntuación frente a lo normal:",
    "or less": "o menos",
    "to": "a",
    "or more": "o más",
    "within ±0.5": "entre −0.5 y +0.5",
    "not out yet": "aún no publicado",
    "Each month's reading is shaded by how far it is from its own normal since 2013, Covid years left out: warm colours above normal, cool colours below. For activity, above normal means stronger, and a fall in unemployment counts as stronger; for inflation, it means hotter. Quarterly figures span their quarter. Hover over a cell for the reading and its score.":
        "Cada dato mensual está sombreado según lo lejos que está de lo normal para él desde 2013, sin los años de la "
        "covid: colores cálidos por encima de lo normal y fríos por debajo. En la actividad, por encima de lo normal "
        "significa más fuerte, y una bajada del paro cuenta como más fuerte; en la inflación, significa más alta. Los "
        "datos trimestrales ocupan su trimestre. Pase el cursor por una celda para ver el dato y su puntuación.",
    "How the scores are made": "Cómo se calculan las puntuaciones",
    "At their highest or lowest in years": "En máximos o mínimos de años",
    "Key figures whose latest reading, as shown, is the highest or lowest in at least two years.":
        "Cifras clave cuyo último dato, tal como se muestra, es el más alto o el más bajo en al menos dos años.",
    "{n} million": "{n} millones",
    # Spain and its peers, and what forecasters expect (econpulse/scoreboard.py)
    "Spain and its peers": "España y sus comparables",
    "Latest figures": "Últimos datos",
    "Where Spain stands": "Dónde está España",
    "Spain's place": "Puesto de España",
    "the fastest of {n}": "el más rápido de los {n}",
    "{rank} fastest of {n}": "el {rank}.º más rápido de los {n}",
    "the highest of {n}": "la cifra más alta de los {n}",
    "{rank} highest of {n}": "la {rank}.ª cifra más alta de los {n}",
    "the largest rise of {n}": "la mayor subida de los {n}",
    "{rank} largest rise of {n}": "la {rank}.ª mayor subida de los {n}",
    "%, monthly avg.": "%, media mensual",
    "Spain's place is among the five countries, from the top; in each strip Spain is the blue dot, the other countries grey and the euro area the dark tick (hover over them for the figures). A period under a figure means that country has not published the latest one yet. Government debt is the IMF's, %(edition)s.":
        "El puesto de España es entre los cinco países, de mayor a menor; en cada franja España es el punto azul, los "
        "demás países los grises y la zona del euro la marca oscura (pase el cursor por encima para ver las cifras). "
        "Un periodo bajo una cifra indica que ese país aún no ha publicado el último dato. La deuda pública es la del "
        "FMI, %(edition)s.",
    "More on the International page": "Más en la página Internacional",
    "{measure}, {year}": "{measure}, {year}",
    "Macroscope: {value}, from INE to {quarter} and the nowcast":
        "Macroscope: {value}, con el INE hasta el {quarter} y la estimación adelantada",
    "Macroscope's estimate: {value}": "Estimación de Macroscope: {value}",
    "Average: {value}": "Media: {value}",
    "The average of %(who)s, with AI-checked figures only. Each grey dot is a forecaster, the dark tick their average and the blue dot Macroscope's own estimate (hover over them for the figures). Inflation is the HICP for some forecasters and the CPI for others.":
        "La media de %(who)s, solo con cifras comprobadas por IA. Cada punto gris es un analista, la marca oscura su "
        "media y el punto azul la estimación propia de Macroscope (pase el cursor por encima para ver las cifras). La "
        "inflación es el IPCA para unos analistas y el IPC para otros.",
    "Every forecast on the Analysis page": "Todas las previsiones, en la página de Análisis",
    # Chart of the week (batch H4)
    "Chart of the week": "Gráfico de la semana",
    "Picked from the past seven days' releases: the figure at its highest or lowest in the longest time, or else the newest. The line across the chart marks the latest reading. This one is from %(release)s, out on %(day)s.":
        "Elegido entre las publicaciones de los últimos siete días: el dato que está en su máximo o su mínimo desde "
        "hace más tiempo o, si no hay ninguno, el más reciente. La línea que cruza el gráfico marca el último dato. "
        "Este es de %(release)s, publicado el %(day)s.",
    "{period}: {value}. {context}.": "{period}: {value}. {context}.",
    "% change on the previous month": "Variación mensual, %",
    "% change on the previous quarter": "Variación intertrimestral, %",
    "% change on the previous year": "Variación anual, %",
    "% change on the previous day": "Variación diaria, %",
    "Change on the previous month, {unit}": "Variación mensual, {unit}",
    "Change on the previous quarter, {unit}": "Variación intertrimestral, {unit}",
    "Change on the previous year, {unit}": "Variación anual, {unit}",
    "Change on the previous day, {unit}": "Variación diaria, {unit}",
    "Change on a year earlier, {unit}": "Variación interanual, {unit}",
    "% change over three months, annualised": "Variación en tres meses, anualizada, %",
    "% change on the previous quarter, annualised": "Variación intertrimestral anualizada, %",
    "Total over the past year, {unit}": "Total del último año, {unit}",
    "Average over the past year, {unit}": "Media del último año, {unit}",
    "{what}, seasonally adjusted by Macroscope": "{what}; datos desestacionalizados por Macroscope",
    # Since your last visit (batch H4)
    "Coming back? This page can mark what is new since each of your visits. Only this browser keeps the date.":
        "¿Va a volver? Esta página puede marcar lo nuevo desde cada una de sus visitas. Solo este navegador guarda la fecha.",
    "On. From your next visit, this page will mark the figures that are new since this one.":
        "Activado. Desde su próxima visita, esta página marcará los datos nuevos desde esta.",
    "Since your last visit ({when}): new or revised figures in {what}, marked below.":
        "Desde su última visita ({when}): datos nuevos o revisados en {what}, marcados abajo.",
    "Nothing new since your last visit ({when}).": "Nada nuevo desde su última visita ({when}).",
    "1 key indicator": "1 indicador clave",
    "{n} key indicators": "{n} indicadores clave",
    "1 of the latest releases": "1 de las últimas publicaciones",
    "{n} of the latest releases": "{n} de las últimas publicaciones",
    "and": "y",
    "Since your last visit": "Desde su última visita",
    "Turn it on": "Activar",
    "Turn off": "Desactivar",
    # The basket, item by item (Inflation page, batch I1)
    "The basket, item by item": "La cesta, artículo a artículo",
    "What households spend their money on, and how fast each price is rising: the items of the harmonised basket, each sized by its weight (its share of household spending that year) and grouped into the 13 categories of the European classification (ECOICOP). Price growth colours each item by its change on a year earlier, warm above the ECB's 2% target and cool below; Weight shades it by its share of the basket instead. Click a category to open it, or pick any month since 2016. Over time shows how much each category has added to annual inflation month by month (worked out as Eurostat does, so they add up to the headline rate), or how the basket's make-up has changed year by year.":
        "En qué gastan los hogares y a qué ritmo sube cada precio: los artículos de la cesta armonizada, cada uno "
        "con un tamaño según su ponderación (su peso en el gasto de los hogares ese año) y agrupados en las 13 "
        "categorías de la clasificación europea (ECOICOP). Variación de los precios colorea cada artículo según su "
        "variación interanual, en tonos cálidos por encima del objetivo del 2% del BCE y fríos por debajo; Peso lo "
        "sombrea según su peso en la cesta. Pulse una categoría para abrirla o elija cualquier mes desde 2016. "
        "Evolución muestra cuánto ha sumado cada categoría a la inflación interanual mes a mes (calculado como lo "
        "hace Eurostat, de modo que suman la tasa general) o cómo ha cambiado la composición de la cesta año a año.",
    # The basket over time (batch I2)
    "View": "Vista",
    "Map": "Mapa",
    "Over time": "Evolución",
    "Month": "Mes",
    "Year": "Año",
    "All categories": "Todas las categorías",
    "Hover over or tap the chart for each period's figures. Pick a category to see its items.":
        "Pase el cursor por el gráfico o tóquelo para ver las cifras de cada periodo. Elija una categoría para ver sus artículos.",
    "The categories add up to the published rate to within {pp} points every month.":
        "Cada mes, las categorías suman la tasa publicada con una diferencia máxima de {pp} puntos.",
    "Contributions to annual HICP inflation by category, percentage points, and the headline rate, %":
        "Contribuciones a la inflación interanual del IPCA por categoría, puntos porcentuales, y tasa general, %",
    "{name}: its items' contributions to annual HICP inflation, percentage points":
        "{name}: contribuciones de sus artículos a la inflación interanual del IPCA, puntos porcentuales",
    "Each category's share of the basket, %, year by year": "Peso de cada categoría en la cesta, %, año a año",
    "{name}: each item's share of the category's spending, %, year by year":
        "{name}: peso de cada artículo en el gasto de la categoría, %, año a año",
    "Headline inflation": "Inflación general",
    "{name}, total": "{name}, total",
    "Other items": "Otros artículos",
    "HICP, {month}: each tile is an item, sized by its share of household spending":
        "IPCA, {month}: cada casilla es un artículo, con un tamaño según su peso en el gasto de los hogares",
    "Eurostat (HICP); Macroscope calculation": "Eurostat (IPCA); cálculo de Macroscope",
    "Food and soft drinks": "Alimentos y bebidas",
    "Alcohol and tobacco": "Bebidas alcohólicas y tabaco",
    "Clothing and footwear": "Vestido y calzado",
    "Housing and energy": "Vivienda y energía",
    "Household goods": "Menaje",
    "Health care": "Sanidad",
    "Recreation and culture": "Ocio y cultura",
    "Restaurants and hotels": "Restaurantes y hoteles",
    "Insurance and finance": "Seguros y servicios financieros",
    "Personal care and other": "Cuidado personal y otros",
    "Price growth": "Variación de los precios",
    "Show": "Mostrar",
    "← All categories": "← Todas las categorías",
    "Open {name}": "Abrir {name}",
    "{share} of the basket": "{share} de la cesta",
    "{rate} on a year earlier": "{rate} interanual",
    "adds about {pp} points to inflation": "suma unos {pp} puntos a la inflación",
    "takes about {pp} points off inflation": "resta unos {pp} puntos a la inflación",
    "No annual rate yet: new in the classification": "Aún sin tasa anual: nuevo en la clasificación",
    "Hover over or tap a tile for its figures. Click a category to open it.":
        "Pase el cursor por una casilla o tóquela para ver sus cifras. Pulse una categoría para abrirla.",
    "Hover over or tap a tile for its figures.": "Pase el cursor por una casilla o tóquela para ver sus cifras.",
    "Category": "Categoría",
    "Weight, % of the basket": "Peso, % de la cesta",
    "Annual rate, %": "Tasa anual, %",
    "Contribution, points": "Contribución, puntos",
    "{x} or less": "{x} o menos",
    "{x} or more": "{x} o más",
    "below {x}": "menos de {x}",
    "no annual rate yet": "aún sin tasa anual",
    "Price change on a year earlier:": "Variación interanual de los precios:",
    "Share of the basket:": "Peso en la cesta:",
    "Our own calculations from the official data.": "Cálculos propios a partir de los datos oficiales.",
    "How they are made": "Cómo se hacen",
    "Since the last update": "Desde la última actualización",
    "And %(n)s more.": "Y %(n)s más.",
    "Follow every change in a feed reader:": "Siga cada cambio en un lector de noticias:",
    "Notes on what each update changes start with the next data update after %(when)s.":
        "Las notas sobre lo que cambia en cada actualización empiezan con la primera actualización de datos posterior al %(when)s.",
    "Notes on what each update changes start with the next data update.":
        "Las notas sobre lo que cambia en cada actualización empiezan con la próxima actualización de datos.",
    # The home page's charts
    "Harmonised index (HICP), % change on a year earlier": "Índice armonizado (IPCA), variación interanual en %",
    "HICP": "IPCA",
    "Core HICP": "IPCA subyacente",
    "2% target": "Objetivo del 2%",
    "10-year government bond yields": "Rentabilidad de la deuda pública a 10 años",
    "%, daily; the gap between the lines is the prima de riesgo": "%, diaria; la distancia entre las líneas es la prima de riesgo",
    "Germany": "Alemania",
    "Monthly change, thousands, seasonally adjusted by Macroscope": "Variación mensual, miles, desestacionalizada por Macroscope",
    "Monthly change": "Variación mensual",
})

# The four questions (econpulse/questions.py)
add({
    "Is inflation coming back to 2%?": "¿Vuelve la inflación al 2%?",
    "HICP inflation, past 12 months": "Inflación del IPCA, últimos 12 meses",
    "Core CPI, past 12 months": "IPC subyacente, últimos 12 meses",
    " (flash)": " (avance)",
    "Core CPI, recent pace (3-month annualised, SA)": "IPC subyacente, ritmo reciente (3 meses anualizado, desest.)",
    "The ECB targets 2% inflation on the harmonised index (HICP) for the euro area as a whole. Core inflation leaves out energy and unprocessed food to show the underlying trend; the 3-month pace shows where it is heading.":
        "El BCE persigue una inflación del 2% en el índice armonizado (IPCA) del conjunto de la zona del euro. La inflación subyacente excluye la energía y los alimentos no elaborados para mostrar la tendencia de fondo; el ritmo a tres meses indica hacia dónde se dirige.",
    "Is the labour market cooling?": "¿Se enfría el mercado laboral?",
    "Social Security registrations, last month (SA)": "Afiliación a la Seguridad Social, último mes (desest.)",
    "3-month average (SA)": "Media de 3 meses (desest.)",
    " per month": " al mes",
    "Unemployment rate (monthly, SA)": "Tasa de paro (mensual, desest.)",
    "vs {value} a year ago": "frente al {value} hace un año",
    "Social Security registrations (afiliados) are Spain's closest equivalent to payrolls: the average number of people paying in each month. Seasonally adjusted by Macroscope, so they show the trend rather than the summer and Christmas swings.":
        "La afiliación a la Seguridad Social es lo más parecido en España a las nóminas (payrolls) de Estados Unidos: el número medio de personas que cotizan cada mes. Macroscope la desestacionaliza, de modo que muestra la tendencia y no las oscilaciones del verano y la Navidad.",
    "Is growth holding up?": "¿Aguanta el crecimiento?",
    "Domestic demand, last quarter": "Demanda interna, último trimestre",
    "Domestic demand, past four quarters": "Demanda interna, últimos cuatro trimestres",
    "Real GDP, last quarter": "PIB real, último trimestre",
    "Domestic demand, spending by Spanish households, firms and government, is the cleanest read on the economy's own momentum, before exports and imports. Growth rates are not annualised, following Spanish convention.":
        "La demanda interna, el gasto de los hogares, las empresas y las administraciones españolas, es la lectura más limpia del impulso propio de la economía, antes de exportaciones e importaciones. Las tasas de crecimiento no se anualizan, según la práctica española.",
    "Spain 10-year yield since {date}": "Bono español a 10 años desde el {date}",
    "Spain 10-year yield this year": "Bono español a 10 años en lo que va de año",
    "German Bund (euro-area rates)": "Bund alemán (tipos de la zona del euro)",
    "Prima de riesgo (Spain-specific)": "Prima de riesgo (propia de España)",
    "to {date}": "hasta el {date}",
    "Why are Spain's borrowing costs moving?": "¿Por qué se mueve el coste de financiación de España?",
    "Spain's 10-year yield is the German Bund yield, which moves with euro-area interest rates and inflation expectations, plus the prima de riesgo, the extra return investors demand to hold Spanish debt. Which part moved says whether the change is about the euro area or about Spain. Here the prima de riesgo is the Spanish yield minus the Bund, so the parts add up; Banco de España's headline spread (the tile above) uses benchmark bonds and can differ by a few bp.":
        "La rentabilidad del bono español a 10 años es la del Bund alemán, que se mueve con los tipos de interés y las expectativas de inflación de la zona del euro, más la prima de riesgo, la rentabilidad adicional que exigen los inversores por tener deuda española. Qué parte se ha movido indica si el cambio tiene que ver con la zona del euro o con España. Aquí la prima de riesgo es la rentabilidad española menos la del Bund, de modo que las partes suman; el diferencial de referencia del Banco de España (el recuadro de arriba) usa bonos de referencia y puede diferir en unos pocos puntos básicos.",
})

# Macroscope readings (econpulse/analytics.py, econpulse/surprises.py)
add({
    "; {value} three months earlier": "; {value} tres meses antes",
    "Activity vs history": "Actividad frente a su historia",
    "Inflation vs history": "Inflación frente a su historia",
    "hotter than normal": "más alta de lo normal",
    "cooler than normal": "más baja de lo normal",
    "stronger than normal": "más fuerte de lo normal",
    "weaker than normal": "más débil de lo normal",
    "close to normal": "cerca de lo normal",
    "± {error} pp typical error": "± {error} pp de error típico",
    "GDP nowcast (placeholder), {q}": "Estimación adelantada del PIB (provisional), {q}",
    "Latest official, {q}": "Último dato oficial, {q}",
    "Data in hand for {q}": "Datos disponibles para {q}",
    "{n} of {total}": "{n} de {total}",
    "monthly readings; the rest is projected": "datos mensuales; el resto se proyecta",
    "ECB rate vs Taylor rule": "Tipo del BCE frente a la regla de Taylor",
    "deposit rate minus the euro-area rule": "tipo de depósito menos la regla de la zona del euro",
    "Activity data vs forecasts": "Datos de actividad frente a previsiones",
    "Inflation data vs forecasts": "Datos de inflación frente a previsiones",
    "{verdict}, {month}; {above} of {total} recent figures above": "{verdict}, {month}; {above} de {total} datos recientes por encima",
    "above expectations": "por encima de lo esperado",
    "below expectations": "por debajo de lo esperado",
    "in line with expectations": "en línea con lo esperado",
})

# What changed (econpulse/changes.py): the log is written in English and rebuilt here
add({
    "{label}: {now} in {period}{flash}, after {before} in {bperiod}.": "{label}: {now} en {period}{flash}, tras {before} en {bperiod}.",
    "{label} for {period} revised to {now}, from {before}.": "{label}, {period}: revisado a {now}, desde {before}.",
    "{label}: {move} since the last update, to {now}.": "{label}: {move} desde la última actualización, hasta {now}.",
    " (flash estimate)": " (avance)",
    "; and {n} more": "; y {n} más",
})

# The tiles' notes, shown when the pointer rests on a tile
add({
    "Monthly average, total system. The monthly change is seasonally adjusted by Macroscope; the y/y change is as published.":
        "Media mensual, total del sistema. La variación mensual la desestacionaliza Macroscope; la interanual es la publicada.",
    "Labour force survey, not seasonally adjusted. The official measure.":
        "Encuesta de Población Activa, sin desestacionalizar. La medida oficial.",
    'Overnight visitors only (FRONTUR "turistas"); same-day visitors are left out.':
        "Solo visitantes que pernoctan (los «turistas» de FRONTUR); se excluyen los excursionistas.",
    "Excludes unprocessed food and energy (INE definition).": "Excluye los alimentos no elaborados y la energía (definición del INE).",
    "Harmonised index, the measure the ECB targets.": "Índice armonizado, la medida que persigue el BCE.",
    "The reference rate for most Spanish variable-rate mortgages.": "El índice de referencia de la mayoría de las hipotecas a tipo variable en España.",
    "Secondary-market yield, all trades in non-stripped bonds with about 10 years to maturity.":
        "Rentabilidad en el mercado secundario, todas las operaciones con bonos no segregados con unos 10 años de vida residual.",
    "Banco de España's 10-year spread over the German Bund.": "Diferencial a 10 años frente al Bund alemán, del Banco de España.",
    "US dollars per euro, ECB reference rate.": "Dólares estadounidenses por euro, tipo de cambio de referencia del BCE.",
    "Europe Brent spot price (US Energy Information Administration); published with a few days' lag.":
        "Precio al contado del Brent europeo (Administración de Información Energética de EE. UU.); se publica con unos días de retraso.",
    "Daily average of the Iberian day-ahead market price for Spain.": "Media diaria del precio del mercado diario ibérico para España.",
    "Average pump price in Spain, taxes included, on Mondays (European Commission, Weekly Oil Bulletin).":
        "Precio medio en surtidor en España, impuestos incluidos, los lunes (Comisión Europea, Boletín Petrolero semanal).",
    "Average pump price of automotive diesel in Spain, taxes included, on Mondays (European Commission, Weekly Oil Bulletin).":
        "Precio medio en surtidor del gasóleo de automoción en España, impuestos incluidos, los lunes (Comisión Europea, Boletín Petrolero semanal).",
})

# ---------------------------------------------------------------- the calendar
add({
    "When the figures on this site are published. Times are Madrid time.": "Cuándo se publican las cifras de este sitio. Las horas son de Madrid.",
    "INE dates come from": "Las fechas del INE proceden del",
    "INE's own calendar": "calendario del propio INE",
    "refreshed at every update. Social Security registrations are expected on the second working day of each month; ECB decisions follow the ECB's published schedule.":
        "que se renueva en cada actualización. La afiliación a la Seguridad Social se espera el segundo día hábil de cada mes; las decisiones del BCE siguen el calendario que publica el BCE.",
    "The next three months, day by day: the darker the day, the more releases it has, and the number in its corner says how many. Click a day to see them.":
        "Los próximos tres meses, día a día: cuanto más oscuro el día, más publicaciones tiene, y el número de su esquina dice cuántas. Pulse en un día para verlas.",
    "Releases in a day": "Publicaciones en un día",
    "today": "hoy",
    "Mo": "Lu", "Tu": "Ma", "We": "Mi", "Th": "Ju", "Fr": "Vi", "Sa": "Sá", "Su": "Do",
    "%(num)s release": "%(num)s publicación",
    "%(num)s releases": "%(num)s publicaciones",
    "expected": "prevista",
    "Nothing scheduled in the next three months.": "No hay nada previsto en los próximos tres meses.",
    "INE puts out each year's calendar towards the end of the year before; until then the months ahead show only the Social Security's and the ECB's dates.":
        "El INE publica el calendario de cada año hacia el final del anterior; hasta entonces, los meses siguientes solo muestran las fechas de la Seguridad Social y del BCE.",
    "Time": "Hora",
    "Release": "Publicación",
    "No releases found for the coming weeks. The calendar fills in at the next data update.":
        "No hay publicaciones previstas para las próximas semanas. El calendario se completa en la próxima actualización de datos.",
    # What the site calls each release
    "CPI and HICP, full data": "IPC e IPCA, datos completos",
    "CPI flash estimate": "Avance del IPC",
    "ECB monetary policy decision": "Decisión de política monetaria del BCE",
    "GDP, first estimate": "PIB, avance",
    "GDP, full quarterly accounts": "PIB, contabilidad trimestral completa",
    "Home sales": "Compraventa de viviendas",
    "Industrial production": "Producción industrial",
    "Labour costs (ETCL)": "Costes laborales (ETCL)",
    "Mortgages": "Hipotecas",
    "Producer prices": "Precios industriales",
    "Regional GDP": "PIB regional",
    "Registrations and registered unemployment": "Afiliación y paro registrado",
    "Retail sales": "Comercio minorista",
    "Tourist arrivals (FRONTUR)": "Llegada de turistas (FRONTUR)",
    "Tourist spending (EGATUR)": "Gasto turístico (EGATUR)",
})

# ---------------------------------------------------------------- the data page
add({
    "Every series on the site, where it comes from, and whether it is up to date.": "Todas las series del sitio, de dónde proceden y si están al día.",
    "%(n)s of %(total)s series need attention:": "%(n)s de %(total)s series requieren atención:",
    "All %(total)s series were fetched successfully and are up to date.": "Las %(total)s series se han descargado correctamente y están al día.",
    "Next releases are on the": "Las próximas publicaciones están en el",
    "calendar": "calendario",
    "By source": "Por fuente",
    "IMF-style sector tables": "Tablas sectoriales al estilo del FMI",
    "Indicators": "Indicadores",
    "Up to date": "Al día",
    "Need attention": "Requieren atención",
    "Last fetched": "Última descarga",
    "“Need attention” counts series whose last update failed or that have stopped updating at the source: each series is allowed a delay that suits how often it is published (10 days for daily data, about 4 months for monthly, 8–9 months for quarterly).":
        "«Requieren atención» cuenta las series cuya última actualización falló o que han dejado de actualizarse en la fuente: cada serie tiene un plazo acorde con la frecuencia con que se publica (10 días para los datos diarios, unos 4 meses para los mensuales y de 8 a 9 meses para los trimestrales).",
    "Run": "Ejecute",
    "for details.": "para ver los detalles.",
    "The tables of the IMF's 2026 Article IV report for Spain, rebuilt from public data, with history from 2015:":
        "Las tablas del informe del Artículo IV del FMI sobre España de 2026, reconstruidas con datos públicos, con historia desde 2015:",
    "download the Excel workbook": "descargue el libro de Excel (en inglés)",
    "All of them are on the": "Todas están en la página de",
    "page, in euros or as a percent of GDP, with charts; each is also on its section page:":
        "(en euros o en porcentaje del PIB, con gráficos); cada una está también en la página de su sección:",
})

# Who publishes the data
add({
    "BIS": "BPI",
    "European Commission (Weekly Oil Bulletin)": "Comisión Europea (Boletín Petrolero semanal)",
    "European Commission (via DBnomics)": "Comisión Europea (vía DBnomics)",
    "Eurostat (Macroscope calculation)": "Eurostat (cálculo de Macroscope)",
    "IMF": "FMI",
    "Macroscope calculation": "cálculo de Macroscope",
    "OECD": "OCDE",
    "US BEA (via DBnomics)": "BEA de EE. UU. (vía DBnomics)",
    "US BLS": "BLS de EE. UU.",
    "US EIA": "EIA de EE. UU.",
    "World Bank": "Banco Mundial",
})
for name in ("Banco de España", "Bundesbank", "DBnomics", "Eurostat", "Eurostat (Comext)", "FRED", "FUNCAS", "INE",
             "Ministerio de Trabajo", "Red Eléctrica", "Seguridad Social", "Seguridad Social, SEPE"):
    add({name: name})

# Units written after a figure (econpulse/snapshot.py); symbols stay as they are
add({
    "% of GDP": "% del PIB",
    "bp": "pb",
    "mn": "mill.",
    "bn": "mm",
    "homes": "viviendas",
    "hours": "horas",
    "mn hours": "mill. de horas",
    "mortgages": "hipotecas",
    "persons": "personas",
    "vehicles": "vehículos",
    "years": "años",
    "€ thousand": "miles de €",
})
for unit in ("$", "$/MMBtu", "$/oz", "$/t", "GWh", "pp", "€/MWh", "€/bbl", "€/l", "€/m²"):
    add({unit: unit})

# The section pages, one file per batch (scripts/ is on the path when this runs as a script)
from catalogue_sections_1 import PAIRS as SECTIONS_1   # noqa: E402  Batch 33b
from catalogue_sections_2 import PAIRS as SECTIONS_2   # noqa: E402  Batch 33c
from catalogue_analysis import PAIRS as ANALYSIS       # noqa: E402  Batch 33c
from catalogue_trade import PAIRS as TRADE             # noqa: E402  Batch 33c
from catalogue_housing import PAIRS as HOUSING         # noqa: E402  Batch 33c
from catalogue_pensions import PAIRS as PENSIONS       # noqa: E402  Batch 33c
from catalogue_international import PAIRS as INTERNATIONAL   # noqa: E402  Batch 33c
from catalogue_imf_a import PAIRS as IMF_A             # noqa: E402  Batch 33c-3
from catalogue_imf_b import PAIRS as IMF_B             # noqa: E402  Batch 33c-3
from catalogue_debt import PAIRS as DEBT               # noqa: E402  Batch 34b
from catalogue_equities import PAIRS as EQUITIES       # noqa: E402  Batch 34c
from catalogue_gdp import PAIRS as GDP                 # noqa: E402  Batch 34d
from catalogue_site import PAIRS as SITE               # noqa: E402  Batch 33d
from catalogue_tools import PAIRS as TOOLS             # noqa: E402  Batch 33d
from catalogue_speak import PAIRS as SPEAK             # noqa: E402  Batch 33d
from catalogue_budget import PAIRS as BUDGET           # noqa: E402  Batch 33d
from catalogue_money import PAIRS as MONEY             # noqa: E402  Batch 35
from catalogue_money_links import PAIRS as MONEY_LINKS # noqa: E402  Batch 35b
from catalogue_recession import PAIRS as RECESSION     # noqa: E402  Batch 36
from catalogue_disclaimer import PAIRS as DISCLAIMER   # noqa: E402  disclaimer
from catalogue_landing import PAIRS as LANDING         # noqa: E402  batches L1-L5

for part in (SECTIONS_1, SECTIONS_2, ANALYSIS, TRADE, HOUSING, PENSIONS, INTERNATIONAL, IMF_A, IMF_B, DEBT, EQUITIES, GDP,
             SITE, TOOLS, SPEAK, BUDGET, MONEY, MONEY_LINKS, RECESSION, DISCLAIMER, LANDING):
    add(part)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "econpulse" / "locale" / "es.yaml"
    header = ("# Spanish for the site: English text (as written in the code and templates) -> Spanish.\n"
              "# Written by scripts/write_catalogue.py; edit the translations there, not here.\n")
    out.write_text(header + yaml.safe_dump(ES, allow_unicode=True, sort_keys=True, width=4096), encoding="utf-8",
                   newline="\n")
    print(f"{len(ES)} entries -> {out}")
