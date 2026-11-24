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
