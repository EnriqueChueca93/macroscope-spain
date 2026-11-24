"""Spanish for the home page's opening and tour (batches L1 to L5): econpulse/hero.py and templates/index.html.
Read by scripts/write_catalogue.py; the keys are the English exactly as the code writes it.
"""

PAIRS: dict[str, str] = {}

# ---------------------------------------------------------------- L1: the headline, the big numbers and the line
PAIRS.update({
    # the headline: the economy, a joiner and prices (hero.ECONOMY, hero.PRICES)
    "{economy}, {joiner} {prices}.": "{economy}, {joiner} {prices}.",
    "while": "mientras que",
    "Spain's economy is running well above its normal pace": "La economía española avanza muy por encima de su ritmo normal",
    "Spain's economy is running above its normal pace": "La economía española avanza por encima de su ritmo normal",
    "Spain's economy is running close to its normal pace": "La economía española avanza cerca de su ritmo normal",
    "Spain's economy is running below its normal pace": "La economía española avanza por debajo de su ritmo normal",
    "Spain's economy is running well below its normal pace": "La economía española avanza muy por debajo de su ritmo normal",
    "prices are rising much faster than normal": "los precios suben mucho más deprisa de lo normal",
    "prices are rising faster than normal": "los precios suben más deprisa de lo normal",
    "inflation is close to normal": "la inflación está cerca de lo normal",
    "inflation is running below normal": "la inflación está por debajo de lo normal",
    "inflation is running well below normal": "la inflación está muy por debajo de lo normal",
    "Macroscope's scores for {month}: activity {activity}, inflation {inflation}, where zero is normal for 2013 to today (Covid years left out).":
        "Puntuaciones de Macroscope en {month}: actividad {activity}, inflación {inflation}, donde cero es lo normal "
        "entre 2013 y hoy (sin los años de la covid).",
    "How the scores work": "Cómo se calculan las puntuaciones",
    # the big numbers
    "{period}, on a year earlier": "{period}, interanual",
    "{change} on the quarter": "{change} en el trimestre",
    "{change} on a year": "{change} en un año",
    "{value} a year earlier": "{value} un año antes",
    "million": "millones",
    "Inflation (CPI)": "Inflación (IPC)",
    # the line
    "Macroscope's scores, monthly since {start}; the band is the normal range":
        "Puntuaciones de Macroscope, mensuales desde {start}; la franja es el rango normal",
    "Line chart of Macroscope's activity and inflation scores, monthly from {start} to {end}. In {end}: activity {activity}, inflation {inflation}.":
        "Gráfico de líneas de las puntuaciones de actividad e inflación de Macroscope, mensuales de {start} a {end}. "
        "En {end}: actividad {activity}, inflación {inflation}.",
    "Normal range": "Rango normal",
    "Covid years": "Años de la covid",
    "The full chart and the readings behind it": "El gráfico completo y los datos que hay detrás",
})

# ---------------------------------------------------------------- found missing on the way
PAIRS.update({
    "Spirits and liquors": "Bebidas espirituosas y licores",     # a basket item, where a chart's legend names it
})

# ---------------------------------------------------------------- L2: the cycle clock
PAIRS.update({
    "The cycle clock": "El reloj del ciclo",
    "Expansion": "Expansión",
    "Slowdown": "Desaceleración",
    "Downturn": "Contracción",
    "Recovery": "Recuperación",
    "above normal and rising": "por encima de lo normal y subiendo",
    "above normal but falling": "por encima de lo normal pero bajando",
    "below normal and falling": "por debajo de lo normal y bajando",
    "below normal but rising": "por debajo de lo normal pero subiendo",
    "{month}: {phase}. Activity is {words}: its three-month average is {level}, {change} over six months.":
        "{month}: {phase}. La actividad está {words}: su media de tres meses es {level} y {change} en seis meses.",
    "up {n}": "ha subido {n}",
    "down {n}": "ha bajado {n}",
    "{when} ({month}): {phase}": "{when} ({month}): {phase}",
    "Six months earlier": "Seis meses antes",
    "Above normal": "Por encima de lo normal",
    "Below normal": "Por debajo de lo normal",
    "Rising": "Subiendo",
    "Falling": "Bajando",
    "Three-month average": "Media de tres meses",
    "Over six months": "En seis meses",
    "The activity score's three-month average across, and its change over six months up, for the past 24 months; a fixed scale (±{limit}), so the clock doesn't rescale from month to month, and a month beyond it sits on the edge, hollow.":
        "La media de tres meses de la puntuación de actividad en horizontal y su variación en seis meses en vertical, "
        "en los últimos 24 meses; con una escala fija (±{limit}), para que el reloj no cambie de escala de un mes a "
        "otro, y un mes que se sale de ella queda en el borde, hueco.",
    "Cycle clock: the past 24 months of Macroscope's activity score, from {start} to {end}, ending in {phase}.":
        "Reloj del ciclo: los últimos 24 meses de la puntuación de actividad de Macroscope, de {start} a {end}, que "
        "terminan en {phase}.",
})

