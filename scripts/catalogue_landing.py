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