# ---------------------------------------------------------------- L3: the map of Spain
PAIRS.update({
    "The regions": "Las regiones",
    "Income per head": "Renta por habitante",
    "house prices, % change on a year earlier": "precios de la vivienda, variación interanual en %",
    "CPI inflation, % on a year earlier": "inflación del IPC, interanual en %",
    "Spain: {value} ({period})": "España: {value} ({period})",
    "Below Spain": "Por debajo de España",
    "Above Spain": "Por encima de España",
    "{n} points above Spain": "{n} puntos por encima de España",
    "{n} points below Spain": "{n} puntos por debajo de España",
    "the same as Spain": "igual que España",
    "{name}, {period}: {value}, {gap}": "{name}, {period}: {value}, {gap}",
    "{name}: no figure yet": "{name}: aún sin dato",
    "Hover over or tap a community; click it for the Regions page.":
        "Pase el ratón o toque una comunidad; haga clic para ir a la página de Regiones.",
    "All the regions": "Todas las regiones",
    "Tile map of Spain's 17 autonomous communities": "Mapa en cuadrados de las 17 comunidades autónomas",
})

# ---------------------------------------------------------------- L4: the tour, first seven chapters
PAIRS.update({
    "Inside Macroscope": "Recorrido por Macroscope",
    "A taste of each part of the site: the figure that matters most there today, and the chart that tells its story.":
        "Un anticipo de cada parte del sitio: la cifra que más importa hoy en ella y el gráfico que cuenta su historia.",
    "Explore {area}": "Explorar {area}",
    # GDP
    "GDP growth, {period}, on a year earlier": "Crecimiento del PIB, {period}, interanual",
    "Domestic demand added {domestic} points to growth in {period} and the rest of the world {external}.":
        "La demanda nacional aportó {domestic} puntos al crecimiento en {period} y el resto del mundo, {external}.",
    "{value} on the quarter": "{value} en el trimestre",
    "{change} since the end of 2019, before Covid": "{change} desde finales de 2019, antes de la covid",
    "Rest of the world": "Resto del mundo",
    "Contributions to real GDP growth on a year earlier, percentage points":
        "Aportaciones al crecimiento interanual del PIB real, puntos porcentuales",
    # Labour market
    "Social Security registrations, {month}": "Afiliación a la Seguridad Social, {month}",
    "Social Security registrations reached a record in {month}, {change} on a year earlier.":
        "La afiliación a la Seguridad Social marcó un récord en {month}, {change} en un año.",
    "Social Security registrations in {month}, {change} on a year earlier.":
        "Afiliación a la Seguridad Social en {month}, {change} en un año.",
    "Unemployment rate {value} ({period}, EPA)": "Tasa de paro {value} ({period}, EPA)",
    "{value} million people in work ({period}, EPA)": "{value} millones de ocupados ({period}, EPA)",
    "Monthly average, millions, since 2008": "Media mensual, millones, desde 2008",
    # Wages
    "Wage cost per worker, {period}, on a year earlier": "Coste salarial por trabajador, {period}, interanual",
    "Wage cost per worker rose {pay} on a year earlier in {period}, against consumer prices up {prices}.":
        "El coste salarial por trabajador subió un {pay} interanual en {period}, frente a una subida de los precios de "
        "consumo del {prices}.",
    "Real wage cost per worker {change} on a year earlier ({period})":
        "Coste salarial real por trabajador {change} interanual ({period})",
    "Pay rises agreed in collective agreements: {value} ({month})":
        "Subida salarial pactada en convenios: {value} ({month})",
    "Pay against prices": "Salarios frente a precios",
    "% change on a year earlier, quarterly, since 2022": "Variación interanual en %, trimestral, desde 2022",
    # Inflation
    "CPI inflation, {period}": "Inflación del IPC, {period}",
    "{first} adds the most to inflation, {a} points, then {second}, {b}.":
        "{first} es lo que más aporta a la inflación, {a} puntos, seguido de {second}, {b}.",
    "Core inflation {value}": "Inflación subyacente {value}",
    "Harmonised index (HICP) {value}": "Índice armonizado (IPCA) {value}",
    "The basket": "La cesta",
    "Each category sized by its weight in the {year} basket and shaded by its prices' change on a year earlier, {month}, around the ECB's 2% target":
        "Cada categoría, del tamaño de su peso en la cesta de {year} y coloreada según la variación interanual de sus "
        "precios en {month}, en torno al objetivo del 2% del BCE",
    "{name}: {share} of the basket, prices {rate} on a year earlier, adding {points} points":
        "{name}: {share} de la cesta, precios {rate} interanual, aporta {points} puntos",
    "Below 2%": "Por debajo del 2%",
    "Above 2%": "Por encima del 2%",
    # Financial
    "Spain's 10-year bond yield, {day}": "Rentabilidad del bono español a 10 años, {day}",
    "{bp} basis points above Germany's: the prima de riesgo.": "{bp} puntos básicos por encima del alemán: la prima de riesgo.",
    "12-month Euribor {value} ({period})": "Euríbor a 12 meses {value} ({period})",
    "IBEX 35 {value} ({period}), {change} this year": "IBEX 35 {value} ({period}), {change} en el año",
    "Ten-year government bond yields": "Rentabilidad de la deuda pública a 10 años",
    "Monthly average, %, since 2019; the gap between them is the prima de riesgo":
        "Media mensual, %, desde 2019; la diferencia entre ambas es la prima de riesgo",
    "Banco de España; Bundesbank": "Banco de España; Bundesbank",
    # ECB
    "Raised by {n} points on {day}.": "Subido {n} puntos el {day}.",
    "Cut by {n} points on {day}.": "Rebajado {n} puntos el {day}.",
    "Euro-area inflation {value} ({month})": "Inflación de la zona euro {value} ({month})",
    "Spain's harmonised inflation {value} ({period})": "Inflación armonizada de España {value} ({period})",
    "Euro-area inflation": "Inflación de la zona euro",
    "The ECB's rate and euro-area inflation": "El tipo del BCE y la inflación de la zona euro",
    "%, monthly, since 2019": "%, mensual, desde 2019",
    "ECB; Eurostat": "BCE; Eurostat",
    # Fiscal
    "Government debt, {period}": "Deuda pública, {period}",
    "of GDP": "del PIB",
    "The European Commission's baseline has it at {value} in {year} without new measures.":
        "El escenario base de la Comisión Europea la sitúa en el {value} en {year} sin nuevas medidas.",
    "Deficit {value} of GDP in {year}": "Déficit del {value} del PIB en {year}",
    "Interest on the debt {value} of GDP in {year}": "Intereses de la deuda: {value} del PIB en {year}",
    "Commission's projection": "Proyección de la Comisión",
    "% of GDP at year end since 2000, and the Commission's projection":
        "% del PIB a final de año desde 2000, y la proyección de la Comisión",
    "Eurostat; European Commission": "Eurostat; Comisión Europea",
})

# ---------------------------------------------------------------- L5: the tour, last seven chapters
PAIRS.update({
    # Economic activity and trade
    "International tourists in the twelve months to {month}": "Turistas internacionales en los doce meses hasta {month}",
    "A record for any twelve months{vs}.": "Un récord para cualquier periodo de doce meses{vs}.",
    "International tourists in the twelve months to {month}{vs}.": "Turistas internacionales en los doce meses hasta {month}{vs}.",
    ", {change} on 2019, before Covid": ", {change} sobre 2019, antes de la covid",
    "Industrial production {value} on a year earlier ({period})": "Producción industrial {value} interanual ({period})",
    "Retail sales {value} on a year earlier ({period})": "Ventas minoristas {value} interanual ({period})",
    "Arrivals in the past twelve months, millions, since 2015": "Llegadas en los últimos doce meses, millones, desde 2015",
    # Housing
    "House prices, {period}, on a year earlier": "Precios de la vivienda, {period}, interanual",
    "House prices are up {n}% since 2015, more than pay.": "Los precios de la vivienda han subido un {n}% desde 2015, más que los salarios.",
    "A home costs {n} years of household income ({period})": "Una vivienda cuesta {n} años de renta del hogar ({period})",
    "Gross rental yield {value} ({period})": "Rentabilidad bruta del alquiler {value} ({period})",
    "Prices against pay": "Precios frente a salarios",
    "Index, 2015 = 100, quarterly": "Índice, 2015 = 100, trimestral",
    # Pensions
    "{n} workers pay in for each pension.": "{n} afiliados cotizan por cada pensión.",
    "Social Security registrations per contributory pension": "Afiliados a la Seguridad Social por pensión contributiva",
    # International
    "Spain's real GDP since the end of 2019": "PIB real de España desde finales de 2019",
    "Spain is {place} of the {n} economies here since the end of 2019.":
        "España es {place} de las {n} economías de la lista desde finales de 2019.",
    "the fastest-growing": "la que más ha crecido",
    "the second fastest-growing": "la segunda que más ha crecido",
    "the third fastest-growing": "la tercera que más ha crecido",
    "the {k}th fastest-growing": "la {k}.ª que más ha crecido",
    "Euro area {value}": "Zona del euro {value}",
    "Real GDP, % change from the last quarter of 2019 to the latest": "PIB real, variación en % del último trimestre de 2019 al más reciente",
    "Eurostat; OECD": "Eurostat; OCDE",
    # Regions
    "points": "puntos",
    "Between the highest and lowest unemployment rates": "Entre la tasa de paro más alta y la más baja",
    "Unemployment runs from {low} in {low_name} to {high} in {high_name}.":
        "El paro va del {low} de {low_name} al {high} de {high_name}.",
    "Income per head from {poor} in {poor_name} to {rich} in {rich_name} (Spain = 100)":
        "Renta por habitante de {poor} en {poor_name} a {rich} en {rich_name} (España = 100)",
    "{name}: income per head {x} (Spain = 100), unemployment {y}": "{name}: renta por habitante {x} (España = 100), paro {y}",
    "Richer regions, fewer jobless": "Regiones más ricas, menos paro",
    "Each community: GDP per head across, unemployment up": "Cada comunidad: PIB per cápita en horizontal, paro en vertical",
    "Income per head, Spain = 100": "Renta por habitante, España = 100",
    "Unemployment, %": "Paro, %",
    # Analysis
    "Macroscope's provisional nowcast of GDP growth, {quarter}, on the quarter":
        "Estimación adelantada provisional de Macroscope del crecimiento del PIB, {quarter}, intertrimestral",
    "A provisional estimate from Social Security registrations and industrial production (the model is still being worked on); typical error ±{e} points.":
        "Una estimación provisional a partir de la afiliación a la Seguridad Social y la producción industrial (el "
        "modelo aún se está afinando); error típico ±{e} puntos.",
    "Macroscope's provisional nowcast": "Estimación provisional de Macroscope",
    "GDP growth and the nowcast": "Crecimiento del PIB y la estimación adelantada",
    "Real GDP, % change on the quarter, and Macroscope's estimate for the quarter under way":
        "PIB real, variación intertrimestral en %, y la estimación de Macroscope para el trimestre en curso",
    # Tools
    "series": "series",
    "from {n} publishers, updated twice a day": "de {n} fuentes, actualizadas dos veces al día",
    "Explorers and calculators to try your own numbers, and every series behind the site to download.":
        "Exploradores y calculadoras para probar sus propias cifras, y todas las series del sitio para descargar.",
    "Tools and data": "Herramientas y datos",
    "Spain's debt to 2070, with levers to pull": "La deuda de España hasta 2070, con palancas para mover",
    "Every administration's spending and revenue since 1995": "El gasto y los ingresos de cada administración desde 1995",
    "Where output would be on its old path": "Dónde estaría la producción en su senda anterior",
    "What rate the rule would set, with your own inputs": "Qué tipo fijaría la regla, con sus propios datos",
    "How hawkish or dovish the ECB's speakers sound": "Cuán duros o blandos suenan los discursos del BCE",
    "What comes out, and when": "Qué se publica y cuándo",
    "IMF-style tables for every sector, and a workbook": "Tablas al estilo del FMI para cada sector, y un libro de Excel",
    "Every series, with its source, to download": "Todas las series, con su fuente, para descargar",
})

# ---------------------------------------------------------------- the page's order (24 Nov 2026)
PAIRS.update({
    "The economy today": "La economía hoy",
})
